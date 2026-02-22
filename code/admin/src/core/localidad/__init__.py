"""Módulo de gestión de localidades.

Este módulo provee funciones para:
- Obtener y buscar provincias por nombre o ID
- Obtener y buscar ciudades por nombre o ID
- Crear nuevas ciudades
- Verificar existencia de ciudades en provincias
"""

from sqlite3 import IntegrityError
from core.database import db
from .provincia import Provincia
from .ciudad import Ciudad


def obtener_ciudad_id(nombre_ciudad: str, nombre_provincia: str) -> int | None:
    """Busca una Ciudad por su nombre y provincia, y devuelve su ID.

    :param nombre_ciudad: Nombre de la ciudad.
    :param nombre_provincia: Nombre de la provincia.
    :return: ID de la ciudad o None si no existe.
    """

    query = db.session.query(Ciudad).filter(Ciudad.nombre.ilike(nombre_ciudad.strip()))
    if nombre_provincia:
        query = query.join(Ciudad.provincia).filter(
            Provincia.nombre.ilike(nombre_provincia.strip())
        )
    ciudad = query.first()
    if ciudad:
        return ciudad.id_ciudad
    return None


def listar_provincias_nombres() -> list[str]:
    """Obtiene solo los nombres de todas las provincias.

    :return: Lista de strings con los nombres de las provincias.
    """

    provincias = (
        db.session.query(Provincia.nombre).order_by(Provincia.nombre.asc()).all()
    )
    return [p[0] for p in provincias]


def obtener_provincias() -> list[dict]:
    """Obtiene todas las provincias.

    :return: Lista de diccionarios con los datos de cada provincia.
    """

    provincias = db.session.query(Provincia).order_by(Provincia.nombre.asc()).all()
    return [{"id_provincia": p.id_provincia, "nombre": p.nombre} for p in provincias]


def obtener_provincia_id(nombre_provincia: str) -> int | None:
    """Busca una Provincia por su nombre y devuelve su ID.

    :param nombre_provincia: Nombre de la provincia.
    :return: ID de la provincia o None si no existe.
    """

    provincia = (
        db.session.query(Provincia)
        .filter(Provincia.nombre.ilike(nombre_provincia.strip()))
        .first()
    )
    return provincia.id_provincia if provincia else None


def obtener_provincia_nombre(provincia_id: int) -> str | None:
    """Busca una Provincia por su ID y devuelve su nombre.

    :param provincia_id: ID de la provincia.
    :return: Nombre de la provincia o None si no existe.
    """

    provincia = (
        db.session.query(Provincia)
        .filter(Provincia.id_provincia == provincia_id)
        .first()
    )

    return provincia.nombre if provincia else None


def obtener_ciudad_nombre(ciudad_id: int) -> str | None:
    """Busca una Ciudad por su ID y devuelve su nombre.

    :param ciudad_id: ID de la ciudad.
    :return: Nombre de la ciudad o None si no existe.
    """

    ciudad = db.session.query(Ciudad).filter(Ciudad.id_ciudad == ciudad_id).first()
    return ciudad.nombre if ciudad else None


def existe_ciudad_provincia(nombre_ciudad: str, nombre_provincia: str) -> int | None:
    """Verifica si una ciudad existe en una provincia dada.

    :param nombre_ciudad: Nombre de la ciudad.
    :param nombre_provincia: Nombre de la provincia.
    :return: ID de la ciudad o None si no existe.
    """
    ciudad = (
        db.session.query(Ciudad)
        .join(Ciudad.provincia)
        .filter(
            Ciudad.nombre.ilike(nombre_ciudad.strip()),
            Provincia.nombre.ilike(nombre_provincia.strip()),
        )
        .first()
    )
    if ciudad:
        return ciudad.id_ciudad
    else:
        return None


def crear_ciudad(nombre_ciudad: str, provincia_id: int, commit: bool) -> int:
    """Crea una nueva ciudad en la provincia especificada y devuelve su ID.

    :param nombre_ciudad: Nombre de la ciudad.
    :param provincia_id: ID de la provincia.
    :param commit: Si True, hace commit; si False, solo flush.
    :return: ID de la nueva ciudad creada.
    """

    provincia = db.session.get(Provincia, provincia_id)
    if not provincia:
        raise ValueError("La provincia especificada no existe.")

    if existe_ciudad_provincia(nombre_ciudad, obtener_provincia_nombre(provincia_id)):
        raise ValueError("La ciudad ya existe en la provincia especificada.")

    try:
        nueva_ciudad = Ciudad(nombre=nombre_ciudad.strip(), id_provincia=provincia_id)
        db.session.add(nueva_ciudad)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return nueva_ciudad.id_ciudad

    except IntegrityError:
        db.session.rollback()
        raise ValueError("Ya existe una ciudad con ese nombre para la provincia.")
