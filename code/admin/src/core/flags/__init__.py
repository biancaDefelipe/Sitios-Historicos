"""Módulo de gestión de Feature Flags.

Este módulo provee funciones para:
- Obtener y verificar estados de feature flags
- Actualizar flags con auditoría de cambios
- Crear feature flags iniciales del sistema
- Consultar última modificación de flags
"""

from core.database import db
from core.flags.feature_flag import FeatureFlag
from core.flags.feature_flag_usuario import FeatureFlagUsuario
from datetime import datetime, timezone

CONST_MODO_MANTENIMIENTO = "modo_mantenimiento"


def obtener_feature_flag(nombre: str) -> FeatureFlag | None:
    """
    Obtiene un feature flag por su nombre.

    :param nombre: Nombre del feature flag.
    :return: Objeto FeatureFlag o None si no existe.
    """
    return db.session.query(FeatureFlag).filter_by(nombre=nombre).first()


def esta_activo(nombre: str) -> bool:
    """
    Verifica si un feature flag está activo.

    :param nombre: Nombre del feature flag.
    :return: True si está activo, False si no existe o está inactivo.
    """
    flag = obtener_feature_flag(nombre)
    return flag.estado if flag else False


def obtener_mensaje_mantenimiento(nombre: str) -> str:
    """
    Obtiene el mensaje de mantenimiento de un feature flag si está activo.

    :param nombre: Nombre del feature flag.
    :return: Mensaje de mantenimiento o cadena vacía si no está activo o no existe.
    """
    flag = obtener_feature_flag(nombre)
    return flag.mensaje_mantenimiento if flag and flag.estado else ""


def listar_feature_flags() -> list[FeatureFlag]:
    """
    Lista todos los feature flags existentes.

    :return: Lista de objetos FeatureFlag.
    """
    return db.session.query(FeatureFlag).order_by(FeatureFlag.id_flag).all()


def obtener_nombres_feature_flags_mantenimiento() -> list[str]:
    """
    Obtiene los nombres de los feature flags relacionados con modo mantenimiento.

    :return: Nombres de feature flags relacionados con modo mantenimiento.
    """
    return [
        nombre
        for (nombre,) in db.session.query(FeatureFlag.nombre)
        .filter(FeatureFlag.nombre.ilike(f"%{CONST_MODO_MANTENIMIENTO}%"))
        .all()
    ]


def obtener_ultima_modificacion(id_flag: int) -> FeatureFlagUsuario | None:
    """
    Obtiene la última modificación realizada sobre un feature flag.

    :param id_flag: ID del feature flag.
    :return: Objeto FeatureFlagUsuario o None si no hay modificaciones.
    """
    return (
        db.session.query(FeatureFlagUsuario)
        .filter_by(id_flag=id_flag)
        .order_by(FeatureFlagUsuario.fecha_hora_modificacion.desc())
        .first()
    )


def actualizar_feature_flag(
    nombre: str, estado: bool, mensaje_mantenimiento: str, id_usuario: int
) -> bool:
    """
    Actualiza el estado y mensaje de mantenimiento de un feature flag.

    :return: True si se actualizó correctamente, False si no hubo cambios.
    :raises ValueError: Si el flag no existe o los datos no son válidos.
    """
    flag = obtener_feature_flag(nombre)
    if not flag:
        raise ValueError(f"Feature flag con nombre {nombre} no encontrado")

    # Si el estado no cambió o el mensaje no cambió, entonces no hubo cambios
    if flag.estado == estado and flag.mensaje_mantenimiento == mensaje_mantenimiento:
        return False

    flag.estado = estado
    if nombre in obtener_nombres_feature_flags_mantenimiento():
        flag.mensaje_mantenimiento = mensaje_mantenimiento

    auditoria = FeatureFlagUsuario(
        fecha_hora_modificacion=datetime.now(timezone.utc),
        id_flag=flag.id_flag,
        id_usuario=id_usuario,
    )

    db.session.add(auditoria)
    db.session.commit()
    return True


def crear_feature_flags_iniciales() -> None:
    """
    Crea los feature flags iniciales si no existen en la base de datos.

    - Si el flag no existe, lo agrega a la base de datos.
    - Si ya existe, lo omite.
    - Al finalizar, imprime cuántos flags fueron creados o si ya existían todos.

    :return: None
    """
    flags_iniciales = [
        {
            "nombre": "modo_mantenimiento_admin",
            "descripcion": "Modo mantenimiento de administración - Deshabilita temporalmente el sitio de administración",
            "mensaje_mantenimiento": "El sistema está en mantenimiento. Solo System Admins pueden acceder.",
            "estado": False,
        },
        {
            "nombre": "modo_mantenimiento_portal_publico",
            "descripcion": "Modo mantenimiento de portal web - Deshabilita temporalmente el portal público",
            "mensaje_mantenimiento": "Portal en mantenimiento programado. Disculpe las molestias.",
            "estado": False,
        },
        {
            "nombre": "reviews_habilitadas",
            "descripcion": "Permitir nuevas reseñas - Habilita/deshabilita creación y visualización de reseñas",
            "mensaje_mantenimiento": "Se encuentran deshabilitadas las reseñas. Sistema en mantenimiento.",
            "estado": True,
        },
    ]

    flags_creados = 0
    for flag_data in flags_iniciales:
        if not obtener_feature_flag(flag_data["nombre"]):

            flag = FeatureFlag(
                nombre=flag_data["nombre"],
                descripcion=flag_data["descripcion"],
                mensaje_mantenimiento=flag_data["mensaje_mantenimiento"],
                estado=flag_data["estado"],
            )
            db.session.add(flag)
            flags_creados += 1

    if flags_creados > 0:
        db.session.commit()
