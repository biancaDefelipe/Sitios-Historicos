"""Utilidades para el almacenamiento en caché de la aplicación web.

Este módulo proporciona funciones para almacenar, recuperar e invalidar entradas
de caché utilizando una convención de nombres consistente.
"""

from web.config import cache


def guardar_en_cache(nombre: str, datos: dict, timeout: int | None = None):
    """Almacena pares clave-valor en la caché con un prefijo especificado.

    :param nombre: Prefijo para la clave de caché.
    :param datos: Diccionario con los datos a almacenar.
    :param timeout: Tiempo de expiración en segundos (opcional).
    """
    for key, value in datos.items():
        cache_key = f"{nombre}:{key}"
        cache.set(cache_key, value, timeout=timeout)


def buscar_en_cache(nombre: str, clave: str):
    """Recupera un valor de la caché utilizando una clave específica.

    :param nombre: Prefijo para la clave de caché.
    :param clave: Clave del valor a recuperar.
    :return: El valor almacenado en caché, o None si no se encuentra.
    """
    cache_key = f"{nombre}:{clave}"
    return cache.get(cache_key)


def invalidar_de_cache(nombre: str, clave: str) -> bool:
    """Elimina una entrada de la caché utilizando una clave específica.

    :param nombre: Prefijo para la clave de caché.
    :param clave: Clave a eliminar de la caché.
    :return: True si la entrada fue eliminada exitosamente, False en caso contrario.
    """
    cache_key = f"{nombre}:{clave}"
    return cache.delete(cache_key)
