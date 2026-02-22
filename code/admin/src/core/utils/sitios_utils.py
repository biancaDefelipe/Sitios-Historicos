"""Utilidades de filtrado y ordenamiento para SitioHistorico.

Provee helpers para aplicar filtros dinámicos y ordenaciones a queries.
"""

from core.sitios_historicos.tag import Tag
from sqlalchemy import or_, func
from sqlalchemy.orm import Query
from datetime import datetime, time
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.localidad.ciudad import Ciudad

FILTER_MAP = {
    "ciudad": lambda v: SitioHistorico.ciudad.has(
        func.trim(func.upper(Ciudad.nombre)) == func.trim(func.upper(v))
    ),
    "provincia": lambda v: SitioHistorico.ciudad.has(Ciudad.id_provincia == int(v)),
    "categoria": lambda v: SitioHistorico.id_categoria == int(v),
    "estado": lambda v: SitioHistorico.id_estado_cons == int(v),
    "fecha_desde": lambda v: (
        SitioHistorico.fecha_hora_alta
        >= datetime.combine(datetime.strptime(v, "%Y-%m-%d"), time.min)
        if v
        else True
    ),
    "fecha_hasta": lambda v: (
        SitioHistorico.fecha_hora_alta
        <= datetime.combine(datetime.strptime(v, "%Y-%m-%d"), time.max)
        if v
        else True
    ),
    "visibilidad": lambda v: SitioHistorico.es_visible == (str(v).lower() == "true"),
    "busqueda": lambda v: or_(
        SitioHistorico.nombre.ilike(f"%{v}%"),
        SitioHistorico.descripcion_breve.ilike(f"%{v}%"),
    ),
    "tags": lambda v: SitioHistorico.tags.any(Tag.id_tag.in_(v)),
}

ORDER_MAP = {
    "fecha": SitioHistorico.fecha_hora_alta,
    "nombre": SitioHistorico.nombre,
    "ciudad": Ciudad.nombre,
}

JOIN_MAP = {"ciudad": SitioHistorico.ciudad}


def aplicar_filtros_y_ordenamiento(
    query: Query, filtros: dict, orden: str | None = None
) -> Query:
    """
    Aplica los filtros y el ordenamiento a una query de SQLAlchemy.

    :param query: La query base (por ejemplo: db.session.query(SitioHistorico))
    :param filtros: Diccionario con filtros dinámicos (clave -> valor)
    :param orden: Clave de ordenamiento.
    :return: Query completa con filtrado y ordenamiento aplicados.
    """
    for clave, valor in filtros.items():
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            continue
        # Ignorar arrays vacíos
        if isinstance(valor, list) and len(valor) == 0:
            continue
        if clave in FILTER_MAP:
            query = query.filter(FILTER_MAP[clave](valor))

    if orden:
        es_desc = orden.endswith("_desc")
        orden_campo = orden.replace("_desc", "").replace("_asc", "")

        # Si el campo requiere JOIN, lo aplicamos dinámicamente
        if orden_campo in JOIN_MAP:
            query = query.join(JOIN_MAP[orden_campo])

        if orden_campo in ORDER_MAP:
            orden_columna = ORDER_MAP[orden_campo]
            query = query.order_by(
                orden_columna.desc() if es_desc else orden_columna.asc()
            )
        else:
            query = query.order_by(SitioHistorico.fecha_hora_alta.desc())
    else:
        query = query.order_by(SitioHistorico.fecha_hora_alta.desc())

    return query
