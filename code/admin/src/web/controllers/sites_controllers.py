"""Módulo de controladores para la gestión de sitios históricos."""

from flask import (
    Blueprint,
    jsonify,
    abort,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    current_app,
    make_response,
)
from core import sitios_historicos, historial
from web.dtos.site_dto import SiteDTO
from core.localidad import obtener_provincias
from web.utils.auth_utils import (
    login_requerido,
    permiso_requerido,
    buscar_datos_session,
    CLAVE_USUARIO_ID,
)
from core.utils.forms import SiteForm
import json
from datetime import datetime, time
from io import BytesIO
from web.utils.csv_utils import generar_csv, obtener_data_headers_sitios
from web.validators.sites_validators import (
    validar_filtros,
    validar_rango_fechas,
)
from web.validators.file_validators import (
    validate_images_count,
)


def get_user_id_from_session():
    """Extrae el ID del usuario de la sesión, manejando el caso de no estar autenticado."""
    datos = buscar_datos_session([CLAVE_USUARIO_ID])
    return datos.get(CLAVE_USUARIO_ID)


def get_site_repo():
    """Obtiene una instancia del repositorio de sitios históricos."""
    return current_app.config["SITE_REPO"]


sites_bp = Blueprint("sites", __name__, url_prefix="/sitios")


PERMISO_SITIOS_LISTAR = "sitios_listar"
PERMISO_SITIOS_VER = "sitios_ver"
PERMISO_SITIOS_CREAR = "sitios_crear"
PERMISO_SITIOS_ACTUALIZAR = "sitios_actualizar"
PERMISO_SITIOS_ELIMINAR = "sitios_eliminar"

PERMISO_RESENIAS_LISTAR = "resenias_listar"

PERMISO_TAGS_LISTAR = "tags_listar"
PERMISO_TAGS_VER = "tags_ver"


def _cargar_choices_formulario(form):
    """Carga las opciones (choices) para los campos SelectField del formulario."""
    try:
        site_repo = get_site_repo()
        provincias_data = obtener_provincias()
        categorias_data = site_repo.listar_categorias()
        estados_data = site_repo.listar_estados()

        nombres_provincias = [p["nombre"] for p in provincias_data]

        form.provincia.choices = [("", "Selecciona Provincia")] + [
            (nombre, nombre) for nombre in nombres_provincias
        ]
        form.categoria.choices = [("", "Selecciona Categoría")] + [
            (c["descripcion"], c["descripcion"]) for c in categorias_data
        ]
        form.estado.choices = [("", "Selecciona Estado")] + [
            (e["descripcion"], e["descripcion"]) for e in estados_data
        ]
        return True
    except Exception:
        current_app.logger.exception(
            "Error crítico al cargar datos de referencia para el formulario."
        )
        form.provincia.choices = [("", "Error al cargar")]
        form.categoria.choices = [("", "Error al cargar")]
        form.estado.choices = [("", "Error al cargar")]
        return False


@sites_bp.route("/")
@login_requerido
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def index():
    """
    Muestra la pantalla con todos los sitios.
    """
    try:
        return render_template("sitios.html")
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/sitios"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@sites_bp.route("/nombre_localidad", methods=["GET"])
@permiso_requerido([PERMISO_SITIOS_LISTAR, PERMISO_RESENIAS_LISTAR])
def listar_id_nombre_sitios():
    """
    Lista el nombre y la localidad de todos los Sitios Históricos disponibles en el sistema.
    """
    try:
        site_repo = get_site_repo()
        return jsonify(site_repo.listar_nombre_localidad())
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/sitios/nombre_localidad"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("sites.listar_sitios"))


