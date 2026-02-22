"""
Módulo de Utilidades para el Almacenamiento de Archivos en MinIO.

Este módulo centraliza toda la lógica para interactuar con el servidor de
almacenamiento de objetos MinIO. Su propósito es abstraer las operaciones
de subida, borrado y generación de URLs, proveyendo una interfaz simple
y consistente para el resto de la aplicación.

Funcionalidades Principales:
---------------------------
- `upload_file_to_minio`: Sube un archivo (proveniente de un formulario de Flask)
  a MinIO. Se encarga de generar un nombre de archivo único y seguro,
  organizarlo en una estructura de carpetas por sitio (`sitios/<id_sitio>/...`),
  y devolver tanto la URL pública permanente como el nombre del objeto (ruta).

- `delete_file_from_minio`: Elimina un archivo de MinIO. Es lo suficientemente
  flexible para aceptar tanto una URL completa como el nombre del objeto directo,
  facilitando su uso desde diferentes partes del sistema.

- `generate_safe_filename`: Función auxiliar interna que crea una ruta de
  objeto única y segura para evitar colisiones de nombres y problemas de
  seguridad.
"""

import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from minio.commonconfig import CopySource


def generate_safe_filename(original_filename: str, site_id: int = None) -> str:
    """
    Toma un nombre de archivo original (ej: "Mi Foto.jpg") y devuelve
    un nombre único y seguro (ej: "a1b2c3d4-uuid.jpg") para evitar
    colisiones en el bucket de MinIO.

    :param original_filename: Nombre original del archivo
    :param site_id: ID del sitio (None para archivos temporales)
    :return: Ruta completa del objeto en MinIO
    """
    filename = secure_filename(original_filename)

    extension = ""
    if "." in filename:
        extension = filename.rsplit(".", 1)[1].lower()

    unique_name = f"{uuid.uuid4()}.{extension}"

    if site_id is None:
        object_name = f"public/temp/{unique_name}"
    else:
        object_name = f"public/sitios/{site_id}/{unique_name}"

    return object_name


def upload_file_to_minio(file_storage, site_id: int = None):
    """
    Sube un objeto FileStorage de Flask a MinIO.

    :param file_storage: El objeto de archivo (ej: request.files['file'])
    :param site_id: ID del sitio (None para archivos temporales en carpeta temp/)
    :return: Una tupla (url_publica, object_name) del archivo subido.
    """

    minio_client = current_app.storage
    bucket_name = current_app.config["MINIO_BUCKET"]

    if not minio_client:
        current_app.logger.error(
            "Error grave: El cliente de MinIO (app.storage) no está inicializado."
        )
        raise ValueError("Error de configuración del servidor de almacenamiento.")

    object_name = generate_safe_filename(file_storage.filename, site_id)

    file_storage.seek(0, 2)
    file_size = file_storage.tell()
    file_storage.seek(0)

    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file_storage.stream,
            length=file_size,
            content_type=file_storage.mimetype,
        )

        endpoint = current_app.config["MINIO_SERVER"]
        protocol = "https" if current_app.config["MINIO_SECURE"] else "http"
        public_url = f"{protocol}://{endpoint}/{bucket_name}/{object_name}"

        return public_url, object_name

    except Exception as e:
        current_app.logger.error(f"Error al subir a MinIO: {e}")
        raise ValueError("No se pudo subir el archivo al servidor de almacenamiento.")


def delete_file_from_minio(file_identifier: str):
    """
    Elimina un objeto de MinIO.
    Acepta tanto una URL pública completa como un object_name directo.
    No lanza excepciones, solo las loguea.
    """
    minio_client = current_app.storage
    bucket_name = current_app.config["MINIO_BUCKET"]

    if not minio_client:
        current_app.logger.error(
            "Cliente de MinIO no inicializado, no se puede borrar el archivo."
        )
        return

    if not file_identifier:
        current_app.logger.error(
            "El identificador del archivo no puede ser nulo o vacío."
        )
        return

    object_name = ""

    try:
        if file_identifier.startswith(("http://", "https://")):
            path = urlparse(file_identifier).path
            object_name = path.replace(f"/{bucket_name}/", "", 1)
        else:
            object_name = file_identifier

        if not object_name:
            current_app.logger.error(
                "Identificador de archivo inválido después del parsing."
            )
            return

        minio_client.remove_object(bucket_name, object_name)
    except Exception as e:
        current_app.logger.error(f"Error al borrar '{object_name}' de MinIO: {e}")


def move_file_from_temp_to_site(temp_object_name: str, site_id: int) -> tuple[str, str]:
    """
    Mueve un archivo de la carpeta temporal a la carpeta del sitio.

    :param temp_object_name: Nombre del objeto temporal (ej: "temp/uuid.jpg")
    :param site_id: ID del sitio al que pertenecerá la imagen
    :return: Tupla (nueva_url_publica, nuevo_object_name)
    """
    minio_client = current_app.storage
    bucket_name = current_app.config["MINIO_BUCKET"]

    if not minio_client:
        raise ValueError("Cliente de MinIO no inicializado.")

    if not temp_object_name.startswith("public/temp/"):
        raise ValueError(
            f"El objeto '{temp_object_name}' no está en la carpeta temporal."
        )

    try:
        filename = temp_object_name.replace("public/temp/", "", 1)

        new_object_name = f"public/sitios/{site_id}/{filename}"

        copy_source = CopySource(bucket_name, temp_object_name)

        minio_client.copy_object(
            bucket_name=bucket_name,
            object_name=new_object_name,
            source=copy_source,
        )

        minio_client.remove_object(bucket_name, temp_object_name)

        endpoint = current_app.config["MINIO_SERVER"]
        protocol = "https" if current_app.config["MINIO_SECURE"] else "http"
        new_public_url = f"{protocol}://{endpoint}/{bucket_name}/{new_object_name}"

        return new_public_url, new_object_name

    except Exception as e:
        current_app.logger.error(
            f"Error al mover archivo de temp a sitio {site_id}: {e}"
        )
        raise ValueError("No se pudo mover el archivo temporal al sitio.")
