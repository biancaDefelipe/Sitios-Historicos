"""
Módulo que define el blueprint y las rutas de la API para la gestión de sitios históricos.

Implementa endpoints para listar sitios con filtros, obtener un sitio por ID,
crear nuevos sitios (requiere autenticación JWT), y obtener listas de provincias
y tags disponibles. Incluye un chequeo de mantenimiento global y manejo de
autenticación opcional para listado de favoritos.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from core.api.sites_api_core import (
    listar_sitios_filtrados_api,
    crear_sitio_api,
    obtener_sitio_por_id,
)
from core.sitios_historicos import obtener_todos_los_tags
from core.localidad import obtener_provincias
from web.schemas.site import (
    SiteSchema,
    SiteCreateSchema,
    SiteListQueryArgsSchema,
)
from flask_cors import cross_origin
from web.utils.mantenimiento_utils import mantenimiento_portal_required

sites_api_blueprint = Blueprint("sites_api", __name__, url_prefix="/sites")
"""Blueprint para las rutas de sitios históricos de la API."""


site_schema = SiteSchema()
"""Esquema de Marshmallow para serializar un único sitio histórico."""
sites_schema = SiteSchema(many=True)
"""Esquema de Marshmallow para serializar listas de sitios históricos."""
site_create_schema = SiteCreateSchema()
"""Esquema de Marshmallow para validar la creación de un nuevo sitio."""
site_list_query_schema = SiteListQueryArgsSchema()
"""Esquema de Marshmallow para validar argumentos de consulta para listar sitios."""


@sites_api_blueprint.get("/")
@cross_origin()
@mantenimiento_portal_required
def list_sites():
    """
    GET /api/sites - Lista sitios históricos con filtros, paginación y ordenamiento.

    Maneja la autenticación JWT de forma opcional. Si se solicita filtrar por
    favoritos (`favorites=true`), se requiere autenticación.

    Returns:
        tuple[dict, int]: Respuesta JSON con la lista de sitios y metadata de paginación (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError por query params inválidos).
        tuple[dict, int]: Respuesta JSON de error con código 401 (si `favorites=true` sin JWT).
    """
    try:

        query_data = site_list_query_schema.load(request.args)

        user_id = None

        autenticado = None

        try:
            verify_jwt_in_request(optional=True)
            autenticado = True
        except Exception:
            autenticado = False

        if not autenticado and query_data.get("favorites"):
            raise NoAuthorizationError("JWT missing or invalid")

        user_id = get_jwt_identity() if autenticado else None

        items, pagination_info = listar_sitios_filtrados_api(query_data, user_id)
        return (
            jsonify(
                {
                    "data": sites_schema.dump(items),
                    "meta": {
                        "page": pagination_info["page"],
                        "per_page": pagination_info["per_page"],
                        "total": pagination_info["total"],
                    },
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": err.messages,
                    }
                }
            ),
            400,
        )

    except NoAuthorizationError:
        return (
            jsonify(
                {
                    "error": {
                        "code": "unauthorized",
                        "message": "Authentication required to filter favorites",
                    }
                }
            ),
            401,
        )


@sites_api_blueprint.get("/<int:site_id>")
@cross_origin()
@mantenimiento_portal_required
def get_site(site_id):
    """
    GET /api/sites/{site_id} - Obtiene un sitio histórico por su ID.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        tuple[dict, int]: Respuesta JSON con los detalles del sitio (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si el sitio no existe).
        tuple[dict, int]: Respuesta JSON de error con código 500 (Exception por error interno).
    """
    try:
        site_model = obtener_sitio_por_id(site_id)

        if not site_model:
            raise ValueError(f"Sitio con id {site_id} no encontrado.")

        result = site_schema.dump(site_model)
        return jsonify(result), 200

    except ValueError as e:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Site not found",
                    }
                }
            ),
            404,
        )


@sites_api_blueprint.post("/")
@jwt_required()
@mantenimiento_portal_required
def create_site():
    """
    POST /api/sites - Crea un nuevo sitio histórico.

    Requiere autenticación JWT. El usuario autenticado es el creador del sitio.

    Returns:
        tuple[dict, int]: Respuesta JSON con los datos del sitio creado (HTTP 201).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError o ValueError por reglas de negocio).
        tuple[dict, int]: Respuesta JSON de error con código 401 (si falta JWT).
    """
    try:
        data = site_create_schema.load(request.get_json())

        user_id = get_jwt_identity()
        new_site = crear_sitio_api(data, user_id)

        return jsonify(site_schema.dump(new_site)), 201

    except ValidationError as err:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": err.messages,
                    }
                }
            ),
            400,
        )
    except ValueError as err:
        return (
            jsonify(
                {
                    "error": {
                        "code": "business_logic_error",
                        "message": str(err),
                    }
                }
            ),
            400,
        )


@sites_api_blueprint.get("/provinces")
@cross_origin()
@mantenimiento_portal_required
def list_provinces():
    """
    GET /api/sites/provinces - Lista los nombres de las provincias disponibles.

    Returns:
        tuple[dict, int]: Respuesta JSON con la clave "provinces" conteniendo una lista de nombres (HTTP 200).
    """
    provinces = obtener_provincias()
    return jsonify({"provinces": [p.get("nombre") for p in provinces]}), 200


@sites_api_blueprint.get("/tags")
@cross_origin()
@mantenimiento_portal_required
def list_tags():
    """
    GET /api/sites/tags - Lista los nombres de los tags disponibles.

    Returns:
        tuple[dict, int]: Respuesta JSON con la clave "tags" conteniendo una lista de nombres (HTTP 200).
    """
    tags = obtener_todos_los_tags()
    return jsonify({"tags": [t.nombre for t in tags]}), 200