@sites_bp.route("/listar", methods=["POST"])
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def listar_sitios():
    """Lista los sitios históricos aplicando filtros, paginación y ordenamiento.

    :param page: número de página actual para la paginación (query param).
    :param orden: criterio de ordenamiento (query param).
    :param filtros: diccionario con filtros opcionales como fechas, nombre, provincia, etc. (body JSON).
    :return: un JSON con la lista de sitios filtrados y la información de paginación.
    """
    site = get_site_repo()
    try:
        page = request.args.get("page", 1, type=int)
        orden = request.args.get("order")

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "JSON inválido en el body"}), 400

        filtros = data.get("filtros", {}) or {}

        validar_filtros(filtros)

        validar_rango_fechas(filtros.get("fecha_desde"), filtros.get("fecha_hasta"))

        sitios, pagination = site.list(filtros=filtros, orden=orden, page=page)

        return jsonify(
            {
                "items": [s.to_dict() for s in sitios],
                "pagination": {
                    "page": pagination["page"],
                    "per_page": pagination["per_page"],
                    "total": pagination["total"],
                    "pages": pagination["total_pages"],
                    "has_next": pagination["has_next"],
                    "has_prev": pagination["has_prev"],
                },
            }
        )
    except TypeError as e:
        msj = str(e)
        return_msj = "Alguno de los datos ingresados no es válido."
        endpoint = "/sitios/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint {endpoint}")
        return jsonify({"error": return_msj}), 400
    except ValueError:
        msj = str(e)
        return_msj = "Alguno de los datos ingresados no es válido."
        endpoint = "/sitios/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint {endpoint}")
        return jsonify({"error": return_msj}), 400
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/sitios/listar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint {endpoint}")
        return jsonify({"error": msj}), 500


@sites_bp.route("/categorias", methods=["GET"])
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def listar_categorias():
    """Obtiene todas las categorías disponibles de sitios históricos.

    :return: un JSON con la lista de categorías.
    """
    try:
        site_repo = get_site_repo()
        return jsonify(site_repo.listar_categorias())
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/sitios/categorias"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return jsonify({"error": msj}), 500


@sites_bp.route("/estados", methods=["GET"])
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def listar_estados():
    """Obtiene todos los estados de conservación registrados para los sitios históricos.

    :return: un JSON con la lista de estados.
    """
    try:
        site_repo = get_site_repo()
        return jsonify(site_repo.listar_estados())
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/sitios/estados"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return jsonify({"error": msj}), 500


@sites_bp.route("/provincias", methods=["GET"])
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def listar_provincias():
    """Obtiene la información de todas las provincias disponibles.

    :return: un JSON con la lista de provincias o un mensaje de error en caso de fallo.
    """
    try:
        site_repo = get_site_repo()
        provincias = site_repo.listar_provincias()
        return jsonify(provincias)
    except Exception:
        msj = "Ocurrió un error inesperado."
        endpoint = "/sitios/provincias"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return jsonify({"error": msj}), 500


@sites_bp.route("/crear", methods=["GET", "POST"])
@permiso_requerido([PERMISO_SITIOS_CREAR])
def new():
    """Crea un nuevo sitio histórico en el sistema.

    :param form: instancia de SiteForm que contiene los datos del formulario de creación.
    :return: renderiza el formulario de creación en GET o redirige al listado tras la creación exitosa.
    """
    try:
        form = SiteForm()

        if not _cargar_choices_formulario(form):
            flash("Error crítico al cargar datos de referencia.", "danger")
            return render_template("crear_sitio.html", form=form)

        if form.validate_on_submit():
            try:
                site_repo = get_site_repo()

                tag_names = json.loads(form.tags.data) if form.tags.data else []
                latitud_float = float(form.latitud.data)
                longitud_float = float(form.longitud.data)
                categoria_id = site_repo.obtener_categoria_id(form.categoria.data)
                estado_id = site_repo.obtener_estado_id(form.estado.data)
                imagenes_data_str = request.form.get("imagenes_json_data")
                imagenes_data = (
                    json.loads(imagenes_data_str) if imagenes_data_str else []
                )

                validate_images_count(imagenes_data)

                dto = SiteDTO(
                    nombre=form.nombre.data.strip(),
                    descripcion_breve=form.descripcion_breve.data,
                    descripcion_detallada=form.descripcion_detallada.data,
                    anio_inauguracion=form.anio_inauguracion.data,
                    visible=form.visible.data == "True",
                    ciudad=form.ciudad.data,
                    provincia=form.provincia.data,
                    categoria=form.categoria.data,
                    estado=form.estado.data,
                    tags=tag_names,
                    latitud=latitud_float,
                    longitud=longitud_float,
                    categoria_id=categoria_id,
                    estado_id=estado_id,
                )

                user_id = get_user_id_from_session()
                if not user_id:
                    flash(
                        "Error de sesión: ID de usuario no encontrado.",
                        "error",
                    )
                    return redirect(url_for("auth.login"))

                site_repo.create(dto, user_id, imagenes_data)

                flash("Sitio creado exitosamente.", "success")
                response = make_response(redirect(url_for("sites.index")))
                response.headers["Cache-Control"] = (
                    "no-cache, no-store, must-revalidate"
                )
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                return response

            except (ValueError, TypeError, json.JSONDecodeError):
                msj = "Error en los datos del formulario de creacion de sitio."
                endpoint = "/sitios/crear"
                current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
                flash(msj, "error")
                return render_template("crear_sitio.html", form=form), 400

        return render_template("crear_sitio.html", form=form)
    except Exception:
        msj = "Ocurrió un error inesperado al acceder al modulo."
        endpoint = "/sitios/crear"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return abort(500, msj)


