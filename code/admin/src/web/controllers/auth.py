"""
Módulo de Vistas (Blueprint) para Autenticación y Gestión de Usuarios.

Define las rutas de Flask (Blueprint 'auth') para:
1. Login, autenticación y logout de usuarios.
2. CRUD completo (Listar, Ver, Crear, Editar, Eliminar) de usuarios del sistema.
3. Servicios auxiliares de validación de email y control de estado (bloqueo/desbloqueo).
"""

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
    request,
    current_app,
)
from core import auth
from core.flags import obtener_feature_flag
from web.utils.auth_utils import (
    cargar_permisos_usuario,
    limpiar_permisos_usuario,
    cargar_session_usuario,
    obtener_de_session,
    eliminar_session_usuario,
    permiso_requerido,
    sesion_es_propia,
)
from web.utils.auth_utils import buscar_datos_session
import re

from web.validators.usuario_validator import (
    validar_filtros_busqueda_usuarios,
    validar_crear_usuario,
    obtener_errores_formateados,
    validar_actualizar_usuario,
    validar_id_entero,
)

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")
"""
Definición del Blueprint 'auth' para agrupar todas las rutas de autenticación
y gestión de usuarios en el panel administrativo.
"""

CLAVE_USUARIO_ID = "id"
CLAVE_USUARIO_EMAIL = "email"
CLAVE_USUARIO_ES_ADMIN = "es_admin"
CLAVE_USUARIO_ACTIVO = "activo"
"""Constantes utilizadas como claves para almacenar datos del usuario en la sesión"""

PERMISO_USUARIOS_LISTAR = "usuarios_listar"
PERMISO_USUARIOS_VER = "usuarios_ver"
PERMISO_USUARIOS_CREAR = "usuarios_crear"
PERMISO_USUARIOS_ACTUALIZAR = "usuarios_actualizar"
PERMISO_USUARIOS_ELIMINAR = "usuarios_eliminar"
"""Constantes que definen los nombres de los permisos requeridos"""


@auth_blueprint.get("/")
def login():
    """
    Muestra el formulario de login.

    Verifica si el flag `modo_mantenimiento_admin` está activo para mostrar mensajes.

    :return: Renderiza el template con mensajes si corresponde,
             o devuelve un error 500 si ocurre un fallo.
    """
    try:
        flag = obtener_feature_flag("modo_mantenimiento_admin")
        mensajes_mantenimiento = []
        if flag and flag.estado and flag.mensaje_mantenimiento:
            mensajes_mantenimiento.append(flag.mensaje_mantenimiento)
        return render_template(
            "login.html", mensajes_mantenimiento=mensajes_mantenimiento
        )
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/auth"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.post("/autenticar")
def autenticar():
    """
    Procesa el formulario de login.

    Valida las credenciales (email y password). Si son válidas y el usuario está
    activo, inicia sesión cargando permisos y datos de usuario en la sesión.

    :return: Redirige al home si es exitoso o al login con un mensaje de error si falla
    """
    try:
        params = request.form

        user = auth.buscar_usuario_por_email_y_contrasena(
            params["email"], params["password"]
        )

        if not user:
            flash("Usuario o clave incorrecto.", "error")
            return redirect(url_for("auth.login"))

        if not user.activo:
            flash(
                "Su cuenta ha sido bloqueada. No es posible iniciar sesión.",
                "error",
            )
            return redirect(url_for("auth.login"))
        if user.eliminado:
            flash("Usuario no encontrado.")
            return redirect(url_for("auth.login"))

        datos_usuario = {
            CLAVE_USUARIO_ID: user.id_usuario,
            CLAVE_USUARIO_EMAIL: user.email,
            CLAVE_USUARIO_ES_ADMIN: user.es_admin,
            CLAVE_USUARIO_ACTIVO: user.activo,
        }

        cargar_permisos_usuario(user.id_usuario)
        cargar_session_usuario(datos_usuario)
        return redirect(url_for("home"))
    except Exception:
        msj = "Ocurrió un error inesperado"
        endpoint = "/auth/autenticar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.login"))


