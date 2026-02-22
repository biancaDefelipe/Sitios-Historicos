"""Utilidades para validación y conversión de fechas.

Provee funciones para validar rangos de fechas y convertir strings a datetime.date.
"""

from datetime import datetime
from typing import Optional


FORMATO_MAP = {"YYYY-MM-DD": "%Y-%m-%d", "DD-MM-YYYY": "%d-%m-%Y"}


def validar_fechas(
    fecha_desde: Optional[str],
    fecha_hasta: Optional[str] = None,
    formato: str = "YYYY-MM-DD",
) -> bool:
    """Valida si una fecha individual o un rango de fechas son válidos.

    :param fecha_desde: Fecha de inicio (obligatoria).
    :param fecha_hasta: Fecha de fin (opcional).
    :param formato: El formato esperado (default YYYY-MM-DD).
    :return: True si las fechas son válidas; False en caso contrario.
    """
    try:
        date_desde = (
            convertir_a_datetime_date(fecha_desde, formato) if fecha_desde else None
        )
        date_hasta = (
            convertir_a_datetime_date(fecha_hasta, formato) if fecha_hasta else None
        )

        if date_desde and date_hasta and date_hasta < date_desde:
            return False
    except ValueError:
        return False

    return True


def convertir_a_datetime_date(fecha: str, formato: str = "YYYY-MM-DD") -> datetime.date:
    """Convierte una fecha de string a datetime.date según el formato dado.

    :param fecha: La fecha a convertir.
    :param formato: El formato de fecha a convertir (default YYYY-MM-DD).
    :return: La fecha convertida a datetime.date
    :raises ValueError: Si el formato no es soportado o la fecha es inválida.
    """
    fmt = FORMATO_MAP.get(formato)
    if not fmt:
        raise ValueError(f"Formato no soportado: {formato}")
    return datetime.strptime(fecha, fmt).date()