@sites_bp.route("/editar/<int:site_id>", methods=["GET", "POST"])
@permiso_requerido([PERMISO_SITIOS_ACTUALIZAR])
def edit(site_id):
    """Edita la información de un sitio histórico existente.

    :param site_id: identificador único del sitio a editar.
    :param form: instancia de SiteForm con los datos del formulario de edición.
    :return: renderiza el formulario de edición o redirige al listado tras la actualización exitosa.
    """
    try:
        site_repo = get_site_repo()
        site = site_repo.get(site_id)
        if not site:
            flash("Sitio no encontrado.", "error")
            return redirect(url_for("sites.index"))

        imagenes_list = site.images or []

        if request.method == "POST":
            form = SiteForm()
        else:
            form = SiteForm(
                nombre=site.nombre,
                descripcion_breve=site.descripcion_breve,
                descripcion_detallada=site.descripcion_detallada,
                ciudad=site.ciudad,
                provincia=site.provincia,
                estado=site.estado,
                categoria=site.categoria,
                anio_inauguracion=site.anio_inauguracion,
                fecha_registro=(
                    site.fecha_hora_alta[:10] if site.fecha_hora_alta else ""
                ),
                visible="True" if site.visible else "False",
                latitud=site.latitud,
                longitud=site.longitud,
                tags=json.dumps(site.tags or []),
            )

        if not _cargar_choices_formulario(form):
            flash("Error crítico al cargar datos de referencia.", "danger")
            return render_template(
                "editar_sitio.html",
                form=form,
                sitio=site,
                imagenes_list=imagenes_list,
            )

        if form.validate_on_submit():
            try:
                user_id = get_user_id_from_session()
                if not user_id:
                    flash(
                        "Error de sesión: ID de usuario no encontrado.",
                        "error",
                    )
                    return redirect(url_for("auth.login"))

                dto = SiteDTO(
                    id=site_id,
                    nombre=form.nombre.data,
                    descripcion_breve=form.descripcion_breve.data,
                    descripcion_detallada=form.descripcion_detallada.data,
                    anio_inauguracion=form.anio_inauguracion.data,
                    visible=form.visible.data == "True",
                    ciudad=form.ciudad.data,
                    provincia=form.provincia.data,
                    latitud=form.latitud.data,
                    longitud=form.longitud.data,
                    tags=json.loads(form.tags.data) if form.tags.data else [],
                    categoria=form.categoria.data,
                    estado=form.estado.data,
                )

                imagenes_data = None
                imagenes_edit_data_str = request.form.get("imagenes_json_data")
                if imagenes_edit_data_str:
                    try:
                        imagenes_data = json.loads(imagenes_edit_data_str)
                        temporales = [
                            img for img in imagenes_data if not img.get("id_imagen")
                        ]
                        existentes = [
                            img for img in imagenes_data if img.get("id_imagen")
                        ]

                        validate_images_count(imagenes_data)

                    except json.JSONDecodeError as e:
                        current_app.logger.error(
                            f"Error al parsear imagenes_json_data: {e}"
                        )

                site_repo.update(site_id, dto, user_id, imagenes_data)

                flash("Sitio actualizado exitosamente.", "success")
                response = make_response(redirect(url_for("sites.index")))
                response.headers["Cache-Control"] = (
                    "no-cache, no-store, must-revalidate"
                )
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                return response

            except ValueError as e:
                current_app.logger.warning(
                    f"Error de validación al editar sitio {site_id}: {e}"
                )
                flash(str(e), "error")
                return (
                    render_template(
                        "editar_sitio.html",
                        form=form,
                        sitio=site,
                        imagenes_list=imagenes_list,
                    ),
                    400,
                )

        return render_template(
            "editar_sitio.html",
            form=form,
            sitio=site,
            imagenes_list=imagenes_list,
        )
    except Exception:
        current_app.logger.exception(
            f"Error al cargar la página de edición para el sitio {site_id}"
        )
        flash("No se pudo cargar la página de edición.", "danger")
        return redirect(url_for("sites.index"))


