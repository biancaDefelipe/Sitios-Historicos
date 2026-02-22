"""
Módulo de gestión de favoritos de sitios históricos.

Contiene las funciones principales para manipular la relación de muchos-a-muchos
entre Usuarios y Sitios Históricos, permitiendo marcar, desmarcar y listar
los sitios favoritos de un usuario de forma paginada.
"""

from sqlalchemy import func, select
from core.database import db
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.auth.usuario import Usuario
from core.resenias.resenia import Resenia
from core.utils.pagination import paginate
from sqlalchemy.exc import IntegrityError


def marcar_favorito(user_id: int, site_id: int):
    """
    Asegura que un sitio esté marcado como favorito. Es idempotente.
    Usa el patrón ORM .append() para máxima compatibilidad.

    Devuelve:
        - True si la operación fue exitosa (ya sea añadiendo o si ya existía).
        - False si el sitio no se encontró (Site not found).
    """
    sitio = db.session.execute(
        select(SitioHistorico).where(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
    ).scalar_one_or_none()

    if not sitio:
        raise ValueError("Site not found")

    usuario = db.session.execute(
        select(Usuario).where(
            Usuario.id_usuario == user_id,
            Usuario.eliminado.is_(False),
        )
    ).scalar_one_or_none()

    if not usuario:
        raise PermissionError("Authentication required")

    if sitio not in usuario.sitios_favoritos:
        try:
            usuario.sitios_favoritos.append(sitio)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def desmarcar_favorito(user_id: int, site_id: int) -> None:
    """
    Asegura que un sitio NO esté marcado como favorito. Es idempotente.
    Usa el patrón ORM .remove() para máxima compatibilidad.

    Lanza ValueError si el sitio o el usuario no existen.
    """
    sitio = db.session.execute(
        select(SitioHistorico).where(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
    ).scalar_one_or_none()

    if not sitio:
        raise ValueError("Site not found")

    usuario = db.session.execute(
        select(Usuario).where(
            Usuario.id_usuario == user_id,
            Usuario.eliminado.is_(False),
        )
    ).scalar_one_or_none()

    if not usuario:
        raise PermissionError("Authentication required")

    if sitio in usuario.sitios_favoritos:
        try:
            usuario.sitios_favoritos.remove(sitio)
            db.session.commit()
        except ValueError:
            db.session.rollback()


def listar_favoritos_usuario(user_id, args):
    """
    Devuelve una lista paginada de sitios favoritos.
    Lanza ValueError si la paginación es incorrecta (para 400).
    """
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        if page < 1 or not (1 <= per_page <= 100):
            raise ValueError()

    except (TypeError, ValueError):
        raise ValueError(
            "Parámetros de paginación inválidos (page debe ser > 0, per_page entre 1 y 100)."
        )

    query = (
        db.session.query(SitioHistorico)
        .join(SitioHistorico.usuarios_favoritos)
        .filter(
            Usuario.id_usuario == user_id,
            SitioHistorico.eliminado == False,
            SitioHistorico.es_visible == True,
        )
    )

    query = (
        query.add_columns(func.avg(Resenia.calificacion).label("rank"))
        .outerjoin(SitioHistorico.resenias.and_(Resenia.id_estado_resenia == 2))
        .group_by(SitioHistorico.id_sitio)
    )

    items, pagination = paginate(query, page, per_page)

    results = []
    for site, rank in items:
        setattr(site, "rank", round(float(rank), 1) if rank is not None else None)
        results.append(site)

    return results, pagination


def validar_sitio_favorito(user_id: int, site_id: int):
    """
    Verifica si un sitio está marcado como favorito para un usuario autenticado.
    Devuelve el sitio y un booleano indicando si es favorito.
    """
    site = (
        db.session.query(SitioHistorico)
        .filter(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    if not site:
        raise ValueError("Site not found")

    site_is_favorite = (
        db.session.query(SitioHistorico.id_sitio)
        .join(SitioHistorico.usuarios_favoritos)
        .filter(
            SitioHistorico.id_sitio == site_id,
            Usuario.id_usuario == user_id,
        )
        .first()
    )

    return site, site_is_favorite is not None
