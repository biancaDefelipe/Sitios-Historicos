"""
Módulo de Vistas (Blueprint) para la Gestión de Reseñas (Resenias).

Define las rutas de Flask (Blueprint 'resenias') para la administración de
reseñas de la plataforma. Incluye endpoints para listar, aprobar, rechazar,
eliminar y obtener el detalle de reseñas, así como para listar los estados
disponibles de las mismas. Todos los endpoints requieren autenticación y permisos específicos.
"""

from flask import (
    Blueprint,
    current_app,
    abort,
    flash,
    redirect,
    url_for,
    request,
    render_template,
    jsonify,
)
from web.utils.auth_utils import login_requerido, permiso_requerido
from core.services import resenia_service
from web.validators.resenias_validators import validar_listar_resenias


bp = Blueprint("resenias", __name__, url_prefix="/resenias")

PERMISO_RESENIAS_LISTAR = "resenias_listar"
PERMISO_RESENIAS_VER = "resenias_ver"
PERMISO_RESENIAS_CREAR = "resenias_crear"
PERMISO_RESENIAS_ACTUALIZAR = "resenias_actualizar"
PERMISO_RESENIAS_ELIMINAR = "resenias_eliminar"


@bp.route("/")
@login_requerido
@permiso_requerido([PERMISO_RESENIAS_LISTAR])
def index():
    """
    Muestra la pantalla con todas las reseñas.

    :return: Renderiza el template 'resenias/listar_resenias.html' o devuelve un error 500.
    """
    try:
        return render_template("resenias/listar_resenias.html")
    except Exception as e:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/resenias"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@bp.post("/listar")
@permiso_requerido([PERMISO_RESENIAS_LISTAR])
def listar_resenias():
    """
    Obtiene todas las reseñas paginadas, aplicando los filtros establecidos.

    Este endpoint consume datos JSON para los filtros y parámetros de la URL
    para paginación y ordenamiento.

    :param nro_pagina: Número de la página a mostrar (query param).
    :param orden: Criterio de ordenamiento (query param).
    :param filtros: Diccionario de filtros en el cuerpo del JSON (e.g., estado, fecha).
    :returns: JSON con la lista de reseñas serializadas y metadatos de paginación.
    """
    try:
        nro_pagina = request.args.get("nro_pagina", 1, type=int)
        orden = request.args.get("orden")

        data = request.get_json(silent=True) or {}
        filtros = data.get("filtros", {}) or {}

        validar_listar_resenias(filtros, {"nro_pagina": nro_pagina, "orden": orden})

        resenias, pageable = resenia_service.obtener_resenias(
            filtros, orden, nro_pagina
        )

        return jsonify(
            {
                "items": [res.serialize() for res in resenias],
                "pageable": {
                    "page": pageable["page"],
                    "per_page": pageable["per_page"],
                    "total": pageable["total"],
                    "pages": pageable["total_pages"],
                    "has_next": pageable["has_next"],
                    "has_prev": pageable["has_prev"],
                },
            }
        )
    except ValueError as e:
        msj = str(e)
        flash_msj = "Alguno de los datos ingresados no es válido."
        endpoint = "/resenias/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(flash_msj, "error")
        return redirect(url_for("resenias.listar_resenias"))
    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/resenias/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("resenias.listar_resenias"))


@bp.get("/estados_resenias")
@permiso_requerido([PERMISO_RESENIAS_LISTAR])
def listar_estados_resenias():
    """
    Lista todos los estados de resenias disponibles en el sistema (API endpoint).

    :returns: JSON con una lista de diccionarios de estados de reseña (id y descripción).
    """
    try:
        estados_resenias = resenia_service.listar_estados_resenias()
        return jsonify(
            [
                {
                    "id_estado_resenia": e.id_estado_resenia,
                    "descripcion": e.descripcion,
                }
                for e in estados_resenias
            ]
        )
    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/resenias/estados_resenias"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("resenias.listar_resenias"))


@bp.put("/aprobar")
@permiso_requerido([PERMISO_RESENIAS_ACTUALIZAR])
def aprobar_reseña():
    """
    Aprueba la reseña con el ID recibido por parámetro (query string).

    :query id_resenia: El ID de la reseña a aprobar.
    :returns: JSON con mensaje de éxito (200) o error (400/500).
    """
    id_resenia = request.args.get("id_resenia", type=int)

    try:
        resenia_service.aprobar_resenia(id_resenia)

        flash("Reseña aprobada con éxito.", "success")

        return jsonify({"mensaje": "Reseña aprobada con éxito."}), 200

    except ValueError:
        flash("No se encontró la reseña. No se logró aprobar.", "error")
        return (
            jsonify({"mensaje": "No se encontró la reseña. No se logró aprobar."}),
            400,
        )

    except Exception as e:
        msj = "Ocurrió un error inesperado al intentar aprobar la reseña."
        endpoint = "/resenias/aprobar"
        current_app.logger.exception(
            f"Mensaje: {msj}, Endpoint: {endpoint} - Detalle: {e}"
        )

        flash(msj, "error")

        return jsonify({"mensaje": msj}), 500


