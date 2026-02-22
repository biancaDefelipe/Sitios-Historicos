"""Configuración de la aplicación Flask (desarrollo, producción y testing).

Expone helpers para inicializar extensiones (cache, session) y clases de
configuración por entorno.
"""

import logging
from os import environ
from datetime import timedelta
from dotenv import dotenv_values
from flask_caching import Cache
from flask_session import Session

cache = Cache()
session = Session()


def cache_init_app(app):
    """Inicializa la extensión de caché con la aplicación dada."""
    cache.init_app(app)
    return cache


def session_init_app(app):
    """Inicializa la extensión de sesión con la aplicación dada."""
    session.init_app(app)
    return session


class Config:
    """Configuración base compartida por todos los entornos."""

    TESTING = False
    SECRET_KEY = "secret-key"
    FLASK_SESSION_TYPE = "filesygit stem"
    CORS_ORIGINS = ["*"]
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }

    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = "./flask_cache"
    CACHE_DEFAULT_TIMEOUT = 7200

    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=120)

    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"

    JWT_SECRET_KEY = environ.get("JWT_SECRET_KEY", "secret-key")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


class ProductionConfig(Config):
    """Configuración para entorno de producción."""

    SQLALCHEMY_ENGINES = {"default": environ.get("DATABASE_URL")}
    CORS_ORIGINS = ["https://grupo02.proyecto2025.linti.unlp.edu.ar"]

    LOG_LEVEL = logging.INFO

    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = environ.get("MINIO_SECURE", "true").lower() == "true"
    MINIO_BUCKET = environ.get("MINIO_BUCKET", "grupo02")

    GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI = environ.get("GOOGLE_REDIRECT_URI")


class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""

    values = dotenv_values()

    DB_SCHEME = values.get("DB_SCHEME")
    DB_USER = values.get("DB_USER")
    DB_PASSWORD = values.get("DB_PASSWORD")
    DB_HOST = values.get("DB_HOST")
    DB_PORT = values.get("DB_PORT")
    DB_NAME = values.get("DB_NAME")

    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }

    LOG_LEVEL = logging.DEBUG

    MINIO_SERVER = values.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = values.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = values.get("MINIO_SECRET_KEY")
    MINIO_SECURE = False
    MINIO_BUCKET = values.get("MINIO_BUCKET")

    GOOGLE_CLIENT_SECRET = values.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_CLIENT_ID = values.get("GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI = values.get("GOOGLE_REDIRECT_URI")


class TestingConfig(Config):
    """Configuración para entorno de testing."""

    TESTING = True
    LOG_LEVEL = logging.CRITICAL


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
