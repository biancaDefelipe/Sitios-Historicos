"""Validaciones para endpoints del controlador de etiquetas (tags).

Incluye reglas y sanitización para alta, edición y búsqueda de tags.
"""

from typing import Optional
from slugify import slugify


def validar_entero_positivo(valor, campo):
    """Valida que el valor sea un entero positivo."""
    try:
        val = int(valor)
    except Exception:
        raise ValueError(f"El parámetro '{campo}' debe ser un número entero.")
    if val <= 0:
        raise ValueError(f"El parámetro '{campo}' debe ser mayor que 0.")
    return val


def validar_listar_tags(q: Optional[str], order: str, page: int, per_page: int):
    """
    Valida parámetros usados en la vista / API de listado de tags.
    Lanza ValueError con mensaje amigable cuando falla.
    """
    if q is not None and len(q) > 200:
        raise ValueError(
            "El parámetro de búsqueda 'q' no puede superar 200 caracteres."
        )

    ordenes_validos = {"name_asc", "name_desc", "fecha_asc", "fecha_desc"}
    if order not in ordenes_validos:
        raise ValueError(
            f"El valor de 'order' ({order}) es inválido. Valores permitidos: name_asc, name_desc, fecha_asc, fecha_desc."
        )

    validar_entero_positivo(page, "page")
    if per_page is not None:
        if not isinstance(per_page, int):
            raise ValueError("El parámetro 'per_page' debe ser un número entero.")
        validar_entero_positivo(per_page, "per_page")


def validar_nombre_tag(data: dict, repo_func_existe):
    """
    Valida el nombre de un tag antes de crear.
    - Obligatorio, string, length 3..50 (trim).
    Lanza ValueError si invalido.
    """
    nombre = data.get("nombre")
    if nombre is None:
        raise ValueError("El nombre del tag es obligatorio.")

    if not isinstance(nombre, str):
        raise ValueError("El nombre del tag debe ser texto.")

    nombre_stripped = nombre.strip()
    if nombre_stripped == "":
        raise ValueError("El nombre del tag es obligatorio.")

    if len(nombre_stripped) < 3:
        raise ValueError("El nombre del tag debe tener al menos 3 caracteres.")

    if len(nombre_stripped) > 50:
        raise ValueError("El nombre del tag no puede superar los 50 caracteres.")

    if repo_func_existe(nombre, slugify(nombre.strip().lower())):
        raise ValueError(f"Ya existe un tag con el nombre o slug '{nombre}'.")


def validar_id_tag(tag_id):
    """
    Valida el id pasado para borrar un tag.
    Lanza ValueError si no es un entero positivo.
    """
    if tag_id is None:
        raise ValueError("El id del tag es obligatorio para eliminar.")
    validar_entero_positivo(tag_id, "tag_id")
