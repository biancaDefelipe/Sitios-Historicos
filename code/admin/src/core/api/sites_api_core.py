"""
Módulo de consultas avanzadas para Sitios Históricos.

Contiene las funciones necesarias para listar, filtrar, ordenar y obtener sitios
históricos, incluyendo filtros geoespaciales, ordenamiento por rating y paginación,
para ser utilizado principalmente por la API pública.
"""

from sqlalchemy import or_, func
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_DWithin
from slugify import slugify
import datetime
from core.database import db
from core.utils.pagination import paginate
from core.localidad.ciudad import Ciudad
from core.localidad.provincia import Provincia
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.sitios_historicos.tag import Tag
from core.sitios_historicos.estado_conservacion import EstadoConservacion
from core.resenias.resenia import Resenia
from core.resenias.estado_resenia import EstadoResenia
from core.auth.usuario import Usuario


API_FILTER_HANDLERS = {
    "name": lambda q, v: q.filter(
        or_(
            SitioHistorico.nombre.ilike(f"%{v}%"),
            SitioHistorico.descripcion_completa.ilike(f"%{v}%"),
        )
    ),
    "description": lambda q, v: q.filter(
        or_(
            SitioHistorico.nombre.ilike(f"%{v}%"),
            SitioHistorico.descripcion_completa.ilike(f"%{v}%"),
        )
    ),
    "city": lambda q, v: q.join(SitioHistorico.ciudad).filter(
        Ciudad.nombre.ilike(f"%{v}%")
    ),
    "province": lambda q, v: q.join(SitioHistorico.ciudad)
    .join(Ciudad.provincia)
    .filter(Provincia.nombre.ilike(v)),
    "tags": lambda q, v: q.join(SitioHistorico.tags).filter(
        func.lower(Tag.nombre).in_([tag.strip().lower() for tag in v.split(",")])
    ),
}


def _apply_geo_filter(query, args):
    """Función auxiliar para aplicar el filtro geoespacial y depurar posibles problemas."""
    if (
        "lat" in args
        and args["lat"]
        and "long" in args
        and args["long"]
        and "radius" in args
        and args["radius"]
    ):
        try:
            lat, lon, radius = (
                float(args["lat"]),
                float(args["long"]),
                float(args["radius"]),
            )
            point = WKTElement(f"POINT({lon} {lat})", srid=4326)
            query = query.filter(
                ST_DWithin(
                    SitioHistorico.location.cast(Geography),
                    point,
                    radius * 1000,
                )
            )
            return query
        except Exception as e:
            return query
    return query


def _apply_order(query, order_by):
    """Función auxiliar para aplicar el ordenamiento."""
    if order_by in ("oldest", "latest"):
        return (
            query.order_by(SitioHistorico.fecha_hora_alta.asc())
            if order_by == "oldest"
            else query.order_by(SitioHistorico.fecha_hora_alta.desc())
        )
    elif order_by in ("name-asc", "name-desc"):
        return (
            query.order_by(SitioHistorico.nombre.asc())
            if order_by == "name-asc"
            else query.order_by(SitioHistorico.nombre.desc())
        )
    elif order_by in ("rating-5-1", "rating-1-5"):
        avg_rating = func.avg(Resenia.calificacion).label("avg_rating")

        subquery = (
            db.session.query(SitioHistorico, avg_rating)
            .outerjoin(SitioHistorico.resenias)
            .filter(
                SitioHistorico.eliminado == False,
                SitioHistorico.es_visible == True,
            )
            .group_by(SitioHistorico.id_sitio)
            .subquery()
        )

        order_column = (
            subquery.c.avg_rating.desc()
            if order_by == "rating-5-1"
            else subquery.c.avg_rating.asc()
        )

        return (
            db.session.query(SitioHistorico)
            .join(subquery, subquery.c.id_sitio == SitioHistorico.id_sitio)
            .order_by(order_column.nullslast())
        )


