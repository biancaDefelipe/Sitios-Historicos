"""Validaciones para endpoints del controlador de feature flags.

Centraliza validaciones relacionadas a la gestión de Feature Flags.
"""

from core.flags import obtener_nombres_feature_flags_mantenimiento


ESTADOS_ESPERADOS = {"true": True, "false": False}


def validar_datos_actualizacion(
    estado_str: str, mensaje_mantenimiento: str, nombre: str
) -> None:
    """
    Valida los datos para actualizar un feature flag.

    :param estado: Nuevo estado del feature flag.
    :param mensaje_mantenimiento: Nuevo mensaje de mantenimiento.
    :param nombre: Nombre del feature flag.
    :raises ValueError: Si alguna validación falla.
    """
    if not isinstance(estado_str, str):
        raise ValueError("El estado debe ser una cadena de texto")
    if not isinstance(mensaje_mantenimiento, str):
        raise ValueError("El mensaje de mantenimiento debe ser una cadena de texto")
    if not isinstance(nombre, str):
        raise ValueError("El nombre del feature flag debe ser una cadena de texto")

    if estado_str.lower() not in ESTADOS_ESPERADOS.keys():
        raise ValueError("Estado inválido para el feature flag")

    if nombre in obtener_nombres_feature_flags_mantenimiento():
        if not mensaje_mantenimiento:
            raise ValueError(
                "El mensaje de mantenimiento es obligatorio para el modo mantenimiento"
            )

        mensaje_mantenimiento = (
            mensaje_mantenimiento.strip() if mensaje_mantenimiento else ""
        )

        if mensaje_mantenimiento.isspace():
            raise ValueError(
                "El mensaje de mantenimiento no puede estar vacío ni contener solo espacios en blanco"
            )

        if len(mensaje_mantenimiento) > 100:
            raise ValueError(
                "El mensaje de mantenimiento no puede exceder los 100 caracteres"
            )
