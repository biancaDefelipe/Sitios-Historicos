"""
Módulo que define el blueprint y las rutas de la API para gestionar los favoritos de los usuarios.

Permite a los usuarios autenticados marcar y desmarcar sitios como favoritos.
También incluye un manejador de errores para la falta de autenticación JWT y un chequeo
de mantenimiento global del portal público.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError

from core.api.favoritos_api_core import (
    marcar_favorito,
    desmarcar_favorito,
)
from web.schemas.site import SiteSchema, SiteIdPathSchema
from web.utils.mantenimiento_utils import mantenimiento_portal_required

favoritos_api_blueprint = Blueprint("favoritos_api", __name__)
"""Blueprint para las rutas de gestión de favoritos de la API."""


sites_schema = SiteSchema(many=True)
"""Esquema de Marshmallow para la serialización de listas de sitios."""

site_id_path_schema = SiteIdPathSchema()
""" Esquema de Marshmallow para validar el ID del sitio."""


@favoritos_api_blueprint.errorhandler(NoAuthorizationError)
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


@favoritos_api_blueprint.put("/sites/<int:site_id>/favorite")
@jwt_required()
@mantenimiento_portal_required
def put_favorite(site_id):
    """
    PUT /api/sites/{site_id}/favorite - Marca un sitio como favorito para el usuario autenticado.

    Requiere autenticación JWT.

    Args:
        site_id (int): El ID del sitio a marcar como favorito.

    Returns:
        tuple[str, int]: Respuesta vacía (No Content) con código HTTP 204 en caso de éxito.
        tuple[dict, int]: Respuesta JSON de error con código 404 si el sitio no existe (ValueError).
        tuple[dict, int]: Respuesta JSON de error con código 500 en caso de error interno.
    """
    try:
        site_id_path_schema.load({"site_id": site_id})
        user_id = int(get_jwt_identity())
        marcar_favorito(user_id, site_id)
        return "", 204

    except ValidationError as e:
        return (
            jsonify({"error": {"code": "bad_request", "message": e.messages}}),
            400,
        )

    except ValueError as e:
        return (
            jsonify({"error": {"code": "not_found", "message": str(e)}}),
            404,
        )


@favoritos_api_blueprint.delete("/sites/<int:site_id>/favorite")
@jwt_required()
@mantenimiento_portal_required
def delete_favorite(site_id):
    """
    DELETE /api/sites/{site_id}/favorite - Desmarca un sitio como favorito para el usuario autenticado.

    Requiere autenticación JWT. Si el sitio no era favorito, la operación se considera exitosa.

    Args:
        site_id (int): El ID del sitio a desmarcar.

    Returns:
        tuple[str, int]: Respuesta vacía (No Content) con código HTTP 204 en caso de éxito.
        tuple[dict, int]: Respuesta JSON de error con código 404 si el sitio no existe (ValueError).
        tuple[dict, int]: Respuesta JSON de error con código 500 en caso de error interno.
    """
    try:
        site_id_path_schema.load({"site_id": site_id})
        user_id = int(get_jwt_identity())
        desmarcar_favorito(user_id, site_id)
        return "", 204

    except ValidationError as e:
        return (
            jsonify({"error": {"code": "bad_request", "message": e.messages}}),
            400,
        )

    except ValueError as e:
        return (
            jsonify({"error": {"code": "not_found", "message": str(e)}}),
            404,
        )
