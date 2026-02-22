"""Módulo de gestión de reseñas.

Este módulo contiene las funciones para gestionar las reseñas de sitios históricos,
incluyendo listado con filtros, cambio de estados y obtención de detalles.
"""

from core.database import db
from sqlalchemy.orm import joinedload
import logging
from core.localidad.ciudad import Ciudad
from core.localidad.provincia import Provincia
from core.utils.pagination import paginate
from core.utils.resenias_utils import aplicar_filtros_y_ordenamiento
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.auth.usuario import Usuario
from core.resenias.resenia import Resenia
from core.resenias.estado_resenia import EstadoResenia
from core.resenias.resenia_contexto import ReseniaContexto


logger = logging.getLogger(__name__)


def get_resenias(filtros=None, orden=None, nro_pagina=1, cant_por_pagina=None):
    """Devuelve una lista de reseñas paginada con filtros y ordenamiento.

    :param filtros: Diccionario con filtros a aplicar.
    :param orden: Criterio de ordenamiento.
    :param nro_pagina: Número de página actual.
    :param cant_por_pagina: Cantidad de elementos por página.
    :return: Tupla con lista de reseñas y objeto de paginación.
    """
    try:
        query = (
            db.session.query(Resenia)
            .join(SitioHistorico)
            .filter(SitioHistorico.eliminado == False)
            .options(
                joinedload(Resenia.usuario).load_only(Usuario.email),
                joinedload(Resenia.estado_resenia).load_only(EstadoResenia.descripcion),
                joinedload(Resenia.sitio_historico)
                .load_only(SitioHistorico.nombre)
                .joinedload(SitioHistorico.ciudad)
                .load_only(Ciudad.nombre)
                .joinedload(Ciudad.provincia)
                .load_only(Provincia.nombre),
            )
        )

        query = aplicar_filtros_y_ordenamiento(query, filtros, orden)

        resenias, paginacion = paginate(
            query=query, page=nro_pagina, per_page=cant_por_pagina
        )

        return resenias, paginacion

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        logger.exception(f"Mensaje: {msj}")
        raise e


def listar_estados_resenias():
    """Lista todos los estados de reseñas disponibles en el sistema.

    :return: Lista de objetos EstadoResenia ordenados por id.
    """
    try:
        return (
            db.session.query(EstadoResenia)
            .order_by(EstadoResenia.id_estado_resenia.asc())
            .all()
        )

    except Exception as e:
        msj = "Ocurrió un error inesperado."
        logger.exception(f"Mensaje: {msj}")
        raise e


def obtener_resenia(id_resenia: int) -> Resenia | None:
    """Obtiene la reseña con el id especificado.

    :param id_resenia: ID de la reseña.
    :return: Objeto Resenia o None si no existe.
    """
    try:
        res_model = db.session.query(Resenia).get(id_resenia)
        return res_model

    except Exception as e:
        msj = "Ocurrió un error insperado."
        logger.exception(f"Mensaje: {msj}")
        raise e


def aprobar_resenia(contexto: ReseniaContexto):
    """Aprueba la reseña recibida por parámetro.

    :param contexto: Contexto de la reseña a aprobar.
    """
    try:
        contexto.aprobar()
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def eliminar_resenia(contexto: ReseniaContexto):
    """Elimina la reseña recibida por parámetro.

    :param contexto: Contexto de la reseña a eliminar.
    """
    try:
        contexto.eliminar()
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def rechazar_resenia(contexto: ReseniaContexto, motivo: str):
    """Rechaza la reseña recibida por parámetro.

    :param contexto: Contexto de la reseña a rechazar.
    :param motivo: Motivo del rechazo.
    """
    try:
        contexto.rechazar(motivo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def obtener_detalle_resenia(id_resenia: int) -> dict | None:
    """Obtiene los datos completos de la reseña especificada.

    :param id_resenia: ID de la reseña.
    :return: Objeto Resenia con relaciones cargadas o None si no existe.
    """
    try:
        return (
            db.session.query(Resenia)
            .options(
                joinedload(Resenia.usuario),
                joinedload(Resenia.sitio_historico),
                joinedload(Resenia.estado_resenia),
            )
            .filter(Resenia.id_resenia == id_resenia)
            .one_or_none()
        )

    except Exception as e:
        msj = "Ocurrió un error insperado obtiendo la reseña."
        logger.exception(f"Mensaje: {msj}: {str(e)}")
        raise


def editar_resenia(contexto: ReseniaContexto, contenido: str):
    """Actualiza el contenido de la reseña con el texto recibido.

    :param contexto: Contexto de la reseña a editar.
    :param contenido: Nuevo contenido de la reseña.
    """
    try:
        contexto.pendiente(contenido)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
