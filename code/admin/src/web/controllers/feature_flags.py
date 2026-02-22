"""Controlador del panel de Feature Flags en el admin."""

from flask import (
    Blueprint,
    current_app,
    abort,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from flask import flash
from web.utils.auth_utils import login_requerido, admin_requerido
from core.flags import (
    listar_feature_flags,
    actualizar_feature_flag,
    obtener_ultima_modificacion,
)
from web.validators.feature_flags_validators import (
    validar_datos_actualizacion,
    ESTADOS_ESPERADOS,
)

feature_flags_blueprint = Blueprint(
    "feature_flags", __name__, url_prefix="/feature-flags"
)


@feature_flags_blueprint.route("/")
@login_requerido
@admin_requerido
def index():
    """
    Vista principal del panel de feature flags.
    Muestra todos los flags, su estado y registros de modificación.
    """
    try:
        flags = listar_feature_flags()
        flags_data = []

        for flag in flags:

            ultima_mod = obtener_ultima_modificacion(flag.id_flag)
            usuario_modificacion_str = "Sin modificaciones"

            if ultima_mod and ultima_mod.usuario:
                usuario_modificacion_str = (
                    f"{ultima_mod.usuario.nombre} {ultima_mod.usuario.apellido}"
                )
            elif ultima_mod:
                usuario_modificacion_str = (
                    f"Usuario ID: {ultima_mod.id_usuario} (eliminado)"
                )

            flag_info = {
                "flag": flag,
                "ultima_modificacion": ultima_mod,
                "usuario_modificacion": usuario_modificacion_str,
            }
            flags_data.append(flag_info)

        return render_template("feature_flags.html", flags_data=flags_data)
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/feature-flags"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@feature_flags_blueprint.route("/toggle/<nombre>", methods=["POST"])
@login_requerido
@admin_requerido
def toggle_flag(nombre):
    """
    Actualiza el estado y mensaje de un feature flag.
    """
    try:
        estado_str = request.form.get("estado")
        mensaje_mantenimiento = request.form.get("mensaje_mantenimiento", "")
        user_id = session["id"]

        validar_datos_actualizacion(estado_str, mensaje_mantenimiento, nombre)

        hubo_cambios = actualizar_feature_flag(
            nombre,
            ESTADOS_ESPERADOS[estado_str.lower()],
            mensaje_mantenimiento,
            user_id,
        )

        if hubo_cambios:
            flash("Feature flag actualizado correctamente", "success")
        else:
            flash("No hubo cambios", "info")

    except ValueError as e:
        msj = "Ocurrió un error al actualizar el feature flag con los datos ingresados."
        endpoint = "/feature-flags"
        current_app.logger.exception(f"Mensaje: {msj}: {str(e)}, Endpoint: {endpoint}")
        flash(msj, "error")

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/feature-flags"
        current_app.logger.exception(f"Mensaje: {msj}: {str(e)}, Endpoint: {endpoint}")
        flash(msj, "error")
    finally:
        return redirect(url_for("feature_flags.index"))
