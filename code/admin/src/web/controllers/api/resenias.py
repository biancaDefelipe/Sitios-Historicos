"""
Módulo que define el blueprint y las rutas de la API para la gestión de reseñas (reviews)
asociadas a sitios históricos.

Implementa las operaciones CRUD para las reseñas, incluyendo la lista paginada,
creación, edición, eliminación y obtención de una reseña específica o la reseña
propia del usuario para un sitio. Incluye un decorador para verificar si la
funcionalidad de reseñas está activa y chequeos de mantenimiento.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from web.utils.mantenimiento_utils import (
    mantenimiento_portal_required,
    reviews_enabled_required,
)
from web.schemas.resenias import (
    ReviewSchema,
    ReviewCreateSchema,
    ReviewListQueryArgsSchema,
    ReviewIdPathSchema,
    ReviewEditSchema,
    ReviewDataSchema,
    UserReviewPathSchema,
    UserReviewSchema,
)
from core.api.resenias_api_core import (
    listar_resenias_de_sitio_api,
    crear_resenia_api,
    obtener_resenia_api,
    obtener_usuario_resenia_api,
    editar_resenia_api,
    eliminar_resenia_api,
)

reviews_api_blueprint = Blueprint(
    "reviews_api", __name__, url_prefix="/sites/<int:site_id>/reviews"
)
"""Blueprint para las rutas de reseñas bajo un sitio histórico."""


review_schema = ReviewSchema()
"""Esquema de Marshmallow para serializar una única reseña."""
reviews_schema = ReviewSchema(many=True)
"""Esquema de Marshmallow para serializar listas de reseñas."""
review_create_schema = ReviewCreateSchema()
"""Esquema de Marshmallow para validar la creación de una reseña."""
review_id_path_schema = ReviewIdPathSchema()
"""Esquema de Marshmallow para validar el ID de la reseña en la ruta."""
review_edit_schema = ReviewEditSchema()
"""Esquema de Marshmallow para validar la edición de una reseña."""
user_review_path_schema = UserReviewPathSchema()
"""Esquema de Marshmallow para validar el ID del sitio en la ruta de reseña de usuario."""
review_data_schema = ReviewDataSchema()
"""Esquema de Marshmallow para serializar datos de reseña de usuario con estado de eliminación."""
user_review_schema = UserReviewSchema()
"""Esquema de Marshmallow para serializar la reseña de un usuario específico."""


@reviews_api_blueprint.get("/")
@reviews_enabled_required
@mantenimiento_portal_required
def list_reviews(site_id):
    """
    GET /sites/{site_id}/reviews - Lista las reseñas de un sitio histórico con paginación.

    Acepta parámetros de paginación (`page`, `per_page`) en los argumentos de consulta.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        tuple[dict, int]: Respuesta JSON con la lista de reseñas y metadata de paginación (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError por datos de entrada inválidos).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si el sitio no existe).
    """
    try:
        review_list_query_args_schema = ReviewListQueryArgsSchema()
        review_list_query_args_schema.context = {"ordering_enabled": False}
        args = review_list_query_args_schema.load(request.args)
        page = args["page"]
        per_page = args["per_page"]

        items, pagination = listar_resenias_de_sitio_api(site_id, page, per_page)

        return (
            jsonify(
                {
                    "data": reviews_schema.dump(items),
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

    except ValueError as e:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )


@reviews_api_blueprint.post("/")
@reviews_enabled_required
@jwt_required()
@mantenimiento_portal_required
def create_review(site_id):
    """
    POST /sites/{site_id}/reviews - Crea una nueva reseña para el sitio.

    Requiere autenticación JWT y que las reseñas estén habilitadas.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        tuple[dict, int]: Respuesta JSON con la reseña creada (HTTP 201).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError o ID de sitio en cuerpo no coincide).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si el sitio no existe o error en servicio).
        tuple[dict, int]: Respuesta JSON de error con código 401 (si falta JWT).
    """
    try:
        data = review_create_schema.load(request.get_json())

        if data["id_sitio_historico"] != site_id:
            raise ValueError("Site ID in URL does not match site ID in body.")

        user_id = get_jwt_identity()
        new_review = crear_resenia_api(data, user_id, site_id)

        return jsonify(review_schema.dump(new_review)), 201

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


@reviews_api_blueprint.put("/<int:review_id>")
@reviews_enabled_required
@jwt_required()
@mantenimiento_portal_required
def edit_review(site_id, review_id):
    """
    PUT /sites/{site_id}/reviews/{review_id} - Edita una reseña propia existente.

    Requiere autenticación JWT y verifica que el usuario sea el autor de la reseña.

    Args:
        site_id (int): ID del sitio histórico.
        review_id (int): ID de la reseña a editar.

    Returns:
        tuple[dict, int]: Respuesta JSON con la reseña actualizada (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si la reseña/sitio no existe).
        tuple[dict, int]: Respuesta JSON de error con código 403 (PermissionError si el usuario no es el autor).
    """
    try:
        data = review_edit_schema.load(request.get_json())

        user_id = get_jwt_identity()
        updated_review = editar_resenia_api(review_id, data, user_id, site_id)
        return jsonify(review_schema.dump(updated_review)), 200

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

    except PermissionError as err:
        return (
            jsonify({"error": {"code": "forbidden", "message": str(err)}}),
            403,
        )

    except ValueError as err:
        return (
            jsonify({"error": {"code": "not_found", "message": str(err)}}),
            404,
        )


@reviews_api_blueprint.get("/user")
@reviews_enabled_required
@jwt_required()
@mantenimiento_portal_required
def get_user_review(site_id):
    """
    GET /sites/{site_id}/reviews/user - Obtiene la reseña propia del usuario autenticado para un sitio.

    Requiere autenticación JWT. Devuelve un objeto con la reseña y si está marcada como eliminada.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        tuple[dict, int]: Respuesta JSON con la reseña y el estado de eliminación (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError).
        tuple[dict, int]: Respuesta JSON de error con código 403 (PermissionError o reviews deshabilitadas).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si la reseña no existe).
    """
    try:
        user_review_path_schema.load({"site_id": site_id})
        user_id = get_jwt_identity()
        if not user_id:
            raise NoAuthorizationError("JWT missing or invalid")

        eliminada, review = obtener_usuario_resenia_api(site_id, user_id)
        return (
            jsonify(review_data_schema.dump({"deleted": eliminada, "review": review})),
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

    except PermissionError as err:
        return (
            jsonify({"error": {"code": "forbidden", "message": str(err)}}),
            403,
        )

    except ValueError:
        return (
            jsonify({"error": {"code": "not_found", "message": "Review not found"}}),
            404,
        )


@reviews_api_blueprint.get("/<int:review_id>")
@reviews_enabled_required
@jwt_required()
@mantenimiento_portal_required
def get_review(site_id, review_id):
    """
    GET /sites/{site_id}/reviews/{review_id} - Obtiene una reseña específica por su ID.

    Requiere autenticación JWT y que las reseñas estén habilitadas.

    Args:
        site_id (int): ID del sitio histórico.
        review_id (int): ID de la reseña a obtener.

    Returns:
        tuple[dict, int]: Respuesta JSON con la reseña (HTTP 200).
        tuple[dict, int]: Respuesta JSON de error con código 400 (ValidationError).
        tuple[dict, int]: Respuesta JSON de error con código 403 (PermissionError o reviews deshabilitadas).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si la reseña no existe o no pertenece al sitio).
    """
    try:
        review_id_path_schema.load({"review_id": review_id})
        review = obtener_resenia_api(review_id, site_id)
        return jsonify(review_schema.dump(review)), 200

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

    except PermissionError as err:
        return (
            jsonify({"error": {"code": "forbidden", "message": str(err)}}),
            403,
        )

    except ValueError:
        return (
            jsonify({"error": {"code": "not_found", "message": str(err)}}),
            404,
        )


@reviews_api_blueprint.delete("/<int:review_id>")
@reviews_enabled_required
@jwt_required()
@mantenimiento_portal_required
def delete_review(site_id, review_id):
    """
    DELETE /sites/{site_id}/reviews/{review_id} - Elimina (marca como eliminada) una reseña propia.

    Requiere autenticación JWT y verifica que el usuario sea el autor de la reseña.

    Args:
        site_id (int): ID del sitio histórico.
        review_id (int): ID de la reseña a eliminar.

    Returns:
        tuple[str, int]: Respuesta vacía (No Content) con código HTTP 204 en caso de éxito.
        tuple[dict, int]: Respuesta JSON de error con código 403 (PermissionError si el usuario no es el autor).
        tuple[dict, int]: Respuesta JSON de error con código 404 (ValueError si la reseña/sitio no existe).
        tuple[dict, int]: Respuesta JSON de error con código 401 (si falta JWT).
    """
    try:
        user_id = get_jwt_identity()
        if not isinstance(user_id, int) and user_id.isdigit():
            user_id = int(user_id)
        eliminar_resenia_api(review_id, user_id, site_id)
        return "", 204

    except PermissionError as err:
        return (
            jsonify({"error": {"code": "forbidden", "message": str(err)}}),
            403,
        )

    except ValueError as err:
        return (
            jsonify({"error": {"code": "not_found", "message": str(err)}}),
            404,
        )
