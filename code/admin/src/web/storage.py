"""
Módulo para la inicialización y gestión del cliente MinIO/S3.

Define la clase 'Storage' que actúa como una extensión de Flask para
configurar y conectar el cliente de almacenamiento S3 (MinIO) a la aplicación.
"""

from minio import Minio
from flask import Flask


class Storage:
    """
    Clase de extensión Flask para manejar la conexión con el servidor MinIO.

    Permite inicializar el cliente MinIO directamente o diferir la inicialización
    usando el patrón Application Factory a través del método `init_app`.
    """

    def __init__(self, app: Flask = None):
        """
        Inicializa la extensión Storage.

        :param app: Instancia opcional de Flask para la configuración inmediata.
        """
        self.client = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> Flask:
        """
        Configura la conexión con MinIO y adjunta el cliente a la aplicación Flask.

        Lee las configuraciones de MinIO (SERVER, ACCESS_KEY, SECRET_KEY, SECURE)
        desde `app.config`.

        :param app: Instancia de Flask a configurar.
        :returns: La instancia de Flask modificada.
        """
        self._client = Minio(
            app.config["MINIO_SERVER"],
            access_key=app.config["MINIO_ACCESS_KEY"],
            secret_key=app.config["MINIO_SECRET_KEY"],
            secure=app.config.get("MINIO_SECURE", False),
        )

        app.storage = self._client

        return app


storage = Storage()