@auth_blueprint.get("/logout")
def logout():
    """
    Cierra la sesión del usuario actual.

    Limpia los permisos y la sesión del usuario, y notifica el cierre.

    :return: Redirige al login.
    """
    try:
        claves = [
            CLAVE_USUARIO_ID,
            CLAVE_USUARIO_EMAIL,
            CLAVE_USUARIO_ES_ADMIN,
            CLAVE_USUARIO_ACTIVO,
        ]
        datos_session_actual = obtener_de_session(claves)
        limpiar_permisos_usuario(datos_session_actual[CLAVE_USUARIO_ID])
        eliminar_session_usuario(claves)

        flash("La sesión se cerró correctamente.", "info")

        return redirect(url_for("auth.login"))
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/logout"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.get("/usuarios")
@permiso_requerido([PERMISO_USUARIOS_LISTAR])
def listar_usuarios():
    """
    Muestra la lista de usuarios con búsqueda, filtrado y paginación.

    Procesa los argumentos de la URL para filtrar por email, estado de actividad y rol,
    y aplica ordenamiento.

    :return: Renderiza el template 'usuarios/listar_usuarios.html' con los resultados.
    """
    try:
        email = request.args.get("email", "").strip()
        activo_str = request.args.get("activo", "").lower()
        id_rol_str = request.args.get("id_rol", "")

        orden = request.args.get("orden", "fecha_desc")
        pagina = request.args.get("pagina", 1, type=int)

        email, activo, id_rol, orden = validar_filtros_busqueda_usuarios(
            email, activo_str, id_rol_str, orden
        )

        usuario = buscar_datos_session([CLAVE_USUARIO_ID])
        id_usuario = usuario[CLAVE_USUARIO_ID]

        resultado = auth.buscar_usuarios_filtrados(
            id_usuario=id_usuario,
            email=email if email else None,
            activo=activo,
            id_rol=id_rol,
            orden=orden,
            pagina=pagina,
        )

        roles = auth.listar_roles()

        return render_template(
            "usuarios/listar_usuarios.html",
            usuarios=resultado["usuarios"],
            total=resultado["total"],
            paginas=resultado["paginas"],
            pagina_actual=resultado["pagina_actual"],
            tiene_anterior=resultado["tiene_anterior"],
            tiene_siguiente=resultado["tiene_siguiente"],
            roles=roles,
            filtro_email=email,
            filtro_activo=activo_str,
            filtro_id_rol=id_rol,
            orden_actual=orden,
        )
    except ValueError as e:
        msj = "Alguno de los datos ingresados no son válidos. Vuelva a intentarlo."
        endpoint = "/auth/usuarios"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        flash(msj, "error")
        return abort(404, msj)
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/auth/usuarios"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.get("/usuarios/<int:id_usuario>")
@permiso_requerido([PERMISO_USUARIOS_VER])
def ver_usuario(id_usuario):
    """
    Muestra el detalle de un usuario específico.

    :param id_usuario: ID del usuario a visualizar.
    :return: Renderiza el template o redirige a la lista si el usuario no existe.
    """
    try:

        validar_id_entero(id_usuario)

        usuario = auth.obtener_usuario_por_id(id_usuario)

        if not usuario or usuario.eliminado:
            raise ValueError("Usuario no encontrado.")

        rol_descripcion = "Sin rol asignado"
        if usuario.id_rol:
            rol = auth.obtener_rol_por_id(usuario.id_rol)
            rol_descripcion = rol.descripcion

        return render_template(
            "usuarios/ver_usuario.html",
            usuario=usuario,
            rol_usuario=rol_descripcion,
        )
    except ValueError as e:
        msj = "Alguno de los datos ingresados no son válidos. Vuelva a intentarlo."
        endpoint = "/auth/usuarios"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        return abort(404, msj)
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/usuarios"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.get("/usuarios/nuevo")
@permiso_requerido([PERMISO_USUARIOS_CREAR])
def nuevo_usuario():
    """
    Muestra el formulario para crear un nuevo usuario.

    Carga la lista de roles disponibles para el selector.

    :return: Renderiza el template 'usuarios/nuevo_usuario.html'.
    """
    try:
        roles = auth.listar_roles_asignables()
        return render_template("usuarios/nuevo_usuario.html", roles=roles)
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/auth/usuarios/nuevo"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.post("/usuarios/crear")
@permiso_requerido([PERMISO_USUARIOS_CREAR])
def crear_usuario():
    """
    Procesa los datos del formulario de creación de usuario.

    Realiza validación de campos requeridos y de email duplicado. Si el email
    duplicado corresponde a un usuario eliminado, lo "revive".

    :return: Redirige a la lista de usuarios si es exitoso.
    """
    try:
        data = request.form.to_dict()

        es_valido, errores = validar_crear_usuario(data)
        if not es_valido:
            flash(obtener_errores_formateados(errores), "error")
            return redirect(url_for("auth.nuevo_usuario"))

        rol = auth.obtener_rol_por_id(data["id_rol"])
        if not rol.es_asignable:
            flash("El rol ingresado no es asignable.", "error")
            return redirect(url_for("auth.nuevo_usuario"))

        user = auth.obtener_usuario_por_email(data["email"])

        if user and user.eliminado:
            auth.revivir_usuario(user, data)
            flash("Usuario recuperado y actualizado correctamente.", "success")
            return redirect(url_for("auth.listar_usuarios"))

        if user and not user.eliminado:
            flash("El email ya está registrado.", "error")
            return redirect(url_for("auth.nuevo_usuario"))

        auth.crear_usuario(**data)
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("auth.listar_usuarios"))

    except (ValueError, TypeError) as e:
        msj = "Alguno de los datos ingresados no son válidos. Vuelva a intentarlo."
        endpoint = "/auth/usuarios/crear"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.nuevo_usuario"))

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/usuarios/crear"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.nuevo_usuario"))