def listar_sitios_filtrados_api(args: dict, user_id: int):
    """
    Lista los sitios históricos con filtros, ordenamiento y ranking.
    """

    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    query = db.session.query(SitioHistorico).filter(
        SitioHistorico.eliminado == False, SitioHistorico.es_visible == True
    )

    for key, handler in API_FILTER_HANDLERS.items():
        if key in args and args[key]:
            query = handler(query, args[key])

    query = (
        query.add_columns(func.avg(Resenia.calificacion).label("rank"))
        .outerjoin(
            SitioHistorico.resenias.and_(
                Resenia.id_estado_resenia == _get_estado_id("Aprobada")
            )
        )
        .group_by(SitioHistorico.id_sitio)
    )

    if user_id and args["favorites"]:
        query = query.join(
            SitioHistorico.usuarios_favoritos.and_(Usuario.id_usuario == user_id).and_(
                Usuario.eliminado.is_(False)
            )
        )

    query = _apply_geo_filter(query, args)

    order_by = args.get("order_by", "latest")

    if order_by == "latest":
        query = query.order_by(SitioHistorico.fecha_hora_alta.desc())

    elif order_by == "oldest":
        query = query.order_by(SitioHistorico.fecha_hora_alta.asc())

    elif order_by == "name-asc":
        query = query.order_by(SitioHistorico.nombre.asc())

    elif order_by == "name-desc":
        query = query.order_by(SitioHistorico.nombre.desc())

    elif order_by in ("rating-5-1", "rating-1-5"):
        direction = (
            func.avg(Resenia.calificacion).desc()
            if order_by == "rating-5-1"
            else func.avg(Resenia.calificacion).asc()
        )
        query = query.order_by(direction.nullslast())

    items, pagination_info = paginate(query, page, per_page)

    results = []
    for site, rank in items:
        setattr(site, "rank", round(float(rank), 1) if rank is not None else None)
        results.append(site)

    return results, pagination_info


def crear_sitio_api(data: dict, user_id: int):
    """
    Crea un nuevo sitio histórico desde la API pública.
    Asigna valores por defecto para campos requeridos por la BD pero no provistos por la API.
    """
    ciudad = db.session.query(Ciudad).filter(Ciudad.nombre.ilike(data["city"])).first()
    if not ciudad:
        raise ValueError(f"La ciudad '{data['city']}' no fue encontrada.")

    estado = (
        db.session.query(EstadoConservacion)
        .filter(EstadoConservacion.descripcion.ilike(data["state_of_conservation"]))
        .first()
    )
    if not estado:
        raise ValueError(
            f"El estado de conservación '{data['state_of_conservation']}' no es válido."
        )

    tags_obj = []
    for tag_name in data.get("tags", []):
        tag = db.session.query(Tag).filter(Tag.nombre.ilike(tag_name)).first()
        if not tag:
            tag = Tag(nombre=tag_name, slug=slugify(tag_name))
            db.session.add(tag)
        tags_obj.append(tag)

    new_site = SitioHistorico(
        nombre=data["name"],
        descripcion_breve=data["short_description"],
        descripcion_completa=data["description"],
        anio_inauguracion=datetime.date.today().year,
        id_ciudad=ciudad.id_ciudad,
        id_categoria=1,
        id_estado_cons=estado.id_estado_cons,
        location=WKTElement(f"POINT({data['long']} {data['lat']})", srid=4326),
        tags=tags_obj,
        es_visible=False,
        eliminado=False,
    )

    db.session.add(new_site)
    db.session.commit()

    return new_site


def listar_sitios_por_tag(tag: str, page: int = 1, per_page: int = 20):
    """
    Retorna (items, pagination) donde pagination = {page, per_page, total}
    Implementación usando SQLAlchemy (ejemplo).
    """
    if page < 1:
        raise ValueError("page must be >= 1")

    query = SitioHistorico.query.join(SitioHistorico.tags).filter_by(name=tag)
    total = query.count()
    items = (
        query.order_by(SitioHistorico.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    pagination = {"page": page, "per_page": per_page, "total": total}
    if not items:
        raise ValueError("No sites found")

    return items, pagination


def obtener_sitio_por_id(site_id: int):
    """Obtiene un único SitioHistorico por su ID, incluyendo el cálculo del ranking promedio."""
    query = (
        db.session.query(SitioHistorico, func.avg(Resenia.calificacion).label("rank"))
        .outerjoin(
            SitioHistorico.resenias.and_(
                Resenia.id_estado_resenia == _get_estado_id("Aprobada")
            )
        )
        .filter(
            SitioHistorico.id_sitio == site_id,
            SitioHistorico.eliminado == False,
            SitioHistorico.es_visible == True,
        )
        .group_by(SitioHistorico.id_sitio)
    )

    result = query.first()

    if not result:
        raise ValueError("Site not found")

    site, rank = result
    setattr(site, "rank", round(float(rank), 1) if rank is not None else None)

    return site


def _get_estado_id(descripcion: str):
    return (
        db.session.query(EstadoResenia.id_estado_resenia)
        .filter(EstadoResenia.descripcion == descripcion)
        .scalar_subquery()
    )