@sites_bp.post("/eliminar/<int:site_id>")
@permiso_requerido([PERMISO_SITIOS_ELIMINAR])
def delete(site_id):
    """Elimina (lógicamente) un sitio histórico existente.

    :param site_id: identificador único del sitio a eliminar.
    :return: redirige al listado de sitios con un mensaje flash de éxito o error.
    """
    try:
        site_repo = get_site_repo()
        user_id = get_user_id_from_session()
        if not user_id:
            flash("Error de sesión: ID de usuario no encontrado.", "error")
            return redirect(url_for("auth.login"))

        site_repo.delete(site_id, user_id)
        flash("Sitio eliminado exitosamente.", "success")
        return redirect(url_for("sites.index"))
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/eliminar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(url_for("sites.index"))


@sites_bp.get("/provincia_sitio/<int:site_id>")
@permiso_requerido([PERMISO_SITIOS_VER])
def obtener_provincia_sitio(site_id: int):
    """Obtiene la provincia asociada a un sitio histórico dado su ID.

    :param site_id: identificador único del sitio.
    :return: un JSON con la provincia del sitio o un mensaje de error si no se encuentra.
    """
    try:
        site_repo = get_site_repo()
        site = site_repo.get(site_id)
        if site:
            return jsonify({"provincia": site.provincia})
        return jsonify({"error": "Sitio no encontrado"}), 404
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/provincia_sitio"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@sites_bp.get("/tags")
@permiso_requerido([PERMISO_TAGS_LISTAR])
def obtener_tags():
    """Obtiene la lista completa de tags disponibles.

    :return: un JSON con los tags registrados.
    """
    try:
        site_repo = get_site_repo()
        tags = site_repo.listar_tags()
        return jsonify(tags)
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "sitios/tags"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(request.referrer)


@sites_bp.get("/tags_sitio/<int:site_id>")
@permiso_requerido([PERMISO_TAGS_VER])
def obtener_tags_sitio(site_id: int):
    """Obtiene los tags del sitio recibido por parámetro"""
    try:
        site_repo = get_site_repo()
        tags = site_repo.obtener_tags(site_id)

        return jsonify([tag for tag in tags])
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/tags_sitio"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return redirect(request.referrer)


