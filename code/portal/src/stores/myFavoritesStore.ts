import { defineStore } from "pinia"
import { useAuthStore } from "./authStore"
import { usePaginationStore } from "./paginationStore"  



import api from "@/services/httpInterceptor"


export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    items: [] as any[],
    loading: false,
    error: null as string | null,


  }),

  actions: {
    async fetchFavorites() {
      const auth = useAuthStore()
      const paginationStore = usePaginationStore()
      const token = auth.token

      if (!token) {
        this.error = "No autenticado"
        return
      }

      this.loading = true
      this.error = null
      try{
          const response= await api.get("me/favorites", {
            params:{

              page:paginationStore.pagination.page,
              per_page:paginationStore.pagination.limit
            }, 
            headers:{
              Authorization:`Bearer ${token}`
            }
          })

          const json=response.data

          this.items = (json.data || []).map((raw: any) => ({
            ...raw,
            nombre: raw.name,
            ciudad: raw.city,
            provincia: raw.province,
            calificacion: raw.rank,
            imagen: raw.images?.find((img: any) => img.is_cover)?.public_url || null,
          }))
        
     
        paginationStore.setTotal (json.meta?.total ?? 0)

        }catch (err:any)  {
          this.error = err.message ?? "Error desconocido"
        }finally{
          this.loading = false
        }
      },
      
      changePage(p: number) {
        const paginationStore = usePaginationStore()
        paginationStore.setPage(p)
        this.fetchFavorites()
    }
  }
})
    