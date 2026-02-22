"""
Módulo principal de la API.

Este módulo inicializa el Blueprint principal de la API ('/api') y registra
todos los sub-blueprints (auth, sites, reviews, etc.). También define los
manejadores de errores globales para asegurar que todas las excepciones
dentro de la API devuelvan respuestas en formato JSON estandarizado.
"""

from flask import Blueprint, jsonify
from .auth import auth_api_blueprint
from .sites import sites_api_blueprint
from .resenias import reviews_api_blueprint
from .favoritos import favoritos_api_blueprint
from .me_reviews_api import me_api
from .config import config_api_blueprint

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

api_blueprint.register_blueprint(auth_api_blueprint)
api_blueprint.register_blueprint(sites_api_blueprint)
api_blueprint.register_blueprint(reviews_api_blueprint)
api_blueprint.register_blueprint(favoritos_api_blueprint)
api_blueprint.register_blueprint(me_api)
api_blueprint.register_blueprint(config_api_blueprint)


@api_blueprint.errorhandler(400)
def bad_request_error(e):
    """Manejador genérico de 400 Bad Request para la API."""
    return (
        jsonify(
            {
                "error": {
                    "code": "bad_request",
                    "message": "La solicitud es inválida.",
                }
            }
        ),
        400,
    )


@api_blueprint.errorhandler(403)
def forbidden_error(e):
    """Manejador genérico de 403 Forbidden para la API."""
    return (
        jsonify(
            {
                "error": {
                    "code": "forbidden",
                    "message": "No tienes permiso para realizar esta acción.",
                }
            }
        ),
        403,
    )


@api_blueprint.errorhandler(404)
def not_found_error(e):
    """Manejador genérico de 404 Not Found para la API."""
    return (
        jsonify(
            {
                "error": {
                    "code": "not_found",
                    "message": "El recurso solicitado no fue encontrado.",
                }
            }
        ),
        404,
    )


@api_blueprint.errorhandler(500)
def internal_server_error(e):
    """Manejador genérico de 500 Internal Server Error para la API."""
    return (
        jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ),
        500,
    )
