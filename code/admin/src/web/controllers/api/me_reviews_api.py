"""
Módulo que define el blueprint y las rutas de la API para el perfil de usuario autenticado ('/me').

Incluye endpoints para listar las reseñas y los sitios favoritos del usuario,
además de manejar la validación de autenticación JWT y el estado de mantenimiento del portal.
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from web.schemas.resenias import ReviewListQueryArgsSchema, UserReviewSchema
from core.api.me_reviews_api_core import listar_resenias_de_usuario_api
from core.api.favoritos_api_core import (
    listar_favoritos_usuario,
    validar_sitio_favorito,
)
from web.utils.mantenimiento_utils import (
    mantenimiento_portal_required,
    reviews_enabled_required,
)
from web.schemas.favorites import (
    FavoriteSiteSchema,
    FavoritesListQueryArgsSchema,
    SiteIsFavoriteSchema,
)

me_api = Blueprint("me_reviews_api", __name__, url_prefix="/me")
"""Blueprint para las rutas de usuario autenticado ('/me')."""


user_review_schema = UserReviewSchema(many=True)
"""Esquema de Marshmallow para serializar listas de reseñas de usuario."""
favorites_schema = FavoriteSiteSchema(many=True)
"""Esquema de Marshmallow para serializar listas de sitios favoritos."""
favorites_query_args_schema = FavoritesListQueryArgsSchema()
"""Esquema de Marshmallow para validar argumentos de consulta de favoritos."""
site_is_favorite_schema = SiteIsFavoriteSchema()
"""Esquema de Marshmallow para serializar la respuesta de si un sitio es favorito."""


@me_api.errorhandler(NoAuthorizationError)
def handle_missing_jwt(e):
    """
    Manejador de errores para cuando falta el token JWT o es inválido.

    Atrapa la excepción `NoAuthorizationError` de Flask-JWT-Extended.

    Args:
        e (NoAuthorizationError): La excepción generada por la falta de autorización.

    Returns:
        tuple[Response, int]: Respuesta JSON de error con código HTTP 401.
    """
    return (
        jsonify(
            {
                "error": {
                    "code": "unauthorized",
                    "message": "Authentication required",
                }
            }
        ),
        401,
    )


@me_api.route("/reviews", methods=["GET", "OPTIONS"])
@cross_origin(expose_headers=["X-Reviews-Enabled", "X-Maintenance-Mode"])
@jwt_required()
@reviews_enabled_required
@mantenimiento_portal_required
def get_my_reviews():
    """
    GET /api/me/reviews - Lista las reseñas del usuario autenticado con paginación.

    Soporta argumentos de consulta para paginación (`page`, `per_page`) y ordenamiento (`order`).
    Maneja la solicitud preflight OPTIONS para CORS.

    Returns:
        tuple[dict, int]: Respuesta JSON con la lista de reseñas y metadata de paginación (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError por datos de entrada inválidos).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError, ej. recurso no encontrado).
        tuple[dict, int]: Respuesta JSON de error con código 500 (Exception por error interno).
    """
    if request.method == "OPTIONS":
        return "", 200

    try:

        query_args_schema = ReviewListQueryArgsSchema()
        query_args_schema.context = {"ordering_enabled": True}
        args = query_args_schema.load(request.args)
        page = args["page"]
        per_page = args["per_page"]
        order = args.get("order", "desc")

        user_id = get_jwt_identity()
        if not user_id:
            raise NoAuthorizationError("JWT missing or invalid")

        items, pagination = listar_resenias_de_usuario_api(
            user_id=user_id, page=page, per_page=per_page, order=order
        )
        return (
            jsonify(
                {
                    "data": user_review_schema.dump(items),
                    "meta": {
                        "page": pagination["page"],
                        "per_page": pagination["per_page"],
                        "total": pagination["total"],
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
            jsonify({"error": {"code": "not_found", "message": str(err)}}),
            404,
        )


@me_api.get("/favorites")
@cross_origin(expose_headers=["X-Maintenance-Mode"])
@jwt_required()
@mantenimiento_portal_required
def get_my_favorites():
    """
    GET /api/me/favorites - Lista los sitios favoritos del usuario autenticado con paginación.

    Requiere autenticación JWT. Acepta parámetros de paginación en `request.args`.

    Returns:
        tuple[dict, int]: Respuesta JSON con la lista de sitios favoritos y metadata de paginación (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValueError por datos de consulta inválidos).
        tuple[dict, int]: Respuesta JSON de error con código 500 (Exception por error interno).
    """
    try:
        args = favorites_query_args_schema.load(request.args)

        user_id = int(get_jwt_identity())

        items, pagination_info = listar_favoritos_usuario(user_id, args)

        return (
            jsonify(
                {
                    "data": favorites_schema.dump(items),
                    "meta": {
                        "page": pagination_info["page"],
                        "per_page": pagination_info["per_page"],
                        "total": pagination_info["total"],
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Datos de consulta inválidos.",
                        "details": {"query_params": [str(e)]},
                    }
                }
            ),
            400,
        )


@me_api.get("/site_is_favorite/<int:site_id>")
@cross_origin(expose_headers=["X-Maintenance-Mode"])
@jwt_required()
@mantenimiento_portal_required
def site_is_favorite(site_id: int):
    """
    Verifica si un sitio esta marcado como favorito para un usuario autenticado.
    """
    try:
        user_id = int(get_jwt_identity())

        site, site_is_favorite = validar_sitio_favorito(user_id, site_id)

        response = {"site": site, "site_is_favorite": site_is_favorite}

        return (jsonify(site_is_favorite_schema.dump(response)), 200)

    except ValueError as e:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Datos de consulta inválidos.",
                        "details": {"query_params": [str(e)]},
                    }
                }
            ),
            400,
        )
