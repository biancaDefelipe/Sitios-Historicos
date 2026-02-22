"""Servicios de API pública para la gestión de reseñas.

Este módulo expone funciones de acceso y manipulación de reseñas
asociadas a sitios históricos, aplicando validaciones de negocio,
control de estados y paginación de resultados.
"""

from datetime import datetime, timezone
from core.auth.usuario import Usuario
from core.database import db
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.resenias.resenia import Resenia
from core.resenias.estado_resenia import EstadoResenia
from core.utils.pagination import paginate
from sqlalchemy.orm import joinedload


def listar_resenias_de_sitio_api(site_id: int, page: int, per_page: int):
    """
    Lista las reseñas de un sitio, validando primero el sitio.
    Lanza un ValueError si el sitio no existe.
    """
    sitio = (
        db.session.query(SitioHistorico.id_sitio)
        .filter(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    if not sitio:
        raise ValueError("Site not found")

    query = (
        db.session.query(Resenia)
        .options(joinedload(Resenia.usuario), joinedload(Resenia.estado_resenia))
        .filter(
            Resenia.id_sitio_historico == site_id,
            Resenia.id_estado_resenia == _get_estado_id_sq("Aprobada"),
        )
        .order_by(Resenia.fecha_hora_alta.desc())
    )

    items, pagination_info = paginate(query, page, per_page)
    return items, pagination_info


def crear_resenia_api(data: dict, user_id: int, site_id: int):
    """
    Crea una reseña para la API pública.
    Si ya existe una reseña del usuario para el sitio, lanza un error.
    La reseña se crea en estado 'Pendiente'.
    """

    sitio = (
        db.session.query(SitioHistorico.id_sitio)
        .filter(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    if not sitio:
        raise ValueError("Site not found.")

    # No se controla el estado de la reseña porque no hace falta, ya que solo puede existir
    # una reseña por usuario y por sitio. No debe poder escribir otra aunque elimine la existente (borrado logico).
    resenia_existente = (
        db.session.query(Resenia)
        .filter_by(id_usuario=user_id, id_sitio_historico=site_id)
        .first()
    )
    if resenia_existente:
        raise RuntimeError("Ya existe una reseña de este usuario para este sitio.")

    resenia = Resenia(
        calificacion=data["calificacion"],
        contenido=data["contenido"],
        id_usuario=user_id,
        id_sitio_historico=site_id,
        fecha_hora_alta=datetime.now(timezone.utc),
        fecha_hora_modificacion=None,
        id_estado_resenia=_get_estado_id_int("Pendiente"),
        motivo_rechazo=None,
    )
    db.session.add(resenia)
    db.session.commit()
    return resenia


def editar_resenia_api(review_id: int, data: dict, user_id: int, site_id: int):
    """
    Edita una reseña existente del usuario para el sitio.
    """
    resenia = (
        db.session.query(Resenia)
        .join(Resenia.sitio_historico)
        .filter(
            Resenia.id_resenia == review_id,
            Resenia.id_usuario == user_id,
            Resenia.id_sitio_historico == site_id,
            Resenia.id_estado_resenia != _get_estado_id_sq("Eliminada"),
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    if not resenia:
        raise ValueError("Review not found or not owned by user.")

    resenia.calificacion = data["calificacion"]
    resenia.contenido = data["contenido"]
    resenia.fecha_hora_modificacion = datetime.now(timezone.utc)
    resenia.motivo_rechazo = None
    resenia.id_estado_resenia = _get_estado_id_int("Pendiente")
    db.session.commit()
    return resenia


def obtener_usuario_resenia_api(site_id: int, user_id: int):
    """
    Obtiene una única Resenia por su ID y sitio, solo si:
    - El usuario existe y no está eliminado
    - El sitio está visible y no eliminado
    Lanza ValueError si no se encuentra.
    """
    user = (
        db.session.query(Usuario.id_usuario)
        .filter(
            Usuario.id_usuario == user_id,
            Usuario.eliminado.is_(False),
        )
        .first()
    )

    if not user:
        raise ValueError("User not found")

    resenia = (
        db.session.query(Resenia)
        .join(Resenia.sitio_historico)
        .options(joinedload(Resenia.sitio_historico))
        .filter(
            Resenia.id_sitio_historico == site_id,
            Resenia.id_usuario == user_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    eliminada = resenia is not None and resenia.id_estado_resenia == _get_estado_id_int(
        "Eliminada"
    )

    return eliminada, resenia


def obtener_resenia_api(review_id: int, site_id: int):
    """
    Obtiene una única Resenia por su ID y sitio, solo si:
    - La reseña existe y está aprobada (id_estado_resenia=2)
    - El sitio está visible y no eliminado
    Lanza ValueError si no se encuentra.
    """
    sitio = (
        db.session.query(SitioHistorico.id_sitio)
        .filter(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    if not sitio:
        raise ValueError("Site not found.")

    resenia = (
        db.session.query(Resenia)
        .options(joinedload(Resenia.sitio_historico))
        .filter(
            Resenia.id_resenia == review_id,
            Resenia.id_sitio_historico == site_id,
            Resenia.id_estado_resenia == _get_estado_id_sq("Aprobada"),
        )
        .first()
    )

    if not resenia:
        raise ValueError("Review not found.")

    return resenia


def eliminar_resenia_api(review_id: int, user_id: int, site_id: int):
    """
    Elimina una reseña si pertenece al usuario que la solicita.
    Cambia el estado de la reseña a 4 (Eliminada) en lugar de eliminarla físicamente.
    Lanza PermissionError si no es el dueño.
    Lanza ValueError si no se encuentra la reseña.
    """
    resenia = (
        db.session.query(Resenia)
        .join(Resenia.sitio_historico)
        .filter(
            Resenia.id_resenia == review_id,
            Resenia.id_estado_resenia != _get_estado_id_sq("Eliminada"),
            Resenia.id_sitio_historico == site_id,
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
        .first()
    )

    # Necesitamos validar por separado que la review exista y que sea propia del usuario
    # autenticado, para poder lanzar la excepcion correcta en cada caso, y retornar lo que
    # corresponde según la especificación de la API.
    if not resenia:
        raise ValueError("Review not found")

    # Si esto lo hicieramos en la misma consulta, no podríamos distinguir entre review no existente
    # y review existente pero de otro usuario, y no podríamos lanzar la excepción adecuada.
    if resenia.id_usuario != user_id:
        raise PermissionError("No tienes permiso para eliminar esta reseña.")

    # Cambiar estado a 4 (Eliminada)
    resenia.id_estado_resenia = _get_estado_id_int("Eliminada")
    db.session.commit()
    return True


def listar_resenias_de_usuario_api(user_id, page, per_page, order="desc"):
    """
    Lista todas las reseñas del usuario autenticado.
    Devuelve estados: 1 (pendiente), 2 (aprobada), 4 (eliminada)
    """
    query = (
        db.session.query(Resenia)
        .join(Resenia.sitio_historico)
        .options(
            joinedload(Resenia.sitio_historico),
            joinedload(Resenia.estado_resenia),
        )
        .filter(
            Resenia.id_usuario == user_id,
            Resenia.id_estado_resenia.in_(
                _get_multiples_estados_ids_sq["Pendiente", "Aprobada", "Eliminada"]
            ),
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
    )

    order_by_fecha = (
        Resenia.fecha_hora_alta.asc()
        if order == "asc"
        else Resenia.fecha_hora_alta.desc()
    )
    query = query.order_by(order_by_fecha)

    items, pagination_info = paginate(query, page, per_page)
    return items, pagination_info


def _get_estado_id_sq(descripcion: str):
    """Obtiene el ID de un estado de reseña como subquery SQLAlchemy."""
    return (
        db.session.query(EstadoResenia.id_estado_resenia)
        .filter(EstadoResenia.descripcion == descripcion)
        .scalar_subquery()
    )


def _get_estado_id_int(descripcion: str) -> int | None:
    """Obtiene el ID de un estado de reseña como entero."""
    return (
        db.session.query(EstadoResenia.id_estado_resenia)
        .filter(EstadoResenia.descripcion == descripcion)
        .scalar()
    )


def _get_multiples_estados_ids_sq(*descripciones):
    """Obtiene múltiples IDs de estados de reseña como subquery."""
    return (
        db.session.query(EstadoResenia.id_estado_resenia)
        .filter(EstadoResenia.descripcion.in_(descripciones))
        .subquery()
    )