@sites_bp.get("/ciudad_sitio/<int:site_id>")
@permiso_requerido([PERMISO_SITIOS_VER])
def obtener_ciudad_sitio(site_id: int):
    """Obtiene la ciudad correspondiente a un sitio histórico.

    :param site_id: identificador único del sitio.
    :return: un JSON con la ciudad del sitio o un mensaje de error si no existe.
    """
    try:
        site_repo = get_site_repo()
        site = site_repo.get(site_id)
        if site:
            return jsonify({"ciudad": site.ciudad})
        return jsonify({"error": "Sitio no encontrado"}), 404
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/ciudad_sitio"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@sites_bp.get("/categoria_sitio/<int:site_id>")
@permiso_requerido([PERMISO_SITIOS_VER])
def obtener_categoria_sitio(site_id: int):
    """Obtiene la categoría asociada a un sitio histórico.

    :param site_id: identificador único del sitio.
    :return: un JSON con la categoría del sitio o un mensaje de error si no se encuentra.
    """
    try:
        site_repo = get_site_repo()
        site = site_repo.get(site_id)
        if site:
            return jsonify({"categoria": site.categoria})
        return jsonify({"error": "Sitio no encontrado"}), 404
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/categoria_sitio"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@sites_bp.get("/estado_sitio/<int:site_id>")
@permiso_requerido([PERMISO_SITIOS_VER])
def obtener_estado_sitio(site_id: int):
    """Obtiene el estado de conservación de un sitio histórico.

    :param site_id: identificador único del sitio.
    :return: un JSON con el estado del sitio o un mensaje de error si no se encuentra.
    """
    try:
        site_repo = get_site_repo()
        site = site_repo.get(site_id)
        if site:
            return jsonify({"estado": site.estado})
        return jsonify({"error": "Sitio no encontrado"}), 404
    except:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/estado_sitio"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return jsonify({"error": msj}), 500


@sites_bp.route("/historial_general", methods=["GET"])
@login_requerido
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def historial_general():
    """
    Muestra la vista principal del historial general de todos los sitios
    y maneja la aplicación de todos los filtros.
    """
    page = request.args.get("page", 1, type=int)

    filtros = {
        "site_nombre": request.args.get("site_nombre", type=str),
        "user_email": request.args.get("user_email", type=str),
        "accion_desc": request.args.get("accion", type=str),
        "page": page,
    }

    fecha_inicio_str = request.args.get("fecha_inicio")
    fecha_fin_str = request.args.get("fecha_fin")

    try:
        if fecha_inicio_str:
            filtros["fecha_inicio"] = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        if fecha_fin_str:
            fecha_fin_dt = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
            filtros["fecha_fin"] = fecha_fin_dt.replace(hour=23, minute=59, second=59)

    except ValueError:
        msj = "Formato de fecha inválido."
        endpoint = "/sitios/historial_general"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        filtros.pop("fecha_inicio", None)
        filtros.pop("fecha_fin", None)
        return flash(msj, "error")

    try:
        historial_data, pagination = historial.listar_historial_general(
            site_nombre=filtros.get("site_nombre"),
            user_email=filtros.get("user_email"),
            accion_desc=filtros.get("accion_desc"),
            fecha_inicio=filtros.get("fecha_inicio"),
            fecha_fin=filtros.get("fecha_fin"),
            page=filtros.get("page", 1),
        )
        acciones = historial.listar_acciones()

        return render_template(
            "historial_general.html",
            historial=[h.to_dict() for h in historial_data],
            pagination=pagination,
            acciones=acciones,
            current_filtros=(request.args.to_dict(flat=True) if request.args else {}),
            endpoint="sites.historial_general",
        )

    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/historial_general"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        flash(msj, "error")
        return (
            render_template(
                "historial_general.html",
                historial=[],
                pagination={
                    "page": 1,
                    "total_pages": 1,
                    "has_prev": False,
                    "has_next": False,
                    "total": 0,
                },
                acciones=[],
                current_filtros=(
                    request.args.to_dict(flat=True) if request.args else {}
                ),
                endpoint="sites.historial_general",
            ),
            500,
        )