@auth_blueprint.get("/usuarios/<int:id_usuario>/editar")
@permiso_requerido([PERMISO_USUARIOS_ACTUALIZAR])
def editar_usuario(id_usuario):
    """
    Muestra el formulario para editar un usuario existente.

    Carga los datos del usuario y la lista de roles disponibles.

    :param id_usuario: ID del usuario a editar.
    :return: Renderiza el template o redirige si el usuario no existe.
    """
    try:

        validar_id_entero(id_usuario)

        usuario = auth.obtener_usuario_por_id(id_usuario)
        if (
            not usuario
            or usuario.eliminado
            or (not usuario.id_rol and not usuario.es_admin)
        ):
            raise ValueError("Usuario no encontrado.")

        roles = auth.listar_roles_asignables()
        return render_template(
            "usuarios/editar_usuario.html", usuario=usuario, roles=roles
        )

    except ValueError as e:
        msj = "Alguno de los datos ingresados no son válidos. Vuelva a intentarlo."
        endpoint = "/auth/usuarios/editar"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        return abort(404, msj)

    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/auth/usuarios/editar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@auth_blueprint.post("/usuarios/<int:id_usuario>/actualizar")
@permiso_requerido([PERMISO_USUARIOS_ACTUALIZAR])
def actualizar_usuario(id_usuario):
    """
    Procesa los datos del formulario de edición de usuario.

    Realiza validación de campos requeridos y de email duplicado. Actualiza
    el usuario si los datos son válidos, omitiendo el password si está vacío.

    :param id_usuario: ID del usuario a actualizar.
    :return: Redirige a la vista de detalle del usuario si es exitoso.
    """
    try:
        data = request.form.to_dict()

        es_valido, errores = validar_actualizar_usuario(id_usuario, data)

        if not es_valido:
            flash(obtener_errores_formateados(errores), "error")
            return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))

        usuario_actual = auth.obtener_usuario_por_id(id_usuario)

        if (
            not usuario_actual
            or usuario_actual.eliminado
            or usuario_actual.es_admin
            or not usuario_actual.id_rol
        ):
            flash("No es posible editar este usuario.", "error")
            return redirect(url_for("auth.listar_usuarios"))

        if auth.email_duplicado(data["email"], exclude_id=id_usuario):
            flash("El email ya está registrado.", "error")
            return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))

        if data.get("id_rol"):
            rol = auth.obtener_rol_por_id(data["id_rol"])

            if not rol:
                flash("El rol ingresado no existe.", "error")
                return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))
            if not rol.es_asignable:
                flash("El rol ingresado no es asignable.", "error")
                return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))
            if not usuario_actual.activo and not rol.es_bloqueable:
                flash(
                    "No es posible asignar un rol no bloqueable a un usuario bloqueado.",
                    "error",
                )
                return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))

        if not data.get("password", "").strip():
            data.pop("password", None)

        filtros = {
            "email": request.args.get("email", ""),
            "activo": request.args.get("activo", ""),
            "id_rol": request.args.get("id_rol", ""),
            "orden": request.args.get("orden", "fecha_desc"),
            "pagina": request.args.get("pagina", "1"),
        }

        auth.actualizar_usuario(id_usuario, data)
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario, **filtros))

    except (ValueError, TypeError) as e:
        msj = "Alguno de los datos ingresados no son válidos. Vuelva a intentarlo."
        endpoint = f"/auth/{id_usuario}/actualizar"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.nuevo_usuario"))

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/usuarios/actualizar"
        current_app.logger.exception(f"Mensaje: {msj}: {e}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.editar_usuario", id_usuario=id_usuario))


