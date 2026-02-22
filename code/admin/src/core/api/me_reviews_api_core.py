"""
Módulo para la consulta de reseñas.

Contiene funciones para listar las reseñas creadas por un usuario específico,
aplicando filtros por estado y paginación para su uso en la API.
"""

from core.database import db
from core.resenias.resenia import Resenia
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.utils.pagination import paginate
from sqlalchemy.orm import joinedload


def listar_resenias_de_usuario_api(user_id, page, per_page, order="desc"):
    """
    Lista todas las reseñas del usuario autenticado.
    Devuelve estados: 1 (pendiente), 2 (aprobada), 3 (rechazada)
    """

    query = (
        db.session.query(Resenia)
        .join(
            SitioHistorico,
            Resenia.id_sitio_historico == SitioHistorico.id_sitio,
        )
        .options(
            joinedload(Resenia.sitio_historico),
            joinedload(Resenia.estado_resenia),
        )
        .filter(
            Resenia.id_usuario == user_id,
            Resenia.id_estado_resenia.in_([1, 2, 3]),
            SitioHistorico.eliminado.is_(False),
            SitioHistorico.es_visible.is_(True),
        )
    )

    if order == "asc":
        query = query.order_by(Resenia.fecha_hora_alta.asc())
    else:
        query = query.order_by(Resenia.fecha_hora_alta.desc())

    items, pagination_info = paginate(query, page, per_page)
    return items, pagination_info