@sites_bp.route("/exportar", methods=["POST"])
@permiso_requerido([PERMISO_SITIOS_LISTAR])
def exportar_sitios():
    """Exporta los sitios históricos filtrados a un archivo CSV descargable."""
    try:
        site_repo = get_site_repo()
        data = request.get_json() or {}
        filtros = data.get("filtros", {})
        orden = data.get("order", "fecha_desc")

        fecha_desde = filtros.get("fecha_desde")
        fecha_hasta = filtros.get("fecha_hasta")
        try:
            if fecha_desde:
                f_desde = datetime.combine(
                    datetime.strptime(fecha_desde, "%Y-%m-%d"), time.min
                )
                filtros["fecha_desde"] = f_desde.isoformat()

            if fecha_hasta:
                f_hasta = datetime.combine(
                    datetime.strptime(fecha_hasta, "%Y-%m-%d"), time.max
                )
                filtros["fecha_hasta"] = f_hasta.isoformat()

            if fecha_desde and fecha_hasta and f_desde > f_hasta:
                msj = "Rango de fechas inválido."
                endpoint = "/sitios/exportar"
                current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
                return jsonify({"error": msj}), 400
        except ValueError:
            msj = "Formato de fecha inválido."
            endpoint = "/sitios/exportar"
            current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
            return jsonify({"error": msj}), 400

        sitios = site_repo.listar_para_exportar(filtros, orden)

        if not sitios:
            return jsonify({"error": "No hay datos para exportar."}), 404

        data, headers = obtener_data_headers_sitios(sitios)
        filename, csv_bytes = generar_csv(data, headers, prefijo_archivo="sitios")

        return send_file(
            BytesIO(csv_bytes),
            mimetype="text/csv; charset=utf-8",
            as_attachment=True,
            download_name=filename,
        )
    except Exception:
        msj = "Ocurrio un error inesperado."
        endpoint = "/sitios/exportar"
        current_app.logger.exception(f"Mensaje: {msj}, Endpoint: {endpoint}")
        return jsonify({"error": msj}), 500


@sites_bp.route("/<int:site_id>/imagenes/<int:image_id>", methods=["DELETE"])
@login_requerido
@permiso_requerido([PERMISO_SITIOS_ACTUALIZAR])
def delete_image_from_site(site_id, image_id):
    """
    Elimina una imagen de un sitio específico.
    Valida que la imagen pertenezca al sitio para mayor seguridad.
    """
    try:
        site_repo = get_site_repo()
        user_id = get_user_id_from_session()

        imagen = sitios_historicos.obtener_imagen_por_id(image_id)

        if not imagen:
            return jsonify({"error": "Imagen no encontrada"}), 404

        if imagen.id_sitio_historico != site_id:
            current_app.logger.warning(
                f"Intento de eliminar imagen {image_id} que no pertenece al sitio {site_id}"
            )
            return (
                jsonify({"error": "La imagen no pertenece a este sitio"}),
                403,
            )

        site_repo.eliminar_imagen(image_id, user_id)
        return jsonify({"message": "Imagen eliminada"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(
            f"Error al eliminar imagen {image_id} del sitio {site_id}: {e}"
        )
        return jsonify({"error": "Error interno del servidor"}), 500


@sites_bp.route("/imagenes/upload_temporal", methods=["POST"])
@login_requerido
@permiso_requerido([PERMISO_SITIOS_CREAR, PERMISO_SITIOS_ACTUALIZAR])
def upload_image_temporal():
    """
    Sube un archivo a MinIO temporalmente (carpeta temp/) sin guardarlo en la DB.
    Devuelve la info necesaria para que el formulario 'crear' la adjunte.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No se encontró el archivo 'file'."}), 400

        file = request.files["file"]
        site_repo = get_site_repo()
        result = site_repo.upload_imagen_temporal(file)

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error en upload_temporal: {e}")
        return (
            jsonify({"error": "Error interno al subir archivo temporal."}),
            500,
        )


@sites_bp.route("/imagenes/delete_temporal", methods=["POST"])
@login_requerido
@permiso_requerido([PERMISO_SITIOS_CREAR, PERMISO_SITIOS_ACTUALIZAR])
def delete_image_temporal():
    """
    Elimina un archivo de MinIO que fue subido temporalmente
    (antes de que el sitio sea creado).
    """
    try:
        data = request.get_json()
        object_name = data.get("object_name_minio")

        site_repo = get_site_repo()
        site_repo.delete_temporal_image(object_name)
        return jsonify({"message": "Archivo temporal eliminado."}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        current_app.logger.error(f"Error en delete_temporal: {e}")
        return (
            jsonify({"error": "Error interno al eliminar archivo temporal."}),
            500,
        )
