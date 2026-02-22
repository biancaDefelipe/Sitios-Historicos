"""Controlador de gestión de etiquetas (tags) en el admin."""

from flask import (
    Blueprint,
    jsonify,
    abort,
    render_template,
    request,
    flash,
    current_app,
)
from slugify import slugify
from web.utils.auth_utils import login_requerido, permiso_requerido
from core.sitios_historicos import (
    editar_tag,
    listar_tags,
    crear_tag,
    borrar_tag,
    existe_tag_nombre_slug,
)


from web.validators.tags_validators import (
    validar_listar_tags,
    validar_nombre_tag,
    validar_id_tag,
)


bp = Blueprint("tags", __name__, url_prefix="/tags")

PERMISO_TAGS_LISTAR = "tags_listar"
PERMISO_TAGS_VER = "tags_ver"
PERMISO_TAGS_CREAR = "tags_crear"
PERMISO_TAGS_ACTUALIZAR = "tags_actualizar"
PERMISO_TAGS_ELIMINAR = "tags_eliminar"


@bp.route("/", methods=["GET"])
@login_requerido
@permiso_requerido([PERMISO_TAGS_LISTAR])
def index():
    """
    Vista HTML que lista tags con búsqueda, orden y paginación.
    Query params:
      - q: texto de búsqueda (opcional)
      - order: name_asc | name_desc | fecha_asc | fecha_desc
      - page: número de página (1-based)
    """
    try:
        q = request.args.get("q", None)
        order = request.args.get("order", "fecha_desc")
        page = request.args.get("page", 1, type=int)

        try:
            validar_listar_tags(q, order, page, per_page=None)

        except ValueError as ve:
            current_app.logger.warning("Validación listar tags: %s", ve)
            abort(400, description=str(ve))

        items, pagination = listar_tags(q=q, order=order, page=page)

        if (
            pagination
            and pagination["total_pages"] > 0
            and page > pagination["total_pages"]
        ):
            mensaje = f"La página {page} no existe. Total de páginas: {pagination['total_pages']}."
            current_app.logger.warning(mensaje)
            abort(404, description=mensaje)

        return render_template(
            "tags.html",
            tags=items,
            pagination=pagination,
            q=q or "",
            order=order,
        )
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/tags"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@bp.route("/crear", methods=["POST"])
@permiso_requerido([PERMISO_TAGS_CREAR])
def crear():
    """
    Crear un nuevo tag. Si la petición es AJAX, responde en JSON.
    """
    try:
        data = request.get_json(silent=True)

        try:
            validar_nombre_tag(data, existe_tag_nombre_slug)
        except ValueError as ve:
            flash(str(ve), "error")
            return jsonify({"error": str(ve)}), 400

        nombre = data.get("nombre")

        nombre = nombre.strip()
        nombre_normalizado = nombre.lower()
        slug = slugify(nombre_normalizado)

        try:
            new_tag = crear_tag(nombre, slug)

            flash(f"Tag '{new_tag.nombre}' creado correctamente.", "success")
            return jsonify({"success": True})

        except ValueError as e:
            flash("Error al crear tag.", "error")
            return ("", 400)

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        endpoint = "/tags/crear"
        current_app.logger.exception(f"Mensaje: {msj}: {str(e)}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@bp.route("/editar/<int:tag_id>", methods=["PUT"])
@permiso_requerido([PERMISO_TAGS_ACTUALIZAR])
def editar(tag_id):
    """
    Edita el tag con el id recibido. Verifica que no exista otro tag con el miso nombre o slug
    """
    try:
        data = request.get_json(silent=True)

        try:
            validar_nombre_tag(data, existe_tag_nombre_slug)
            validar_id_tag(tag_id)
        except ValueError as ve:
            flash(str(ve), "error")
            return jsonify({"error": str(ve)}), 400

        nombre = data["nombre"].strip()
        nombre_normalizado = nombre.lower()
        slug = slugify(nombre_normalizado)

        try:
            tag = editar_tag(tag_id, nombre, slug)

            flash(f"Tag '{tag.nombre}' actualizado correctamente.", "success")
            return jsonify({"success": True}), 200
        except ValueError as e:
            flash("Error al editar tag.", "error")
            return ("", 400)

    except ValueError as ve:
        msj = "Ocurrió un error al intentar editar un tag con los datos ingresados."
        endpoint = f"/tags/editar/{tag_id}"
        current_app.logger.exception(f"Mensaje: {msj}: {str(ve)}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 400

    except Exception as ex:
        msj = "Ocurrió un error inesperado."
        endpoint = f"/tags/editar/{tag_id}"
        current_app.logger.exception(f"Mensaje: {msj}: {str(ex)}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@bp.route("/borrar/<int:tag_id>", methods=["POST"])
@permiso_requerido([PERMISO_TAGS_ELIMINAR])
def borrar(tag_id):
    """
    Elimina un tag. Si está asociado a sitios, responde con error.
    """
    try:
        validar_id_tag(tag_id)
        borrar_tag(tag_id)
        flash("Tag eliminado correctamente.", "success")
        return jsonify({"success": True}), 200

    except ValueError:
        msj = "No se puede borrar el tag porque está en uso."
        endpoint = "/tags/borrar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return (
            jsonify({"error": "No se puede borrar el tag porque está en uso."}),
            400,
        )
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/tags/borrar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": "Error interno al borrar tag."}), 500


@bp.route("/listar", methods=["GET"])
@login_requerido
@permiso_requerido([PERMISO_TAGS_LISTAR])
def api_list():
    """
    Endpoint JSON para consumir la lista de tags (útil para fetch/AJAX).
    Parámetros idénticos a la vista HTML.
    Devuelve: { tags: [...], pagination: {...} }
    """
    try:
        q = request.args.get("q", None)
        order = request.args.get("order", "name_asc")
        page = request.args.get("page", 1, type=int)

        items, pagination = listar_tags(q=q, order=order, page=page)

        if (
            pagination
            and pagination["total_pages"] > 0
            and page > pagination["total_pages"]
        ):
            return (
                jsonify(
                    {
                        "error": f"La página {page} no existe. Total de páginas: {pagination['total_pages']}."
                    }
                ),
                404,
            )

        def serialize_tag(t):
            """Serializa un tag a un diccionario JSON."""
            return {
                "id_tag": getattr(t, "id_tag", None),
                "nombre": getattr(t, "nombre", None),
                "slug": getattr(t, "slug", None),
                "fecha_hora_alta": (
                    getattr(t, "fecha_hora_alta", None).isoformat()
                    if getattr(t, "fecha_hora_alta", None)
                    else None
                ),
            }

        tags_json = [serialize_tag(t) for t in items]

    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/tags/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500

    return jsonify({"tags": tags_json, "pagination": pagination})