@auth_blueprint.post("/usuarios/validar-email")
@permiso_requerido([PERMISO_USUARIOS_CREAR])
def validar_email():
    """
    API endpoint para validar un email en tiempo real (por ejemplo, vía AJAX).

    Verifica el formato del email y si ya está registrado en la base de datos.

    :returns: Un objeto JSON con `valido` (bool) y `mensaje` (str).
    """
    try:
        data = request.get_json()
        email = data.get("email", "").strip()

        if not email:
            return jsonify({"valido": False, "mensaje": "El email es requerido"})

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return jsonify(
                {
                    "valido": False,
                    "mensaje": "El formato del email no es válido",
                }
            )

        usuario_existente = auth.obtener_usuario_por_email(email)
        if usuario_existente and not usuario_existente.eliminado:
            return jsonify(
                {"valido": False, "mensaje": "Este email ya está registrado"}
            )

        return jsonify({"valido": True, "mensaje": "Email disponible"})

    except Exception:
        msj = "Ocurrió un error inesperado al validar el email."
        endpoint = "/auth/usuarios/validar-email"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return jsonify({"valido": False, "mensaje": msj}), 500


@auth_blueprint.route("/bloquear_usuario/<int:id_usuario>", methods=["POST"])
@permiso_requerido([PERMISO_USUARIOS_ACTUALIZAR])
def bloquear_usuario(id_usuario: int):
    """
    Servicio encargado de realizar el bloqueo de un usuario en específico, validando
    si el usuario puede o no puede ser bloqueado previamente.

    Si el bloqueo es exitoso, limpia los permisos de la sesión.

    :param id_usuario: El ID del usuario a bloquear.
    :returns: Redirecciona a la vista del usuario.
    """
    try:

        validar_id_entero(id_usuario)

        usuario = auth.obtener_usuario_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if usuario.rol:
            if usuario.rol.es_bloqueable and not usuario.es_admin:
                if usuario.activo:
                    auth.bloquear_usuario(id_usuario)
                    limpiar_permisos_usuario(id_usuario)
                    current_app.logger.info(f"Usuario bloqueado: {usuario.email}")
                else:
                    flash("El usuario ya está bloqueado", "error")
                    return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))
            else:
                flash(
                    "No es posible bloquear al usuario debido a su rol",
                    "error",
                )
                return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))

            flash("Usuario bloqueado con exito", "success")
            return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))
        else:
            flash(
                "No es posible bloquear al usuario.",
                "error",
            )
            return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))
    except ValueError as ve:
        msj = (
            "Ocurrió un error al intentar bloquear al usuario con los datos ingresados."
        )
        endpoint = "/auth/cambiar_estado_bloqueo"
        current_app.logger.exception(f"Mensaje: {msj}: {ve}, Endpoint: {endpoint}")
        flash(msj, "error")

        return abort(404, msj)

    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/cambiar_estado_bloqueo"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))


