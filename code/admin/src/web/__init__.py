"""Módulo principal de la aplicación web Flask.
Este módulo crea y configura la aplicación Flask, inicializa las extensiones,
registra los blueprints y define los manejadores de errores globales.
"""

from flask import Flask, render_template, jsonify
from core import database
from web.config import config, cache_init_app, session_init_app
from web.storage import storage
from web.handlers import HttpError
from .controllers.auth import auth_blueprint
from .controllers.feature_flags import feature_flags_blueprint
from .utils.auth_utils import _esta_autenticado, _es_admin
from .utils.auth_utils import obtener_de_session
from .utils.mantenimiento_utils import mantenimiento_admin
import logging
from flask_jwt_extended import JWTManager
from web.controllers.api import api_blueprint
from flask_cors import CORS
from web.controllers.sites_controllers import sites_bp as sites_blueprint

from web.controllers.tags_controller import bp as tags_blueprint
from web.controllers.resenias_controller import bp as resenias_blueprint


CLAVE_USUARIO_ID = "id"
CLAVE_USUARIO_EMAIL = "email"


def create_app(env="development", static_folder="../../static"):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    database.init_app(app)
    database.importar_modelos()

    cache_init_app(app)
    session_init_app(app)
    storage.init_app(app)
    JWTManager(app)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", ["*"]),
                "supports_credentials": True,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "expose_headers": ["X-Maintenance-Mode", "X-Reviews-Enabled"],
            }
        },
    )

    app.url_map.strict_slashes = False
    app.url_map.redirect_defaults = False

    logging.basicConfig(level=app.config["LOG_LEVEL"], format=app.config["LOG_FORMAT"])

    @app.errorhandler(Exception)
    def capturar_excepcion_no_manejada(e):
        """Manejador global para excepciones no manejadas."""
        app.logger.exception("Ocurrió un error inesperado en la aplicación.")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Ocurrió un error inesperado en la aplicación.",
                }
            ),
            500,
        )

    app.before_request(mantenimiento_admin)
    database.importar_modelos()

    from core.sitios_repo.repo_sitios_historicos import SiteRepo

    with app.app_context():
        app.config["SITE_REPO"] = SiteRepo()

    @app.route("/")
    def home():
        """Ruta principal que muestra la página de bienvenida o mantenimiento."""
        id_user_dict = obtener_de_session([CLAVE_USUARIO_ID])
        email_dict = obtener_de_session([CLAVE_USUARIO_EMAIL])
        id_user = id_user_dict[CLAVE_USUARIO_ID]
        email = email_dict[CLAVE_USUARIO_EMAIL]
        if id_user and email:
            return render_template("bienvenida.html", email=email)
        else:
            return render_template("bienvenida.html", rol=None, nombre=None)

    app.register_blueprint(sites_blueprint)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(feature_flags_blueprint)
    app.register_blueprint(tags_blueprint)
    app.register_blueprint(resenias_blueprint)
    app.register_blueprint(api_blueprint)

    app.register_error_handler(400, HttpError.bad_request_error)
    app.register_error_handler(401, HttpError.unauthorized_error)
    app.register_error_handler(403, HttpError.forbidden_error)
    app.register_error_handler(404, HttpError.not_found_error)
    app.register_error_handler(500, HttpError.internal_server_error)

    app.jinja_env.globals.update(esta_autenticado=lambda: _esta_autenticado())
    app.jinja_env.globals.update(es_admin=lambda: _es_admin())

    @app.cli.command("reset-db")
    def reset_db():
        """Reinicia la base de datos eliminando todas las tablas y datos existentes."""
        database.importar_modelos()
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        """Carga datos iniciales (roles, usuarios de prueba, sitios) a la base de datos."""
        database.importar_modelos()

    return app
