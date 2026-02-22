"""Utilidades para autenticación y autorización en la aplicación web.

Este módulo provee decoradores y funciones de ayuda para gestionar la autenticación
de usuarios, los permisos y el manejo de la sesión, utilizando tanto la sesión de Flask
como un sistema de caché para los permisos.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from core.auth import buscar_permisos
from web.utils.cache_utils import (
    guardar_en_cache,
    buscar_en_cache,
    invalidar_de_cache,
)
from web.utils.session_utils import (
    guardar_en_session,
    obtener_de_session,
    existe_en_session,
    eliminar_de_session,
)

from core.auth import obtener_eliminado_por_id

PREFIJO_PERMISOS = "permisos"
"""Prefijo utilizado en el sistema de caché para almacenar y recuperar los permisos de usuario."""

CLAVE_USUARIO_ID = "id"
CLAVE_USUARIO_EMAIL = "email"
CLAVE_USUARIO_ES_ADMIN = "es_admin"
CLAVE_USUARIO_ACTIVO = "activo"
"""Claves predefinidas utilizadas para almacenar y recuperar la información esencial del usuario en la sesión."""


def admin_requerido(f):
    """
    Decorador para requerir que el usuario sea **administrador**.

    Si el usuario actual no es administrador, la solicitud es abortada
    con código HTTP **401 Unauthorized**.

    Args:
        f (function): La función de vista (view function) a decorar.

    Returns:
        function: La función decorada que incluye la lógica de validación.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Función interna del decorador `admin_requerido`.

        Verifica si el usuario es administrador antes de permitir el acceso
        a la función decorada.
        """
        if not _es_admin():
            return abort(401, "Es necesario ser administrador.")
        return f(*args, **kwargs)

    return decorated_function


def login_requerido(f):
    """
    Decorador para requerir que el usuario esté **autenticado** (tenga sesión) y **activo**.

    La función verifica dos condiciones:
    1. Si no hay ID de usuario en sesión, aborta con código **401 Unauthorized**.
    2. Si el usuario está inactivo, fuerza el cierre de sesión (`session.clear()`),
       limpia los permisos de caché, muestra un mensaje flash y redirige al login.

    Args:
        f (function): La función de vista (view function) a decorar.

    Returns:
        function: La función decorada que incluye la lógica de validación de sesión y estado.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Función interna del decorador `login_requerido`.

        Verifica:
        - Que haya un usuario autenticado.
        - Que el usuario esté activo.
        Maneja el caso de usuario bloqueado y realiza limpieza de sesión y permisos.
        """
        usuario_dict = obtener_de_session([CLAVE_USUARIO_ID, CLAVE_USUARIO_ACTIVO])
        usuario_id = usuario_dict.get(CLAVE_USUARIO_ID)
        usuario_activo = usuario_dict.get(CLAVE_USUARIO_ACTIVO)

        if not usuario_id:
            return abort(401, "Es necesario iniciar sesión.")

        if not usuario_activo:

            eliminar_session_usuario(
                [
                    CLAVE_USUARIO_ID,
                    CLAVE_USUARIO_EMAIL,
                    CLAVE_USUARIO_ES_ADMIN,
                    CLAVE_USUARIO_ACTIVO,
                ]
            )

            limpiar_permisos_usuario(usuario_id)
            flash("Su cuenta ha sido bloqueada.", "error")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def permiso_requerido(permisos: list[str]):
    """
    Decorador para requerir que el usuario posea uno o más **permisos específicos**.

    **Lógica de Acceso:**
    * Si el usuario es administrador, siempre se le concede el acceso.
    * Si no es administrador, verifica si el usuario tiene todos los permisos listados.
    * Si el usuario no está autenticado, aborta con código **401 Unauthorized**.
    * Si el usuario está autenticado pero no tiene los permisos, aborta con **403 Forbidden**.

    :param permisos: Lista de descripciones de permisos requeridos (e.g., ['sitio_new', 'sitio_edit']).
    :type permisos: list[str]
    :return: Un decorador de función que envuelve la función de vista.
    :rtype: function
    """

    def decorator(f):
        """Envuelve una función de vista para validar permisos de acceso."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            Función interna del decorador `permiso_requerido`.

            - Controla si el usuario está autenticado.
            - Verifica si es administrador.
            - Si no lo es, comprueba si posee los permisos requeridos.
            """
            usuario_dict = obtener_de_session(
                [CLAVE_USUARIO_ID, CLAVE_USUARIO_ES_ADMIN]
            )
            usuario_id = usuario_dict.get(CLAVE_USUARIO_ID)
            usuario_es_admin = usuario_dict.get(CLAVE_USUARIO_ES_ADMIN)

            if usuario_id is None:
                return abort(401, "Es necesario iniciar sesión.")

            if not (usuario_es_admin or usuario_tiene_permisos(usuario_id, permisos)):
                return abort(
                    403,
                    "No posee los permisos necesarios para realizar esta acción.",
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def cargar_session_usuario(datos_usuario: dict):
    """
    Guarda en la sesión de Flask los datos esenciales del usuario tras el login.

    :param datos_usuario: Un diccionario con los datos del usuario (debe incluir claves como CLAVE_USUARIO_ID).
    :type datos_usuario: dict
    :rtype: None
    """
    guardar_en_session(datos_usuario)


def buscar_datos_session(claves: list[str]) -> dict:
    """
    Obtiene valores específicos del usuario almacenados en la sesión.

    :param claves: Lista de las claves de sesión a buscar.
    :type claves: list[str]
    :return: Un diccionario con las claves y sus valores encontrados.
    :rtype: dict
    """
    return obtener_de_session(claves)


def eliminar_session_usuario(datos_usuario: list[str]):
    """
    Limpia los datos del usuario especificados de la sesión de Flask.

    :param datos_usuario: Lista de claves de datos del usuario que se eliminarán de la sesión.
    :type datos_usuario: list[str]
    :rtype: None
    """
    eliminar_de_session(datos_usuario)


def cargar_permisos_usuario(id_usuario: int) -> list[str]:
    """
    Busca la lista completa de permisos de un usuario en el core, y los almacena en la **cache**.

    :param id_usuario: El ID del usuario para quien se buscan y guardan los permisos.
    :type id_usuario: int
    :return: La lista de permisos del usuario.
    :rtype: list[str]
    """
    permisos = buscar_permisos(id_usuario)
    guardar_en_cache(PREFIJO_PERMISOS, {id_usuario: permisos})
    return permisos


def usuario_tiene_permisos(id_usuario: int, permisos: list[str]) -> bool:
    """
    Verifica si el usuario posee todos los permisos especificados.

    Los permisos se buscan primero en la caché (`PREFIJO_PERMISOS`).
    Si no están en caché y el usuario está autenticado, los recarga automáticamente
    desde el core y los guarda en caché.

    :param id_usuario: El ID del usuario para quien se verificará la posesión de permisos.
    :type id_usuario: int
    :param permisos: Lista de permisos a verificar.
    :type permisos: list[str]
    :return: True si el usuario tiene todos los permisos ingresados; False en caso contrario.
    :rtype: bool
    """
    permisos_usuario = buscar_en_cache(PREFIJO_PERMISOS, id_usuario)
    if (
        _esta_autenticado()
        and not _esta_eliminado(id_usuario)
        and permisos_usuario is None
    ):
        permisos_usuario = buscar_permisos(id_usuario)
        guardar_en_cache(PREFIJO_PERMISOS, {id_usuario: permisos_usuario})

    permisos_usuario = permisos_usuario or []

    return set(permisos).issubset(set(permisos_usuario))


def limpiar_permisos_usuario(id_usuario: int):
    """
    Elimina los permisos de un usuario de la **cache** para forzar su recarga en la próxima petición.

    :param id_usuario: El ID del usuario para quien se limpiarán los permisos de la caché.
    :type id_usuario: int
    :rtype: None
    """
    invalidar_de_cache(PREFIJO_PERMISOS, id_usuario)


def _esta_autenticado() -> bool:
    """
    Verifica si el usuario está autenticado comprobando la existencia de la clave CLAVE_USUARIO_EMAIL en la sesión.

    :return: True si hay un email en la sesión, False en caso contrario.
    :rtype: bool
    """
    return existe_en_session(CLAVE_USUARIO_EMAIL)


def _es_admin() -> bool:
    """
    Verifica si el usuario actual tiene el rol de administrador leyendo el estado CLAVE_USUARIO_ES_ADMIN de la sesión.

    :return: True si el valor de la clave en sesión es verdadero; False en caso contrario o si la clave no existe.
    :rtype: bool
    """
    es_admin_dict = obtener_de_session([CLAVE_USUARIO_ES_ADMIN])
    return es_admin_dict.get(CLAVE_USUARIO_ES_ADMIN, False)


def sesion_es_propia(id) -> bool:
    """
    Verifica si el usuario autenticado es el mismo que se consulta

    :return: True si es el mismo usuario. False si es diferente.
    :rtype: bool
    """
    return id == buscar_datos_session([CLAVE_USUARIO_ID]).get(CLAVE_USUARIO_ID)


def _esta_eliminado(id_usuario) -> bool | None:
    """
    Verifica si el usuario con el ID dado ha sido eliminado del sistema.

    :return: True si el usuario ha sido eliminado; False en caso contrario.
    :rtype: bool
    """
    eliminado = obtener_eliminado_por_id(id_usuario)
    if eliminado is None:
        return False
    return eliminado
