"""Configuración y utilidades de base de datos para la app Flask.

Este módulo centraliza la inicialización de SQLAlchemy y expone utilidades para
importar los modelos y reiniciar el esquema de la base de datos en entornos de
desarrollo.

Las docstrings siguen una convención en español para mantener la consistencia
del proyecto.
"""

from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()


def init_app(app):
    """Inicializa SQLAlchemy y lo vincula con la aplicación Flask.

    Args:
        app: Instancia de la aplicación Flask.

    Returns:
        SQLAlchemy: Instancia configurada del objeto SQLAlchemy.
    """
    db.init_app(app)
    return db


modelos_cargados = False


def importar_modelos():
    """Importa todos los módulos de modelos para registrarlos en SQLAlchemy.

    Esta función debe ejecutarse antes de realizar operaciones con el metadata
    (por ejemplo, ``create_all`` o ``drop_all``), para asegurar que todas las
    tablas estén definidas.
    """
    global modelos_cargados
    if modelos_cargados:
        return

    modelos_cargados = True


def reset_db():
    """Elimina y vuelve a crear todas las tablas de la base de datos.

    Advertencia:
        Usar únicamente en desarrollo o pruebas. Esta acción borra todos los
        datos existentes.
    """
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)


class Base(DeclarativeBase):
    """Clase base para todos los modelos de SQLAlchemy del proyecto."""

    __abstract__ = True
    __table_args__ = {"extend_existing": True}