@auth_blueprint.route("/desbloquear_usuario/<int:id_usuario>", methods=["POST"])
@permiso_requerido([PERMISO_USUARIOS_ACTUALIZAR])
def desbloquear_usuario(id_usuario: int):
    """
    Servicio encargado de realizar el desbloqueo de un usuario en específico.

    :param id_usuario: El ID del usuario a desbloquear.
    :returns: Redirecciona a la vista del usuario.
    """
    try:

        validar_id_entero(id_usuario)

        usuario = auth.obtener_usuario_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if usuario.rol:
            if usuario.rol.es_bloqueable and not usuario.es_admin:
                if not usuario.activo:
                    auth.desbloquear_usuario(id_usuario)
                    current_app.logger.info(f"Usuario desbloqueado: {usuario.email}")
                else:
                    flash("El usuario ya está desbloqueado", "error")
                    return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))

                flash("Usuario desbloqueado con exito", "success")
                return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))
            else:
                flash(
                    "No es posible desbloquear al usuario debido a su rol",
                    "error",
                )
                return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))
        else:
            flash(
                "No es posible desbloquear al usuario.",
                "error",
            )
            return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))

    except ValueError as ve:
        msj = (
            "Ocurrió un error al intentar bloquear al usuario con los datos ingresados."
        )
        endpoint = "/auth/cambiar_estado_bloqueo"
        current_app.logger.exception(f"Mensaje: {msj}: {ve}, Endpoint: {endpoint}")
        flash(msj, "error")

        return abort(404, msj)

    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/desbloquear_usuario"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.ver_usuario", id_usuario=id_usuario))


@auth_blueprint.post("/usuarios/<int:id_usuario>/eliminar")
@permiso_requerido([PERMISO_USUARIOS_ELIMINAR])
def eliminar_usuario(id_usuario):
    """
    Marca un usuario como eliminado (eliminación lógica).

    Si el usuario eliminado es el usuario de la sesión actual, la sesión se cierra.
    Mantiene los parámetros de filtrado y paginación en la redirección.

    :param id_usuario: ID del usuario a eliminar.
    :return: Redirige a la lista de usuarios.
    """
    try:
        filtros = {
            "email": request.args.get("email", ""),
            "activo": request.args.get("activo", ""),
            "id_rol": request.args.get("id_rol", ""),
            "orden": request.args.get("orden", "fecha_desc"),
            "pagina": request.args.get("pagina", "1"),
        }

        validar_id_entero(id_usuario)

        if sesion_es_propia(id_usuario):
            flash("No puedes eliminar tu propia cuenta.", "error")
            return redirect(url_for("auth.listar_usuarios", **filtros))

        auth.eliminar_usuario(id_usuario)
        flash("Usuario eliminado correctamente.", "info")

        limpiar_permisos_usuario(id_usuario)

        return redirect(url_for("auth.listar_usuarios", **filtros))

    except ValueError:
        msj = (
            "Ocurrió un error al intentar eliminar al usuario con los datos ingresados."
        )
        endpoint = "/auth/usuarios/eliminar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.listar_usuarios"))

    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/auth/usuarios/eliminar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("auth.listar_usuarios"))
