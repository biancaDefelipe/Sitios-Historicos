"""Helpers para manejo de datos en la sesión de Flask.

Provee utilidades simples para guardar, obtener y limpiar claves en ``session``.
"""

from flask import session


def guardar_en_session(datos: dict):
    """Guarda múltiples pares clave/valor en la sesión.

    Args:
        datos: Diccionario con las claves y valores a persistir en sesión.
    """
    for key, value in datos.items():
        session[key] = value


def obtener_de_session(claves: list[str]):
    """Obtiene un subconjunto de claves desde la sesión.

    Args:
        claves: Lista de claves a recuperar.

    Returns:
        dict: Diccionario (clave -> valor) con los valores encontrados.
    """
    datos = {}
    for key in claves:
        datos[key] = session.get(key)
    return datos


def existe_en_session(clave: str) -> bool:
    """Verifica si una clave existe en la sesión."""
    return clave in session


def eliminar_de_session(claves: list[str]):
    """Elimina claves específicas de la sesión si existen.

    Args:
        claves: Lista de claves a remover.
    """
    for key in claves:
        session.pop(key, None)


def limpiar_session_all():
    """Limpia por completo la sesión actual."""
    session.clear()
