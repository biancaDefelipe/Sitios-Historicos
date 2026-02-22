"""
Módulo que contiene funciones *helper* para gestionar el modo de mantenimiento
del portal público y del área de administración.

Estas funciones se usan típicamente como *before_request* en Flask para
interceptar solicitudes y aplicar restricciones o notificaciones según el
estado de mantenimiento.
"""

from flask import (
    session,
    flash,
    render_template,
    request,
    jsonify,
    current_app,
)
from core.flags import esta_activo, obtener_mensaje_mantenimiento
from functools import wraps


def mantenimiento_portal_required(fn):
    """
    Controla el modo de mantenimiento para el portal público (API y Front-end público).

    Si el modo de mantenimiento del portal público está activo:
    1. Permite solicitudes `OPTIONS` (preflight CORS) sin restricción.
    2. Para cualquier otro método, devuelve un error JSON con código **403 Forbidden**.

    Returns:
        tuple[Response, int] or None: Una tupla (JSON de error, 403) si el modo
                                      está activo, o `None` para continuar la solicitud.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        """Aplica la validación de modo mantenimiento al portal público."""
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)

        try:
            activo = esta_activo("modo_mantenimiento_portal_publico")
        except Exception as e:
            current_app.logger.error(
                "Error consultando modo_mantenimiento_portal_publico",
                exc_info=e,
            )
            activo = False

        if activo:
            mensaje = obtener_mensaje_mantenimiento("modo_mantenimiento_portal_publico")

            response = jsonify({"error": {"code": "forbidden", "message": mensaje}})
            response.status_code = 403
            response.headers["X-Maintenance-Mode"] = "true"

            return response

        return fn(*args, **kwargs)

    return wrapper


def mantenimiento_admin():
    """
    Controla el modo de mantenimiento para el área de **administración**.

    **Lógica de Acceso:**
    * **Rutas siempre permitidas:** 'auth.login', 'auth.autenticar', 'static'.
    * **Si el modo mantenimiento ('modo_mantenimiento_admin') está activo:**
        * Si el usuario **NO** es admin (`session.get("es_admin")` es Falso), se:
            * Muestra un mensaje `flash`.
            * Limpia la sesión (`session.clear()`), forzando el *logout*.
            * Muestra la plantilla `mantenimiento.html`.
        * Si el usuario **ES** admin, se le permite el acceso, pero se muestra
            un mensaje *flash* de advertencia si el mensaje de mantenimiento ha cambiado.
    * **Si el modo mantenimiento está inactivo:**
        * Se limpia el mensaje de mantenimiento guardado en sesión (`ultimo_mensaje_mantenimiento`).

    Returns:
        Response or None: Una respuesta de renderizado (página de mantenimiento) si
                          el usuario no es admin y el modo está activo, o `None`
                          para continuar la ejecución de la solicitud.
    """
    try:
        rutas_permitidas = ["auth.login", "auth.autenticar", "static"]

        if request.endpoint in rutas_permitidas:
            return

        if esta_activo("modo_mantenimiento_admin"):

            if not session.get("es_admin"):
                mensaje = obtener_mensaje_mantenimiento("modo_mantenimiento_admin")
                flash(f"🚧 Mantenimiento: {mensaje}", "warning")
                session.clear()
                return render_template(
                    "mantenimiento.html", mensajes_mantenimiento=[mensaje]
                )
            else:

                mensaje = obtener_mensaje_mantenimiento("modo_mantenimiento_admin")
                if session.get("ultimo_mensaje_mantenimiento") != mensaje:
                    flash(f"⚠ Mantenimiento: {mensaje}", "warning")
                    session["ultimo_mensaje_mantenimiento"] = mensaje
        else:

            session.pop("ultimo_mensaje_mantenimiento", None)
    except Exception as e:
        current_app.logger.error(
            "Error en mantenimiento_admin para endpoint %s",
            request.endpoint,
            exc_info=e,
        )


def reviews_enabled_required(func):
    """
    Decorador que verifica si las reseñas están habilitadas mediante Feature Flags.

    Si las reviews no están habilitadas, devuelve una respuesta JSON de error con código 403.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Verifica si las reseñas están habilitadas mediante Feature Flags."""
        if not esta_activo("reviews_habilitadas"):
            response = jsonify(
                {
                    "error": {
                        "code": "forbidden",
                        "message": "La creación de reseñas está deshabilitada temporalmente.",
                    }
                }
            )
            response.status_code = 403
            response.headers["X-Reviews-Enabled"] = "false"
            return response

        return func(*args, **kwargs)

    return wrapper
