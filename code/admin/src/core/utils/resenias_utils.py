"""Utilidades de filtrado y ordenamiento para Resenia.

Provee helpers para aplicar filtros dinámicos y ordenaciones a queries de reseñas.
"""

from sqlalchemy.orm import Query
from datetime import datetime, time
from core.resenias.resenia import Resenia
from core.auth.usuario import Usuario

FILTER_MAP = {
    "estado": lambda v: Resenia.id_estado_resenia == int(v),
    "sitio": lambda v: Resenia.id_sitio_historico == int(v),
    "calificacion_min": lambda v: Resenia.calificacion >= int(v),
    "calificacion_max": lambda v: Resenia.calificacion <= int(v),
    "fecha_desde": lambda v: (
        Resenia.fecha_hora_alta
        >= datetime.combine(datetime.strptime(v, "%Y-%m-%d"), time.min)
        if v
        else True
    ),
    "fecha_hasta": lambda v: (
        Resenia.fecha_hora_alta
        <= datetime.combine(datetime.strptime(v, "%Y-%m-%d"), time.max)
        if v
        else True
    ),
    "usuario": lambda v: Resenia.usuario.has(Usuario.email.ilike(f"%{v}%")),
}

ORDER_MAP = {
    "fecha": Resenia.fecha_hora_alta,
    "calificacion": Resenia.calificacion,
}


def aplicar_filtros_y_ordenamiento(
    query: Query, filtros: dict, orden: str | None = None
) -> Query:
    """
    Aplica los filtros y el ordenamiento a una query de SQLAlchemy.

    :param query: La query base (por ejemplo: db.session.query(Resenia))
    :param filtros: Diccionario con filtros dinámicos (clave -> valor)
    :param orden: Clave de ordenamiento.
    :return: Query completa con filtrado y ordenamiento aplicados.
    """
    for clave, valor in filtros.items():
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            continue
        if clave in FILTER_MAP:
            query = query.filter(FILTER_MAP[clave](valor))

    if orden:
        es_desc = orden.endswith("_desc")
        orden_campo = orden.replace("_desc", "").replace("_asc", "")

        if orden_campo in ORDER_MAP:
            orden_columna = ORDER_MAP[orden_campo]
            query = query.order_by(
                orden_columna.desc() if es_desc else orden_columna.asc()
            )
        else:
            query = query.order_by(Resenia.fecha_hora_alta.desc())
    else:
        query = query.order_by(Resenia.fecha_hora_alta.desc())

    return query
