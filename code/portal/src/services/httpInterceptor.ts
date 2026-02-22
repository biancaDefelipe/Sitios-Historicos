import { AxiosError, type AxiosResponse } from "axios";
import axios from "axios";
import { useAuthStore } from "@/stores/authStore";
import { useToastStore } from "@/stores/toastStore";
import { useConfigStore } from "@/stores/configStore";
import router from "@/router"; 

const api = axios.create({
  baseURL: import.meta.env.VITE_API_LOCAL,
  withCredentials: false,
})


api.interceptors.response.use(

  (response) => response,
  (error) => {
    
    if (!error.response){
        return Promise.reject(error)
    }
    
    const auth = useAuthStore()
    const toast = useToastStore()
    const status = error.response.status // saca el codigo de estado HTTP que nos devolvio el servidor
    const config = error.config // saca la configuracion del request fallido
    const url = config?.url || "" // saca la url del request
    const method = config?.method?.toLowerCase() || "" // saca el metodo http y lo pone en minuscula

    switch (status) {
      case 400:
        toast.show("Ocurrió un error con los datos ingresados al intentar realizar la operación.")
        break;

      case 401:
        auth.clearSession()
        toast.show("Tu sesión expiró. Iniciá sesión nuevamente.")
        
        setTimeout(() => {
          window.location.reload();
        }, 1500);
        break;

      case 403:
        // La API define que se debe evitar lanzando un 403 Forbidden cuando un usuario intenta
        // acceder a recursos que no son suyos. Por ejemplo, intentar acceder o eliminar una
        // reseña que pertenece a otro usuario.
        // De esta forma, se controla si el 403 corresponde a mantanimiento o a lo mencionado anteriormente.
        const isMaintenanceMode = error.response?.headers["x-maintenance-mode"] === "true"
        const areReviewsDisabled = error.response?.headers["x-reviews-enabled"] === "false"

        if (isMaintenanceMode) {
          toast.show("El sitio se encuentra en mantenimiento. Volvé a intentarlo más tarde.")
          setTimeout(() => {
            window.location.reload()
          }, 1500)
        }
        else if (url.includes("/reviews") && areReviewsDisabled) {
          toast.show("Las reseñas están deshabilitadas temporalmente. Volvé a intentarlo más tarde.")
          break
        }
        else {
          toast.show("No tenés permisos para realizar esta acción.")
        }
        break

      case 404:
        if (url.includes('/reviews')) {
          switch (method) {
            case 'post':
              toast.show("Error. No se encontró el sitio al intentar publicar una reseña.")
              break
            case 'put':
              toast.show("Error. No se encontró el sitio al intentar editar una reseña.")
              break
            case 'delete':
              toast.show("Error. No se encontró el sitio al intentar eliminar una reseña.")
              break
          }
        }else if (url.includes('/favorites/')) {
          switch (method) {
            case 'put':
              toast.show("Error. No se encontró el sitio al intentar añadirlo a favoritos")
              break
            case 'delete':
              toast.show("Error. No se encontró el sitio al intentar eliminarlo de favoritos.")
              break
          }
        }else{
          router.push({
          name: 'not-found'
        })
        }
        break;

      case 500:        
        toast.show("Ocurrió un error inesperado en el servidor. Por favor, intentá nuevamente.")        
        break;
    }

    return Promise.reject(error)
  }
)

export default api

