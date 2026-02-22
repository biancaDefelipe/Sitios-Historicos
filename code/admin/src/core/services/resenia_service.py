"""Servicio de gestión de reseñas.

Capa de servicio que coordina las operaciones de negocio relacionadas
con las reseñas, delegando en el módulo core.resenias.
"""

from core.resenias.resenia_contexto import ReseniaContexto
from core import resenias as resenias_core


def obtener_resenias(filtros=None, orden=None, nroPagina=1, cant_por_pagina=None):
    """Obtiene una lista paginada de reseñas con filtros y ordenamiento.

    :param filtros: Diccionario con filtros a aplicar.
    :param orden: Criterio de ordenamiento.
    :param nroPagina: Número de página actual.
    :return: Tupla con lista de reseñas y objeto de paginación.
    """

    return resenias_core.get_resenias(
        filtros, orden, nroPagina, cant_por_pagina=cant_por_pagina
    )


def listar_estados_resenias():
    """Lista todos los estados de reseñas disponibles en el sistema.

    :return: Lista de objetos EstadoResenia.
    """
    return resenias_core.listar_estados_resenias()


def aprobar_resenia(id_resenia: int):
    """Aprueba la reseña especificada por su ID.

    :param id_resenia: ID de la reseña a aprobar.
    """
    try:
        res_model = resenias_core.obtener_resenia(id_resenia)
        if not res_model:
            raise ValueError
        contexto = ReseniaContexto(res_model)
        resenias_core.aprobar_resenia(contexto)
    except Exception as e:
        return


def eliminar_resenia(id_resenia):
    """Elimina la reseña especificada por su ID.

    :param id_resenia: ID de la reseña a eliminar.
    """
    try:
        res_model = resenias_core.obtener_resenia(id_resenia)
        if not res_model:
            raise ValueError
        contexto = ReseniaContexto(res_model)
        resenias_core.eliminar_resenia(contexto)
    except Exception as e:
        return


def rechazar_resenia(id_resenia: int, motivo: str):
    """Rechaza la reseña especificada por su ID.

    :param id_resenia: ID de la reseña a rechazar.
    :param motivo: Motivo del rechazo.
    """
    try:
        res_model = resenias_core.obtener_resenia(id_resenia)
        if not res_model:
            raise ValueError
        contexto = ReseniaContexto(res_model)
        resenias_core.rechazar_resenia(contexto, motivo)
    except Exception as e:
        return


def obtener_detalle_resenia(id_resenia: int) -> dict | None:
    """Obtiene los datos completos de una reseña.

    :param id_resenia: ID de la reseña.
    :return: Objeto Resenia con relaciones cargadas o None.
    """
    try:
        res_model = resenias_core.obtener_resenia(id_resenia)
        if not res_model:
            raise ValueError
        return resenias_core.obtener_detalle_resenia(id_resenia)
    except Exception as e:
        return


def editar_resenia(id_resenia: int, contenido: str):
    """Actualiza el contenido de una reseña existente.

    :param id_resenia: ID de la reseña a editar.
    :param contenido: Nuevo contenido de la reseña.
    """
    try:
        res_model = resenias_core.obtener_resenia(id_resenia)
        if not res_model:
            raise ValueError
        contexto = ReseniaContexto(res_model)
        resenias_core.editar_resenia(contexto, contenido)
    except Exception as e:
        return