@bp.put("/eliminar")
@permiso_requerido([PERMISO_RESENIAS_ELIMINAR])
def eliminar_reseña():
    """
    Elimina (lógicamente) la reseña con el ID recibido por parámetro (query string).

    :query id_resenia: El ID de la reseña a eliminar.
    :returns: JSON con mensaje de éxito (200) o error (400/500).
    """
    id_resenia = request.args.get("id_resenia", type=int)

    try:
        resenia_service.eliminar_resenia(id_resenia)

        flash("Reseña eliminada con éxito.", "success")

        return jsonify({"mensaje": "Reseña eliminada con éxito."}), 200

    except ValueError:
        flash("No se encontró la reseña. No se logró aliminar.", "error")
        return (
            jsonify({"mensaje": "No se encontró la reseña. No se logró eliminar."}),
            400,
        )

    except Exception as e:
        msj = "Ocurrió un error inesperado al intentar eliminar la reseña."
        endpoint = "/resenias/aprobar"
        current_app.logger.exception(
            f"Mensaje: {msj}, Endpoint: {endpoint} - Detalle: {e}"
        )

        flash(msj, "error")

        return jsonify({"mensaje": msj}), 500


@bp.put("/rechazar")
@permiso_requerido([PERMISO_RESENIAS_ACTUALIZAR])
def rechazar_reseña():
    """
    Rechaza una reseña con el ID recibido por parámetro (query string),
    requiriendo un "motivo" en el cuerpo del JSON.

    :query id_resenia: El ID de la reseña a rechazar.
    :body motivo: La razón del rechazo (string, requerido, máx 200 chars).
    :returns: JSON con mensaje de éxito (200) o error (400/500).
    """
    id_resenia = request.args.get("id_resenia", type=int)

    data = request.get_json(silent=True) or {}
    motivo = data.get("motivo") if isinstance(data, dict) else None

    if not motivo or not isinstance(motivo, str) or not motivo.strip():
        flash("El motivo del rechazo es obligatorio.", "error")
        return (
            jsonify({"mensaje": "El motivo del rechazo es obligatorio."}),
            400,
        )

    motivo = motivo.strip()
    if len(motivo) > 200:
        flash("El motivo no puede superar los 200 caracteres.", "error")
        return (
            jsonify({"mensaje": "El motivo no puede superar los 200 caracteres."}),
            400,
        )

    try:
        resenia_service.rechazar_resenia(id_resenia, motivo)
        flash("Reseña rechazada con éxito.", "success")
        return jsonify({"mensaje": "Reseña rechazada con éxito."}), 200

    except ValueError:
        flash("No se encontró la reseña. No se logró rechazar.", "error")
        return (
            jsonify({"mensaje": "No se encontró la reseña. No se logró rechazar."}),
            400,
        )

    except Exception as e:
        msj = "Ocurrió un error inesperado al intentar rechazar la reseña."
        endpoint = "/resenias/rechazar"
        current_app.logger.exception(
            f"Mensaje: {msj}, Endpoint: {endpoint} - Detalle: {e}"
        )

        flash(msj, "error")

        return jsonify({"mensaje": msj}), 500


@bp.get("/get")
@permiso_requerido([PERMISO_RESENIAS_VER])
def get_resenia():
    """
    Obtiene los detalles de una reseña específica por su ID (API endpoint).

    Espera el ID de la reseña en el query string.

    :query id_resenia: ID de la reseña a obtener.
    :returns: JSON con los datos serializados de la reseña (200) o un error (400/500).
    """
    id_resenia = request.args.get("id_resenia", type=int)
    if not id_resenia:
        return jsonify({"mensaje": "id_resenia requerido"}), 400

    try:
        datos = resenia_service.obtener_detalle_resenia(id_resenia)
        return jsonify(datos.serialize()), 200
    except ValueError:
        flash("No se encontró la reseña. No se logró rechazar.", "error")
        return jsonify({"mensaje": "No se encontró la reseña."}), 400

    except Exception as e:
        current_app.logger.exception("Error en endpoint /resenias/get: %s", e)
        return jsonify({"mensaje": "Error interno"}), 500
