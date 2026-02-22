"""Modulo para validaciones de imágenes de sitios históricos"""

from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_IMAGES_PER_SITE = 10


def is_allowed_format(filename: str) -> bool:
    """Verifica si la extensión del archivo está en la lista de permitidas."""
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def validate_image_file(file_storage: FileStorage):
    """
    Funcion principal: ejecuta todas las validaciones sobre un objeto FileStorage.
    - no vacio
    - formato permitido
    - tamaño permitido
    Lanza un `ValueError` si alguna validación falla.
    """

    if not file_storage:
        raise ValueError("No se recibió ningún archivo (file_storage is None).")

    if not file_storage.filename:
        raise ValueError("El archivo no tiene nombre.")

    if not is_allowed_format(file_storage.filename):
        raise ValueError(
            f"Formato no permitido. Solo se aceptan: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if file_storage.content_length > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE_MB} MB."
        )

    file_storage.seek(0)


def validate_images_count(imagenes_data: list):
    """
    Valida que el número de imágenes no exceda el límite permitido.

    Función reutilizable tanto para crear como editar sitios.

    :param imagenes_data: Lista de diccionarios con datos de imágenes
    :raises ValueError: Si se excede el límite de imágenes
    """
    if not imagenes_data:
        return

    if len(imagenes_data) > MAX_IMAGES_PER_SITE:
        raise ValueError(
            f"No se pueden tener más de {MAX_IMAGES_PER_SITE} imágenes por sitio. "
            f"Actualmente tienes {len(imagenes_data)} imágenes."
        )
