"""
Módulo de gestión de sitios históricos y tags.

Este módulo contiene funciones de acceso a datos y lógica de negocio
relacionadas con:
- Listado y filtrado de sitios históricos
- Gestión de categorías, estados de conservación y tags
- Búsqueda, ordenamiento y paginación de tags
- Validaciones de unicidad y relaciones entre entidades
"""

from core.database import db
from core.sitios_historicos.imagen import Imagen
from .categoria import Categoria
from .estado_conservacion import EstadoConservacion
from sqlalchemy import select, func, exists, or_
from sqlalchemy.exc import IntegrityError
from .sitio_historico import sitios_tags
from core.utils.pagination import paginate
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.sitios_historicos.tag import Tag
from core.localidad.ciudad import Ciudad
from core.utils.fechas_utils import convertir_a_datetime_date

FILTER_MAP = {
    "ciudad": lambda v: Ciudad.nombre.ilike(f"%{v}%"),
    "id_provincia": lambda v: Ciudad.id_provincia == v,
    "estado": lambda v: SitioHistorico.estado_conservacion == v,
    "fecha_desde": lambda v: SitioHistorico.fecha_hora_alta
    >= convertir_a_datetime_date(v),
    "fecha_hasta": lambda v: SitioHistorico.fecha_hora_alta
    <= convertir_a_datetime_date(v),
    "visibilidad": lambda v: SitioHistorico.es_visible == v,
    "busqueda": lambda v: or_(
        SitioHistorico.nombre.ilike(f"%{v}%"),
        SitioHistorico.descripcion_breve.ilike(f"%{v}%"),
    ),
    "tags": lambda v: SitioHistorico.tags.any(Tag.id.in_(v)),
}

ORDER_MAP = {
    "fecha": SitioHistorico.fecha_hora_alta,
    "nombre": SitioHistorico.nombre,
    "ciudad": SitioHistorico.ciudad,
}


def listar_sitios_filtrados(
    filtros=None, orden=None, direccion=None, page: int = 1, per_page=None
):
    """
    Lista sitios históricos aplicando filtros, ordenamiento y paginación.

    :param filtros: Diccionario de filtros a aplicar.
    :param orden: Campo de ordenamiento ('fecha', 'nombre', 'ciudad').
    :param direccion: 'asc' o 'desc'.
    :param page: Número de página (comienza en 1).
    :param per_page: Cantidad de elementos por página (opcional).
    :return: Tupla (items, pagination) donde:
             - items es la lista de SitioHistorico de la página actual
             - pagination es el diccionario devuelto por paginate
    """
    query = (
        db.session.query(SitioHistorico)
        .join(SitioHistorico.ciudad)
        .join(Ciudad.provincia)
    )

    if filtros:
        for key, value in filtros.items():
            if value is None or value == "" or value.isspace():
                continue
            if key in FILTER_MAP:
                query = query.filter(FILTER_MAP[key](value))

    if orden and orden in ORDER_MAP:
        columna = ORDER_MAP[orden]
        if direccion == "desc":
            query = query.order_by(columna.desc())
        else:
            query = query.order_by(columna.asc())

    items, pagination = paginate(
        query=query,
        page=page,
        per_page=per_page,
    )

    return items, pagination


def listar_categorias_nombres() -> list[str]:
    """Obtiene las descripciones de todas las categorías."""
    categorias = (
        db.session.query(Categoria.descripcion)
        .order_by(Categoria.descripcion.asc())
        .all()
    )
    return [c[0] for c in categorias]


def listar_estados_nombres() -> list[str]:
    """Obtiene las descripciones de todos los estados de conservación."""
    estados = (
        db.session.query(EstadoConservacion.descripcion)
        .order_by(EstadoConservacion.descripcion.asc())
        .all()
    )
    return [e[0] for e in estados]


def obtener_estado_id(nombre_estado: str) -> int | None:
    """Busca un Estado de Conservación por su descripción y devuelve su ID."""
    estado = (
        db.session.query(EstadoConservacion)
        .filter(EstadoConservacion.descripcion.ilike(nombre_estado.strip()))
        .first()
    )
    return estado.id_estado_cons if estado else None


def crear_tag(nombre: str, slug: str) -> Tag:
    """
    Crea un nuevo tag en la base de datos.
    - Convierte el nombre a minúsculas y genera el slug automáticamente.
    - No valida unicidad (ya verificada por el controlador).
    """
    if not slug:
        raise ValueError("Error en la creación del tag")

    new_tag = Tag(nombre=nombre, slug=slug)
    db.session.add(new_tag)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error al crear el tag: {str(e)}")

    return new_tag


def borrar_tag(tag_id: int) -> bool:
    """
    Elimina un tag de la base de datos si no está asociado a ningún sitio histórico.
    Retorna True si se eliminó correctamente.
    Lanza ValueError si el tag no existe o si está asociado a algún sitio.
    """

    tag = db.session.get(Tag, tag_id)
    if not tag:
        raise ValueError(f"No se encontró ningún tag con id {tag_id}.")

    stmt_check = select(exists().where(sitios_tags.c.id_tag == tag_id))
    asociado = db.session.scalar(stmt_check)

    if asociado:
        raise ValueError(
            "No se puede eliminar el tag porque está en uso."
        )

    try:
        db.session.delete(tag)
        db.session.commit()
        return True

    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error al eliminar el tag: {str(e)}")


def listar_tags(
    order: str,
    q: str | None = None,
    page: int = 1,
    per_page=None,
):
    """
    Lista tags con búsqueda (por nombre), orden y paginación del lado del servidor.

    :param q: texto de búsqueda (busca en nombre, case-insensitive, partial match)
    :param order: 'name_asc' | 'name_desc' | 'fecha_asc' | 'fecha_desc'
    :param page: número de página (1-based)
    :param per_page: elementos por página
    :return: (items, pagination)
    """
    query = db.session.query(Tag)

    if q:
        pattern = f"%{q.strip().lower()}%"
        query = query.filter(func.lower(Tag.nombre).like(pattern))

    if order == "name_asc":
        query = query.order_by(Tag.nombre.asc())
    elif order == "name_desc":
        query = query.order_by(Tag.nombre.desc())
    elif order == "fecha_asc":
        query = query.order_by(Tag.fecha_hora_alta.asc())
    elif order == "fecha_desc":
        query = query.order_by(Tag.fecha_hora_alta.desc())

    items, pagination = paginate(query=query, page=page, per_page=per_page)

    return items, pagination


def existe_tag_nombre_slug(nombre: str, slug: str) -> Tag | None:
    """
    Devuelve un tag que tenga el mismo nombre o el mismo slug (case-insensitive).
    Si no existe, devuelve None.
    :param nombre: nombre del tag
    :param slug slug del tag
    """
    if not nombre and not slug:
        return None
    tag = (
        db.session.query(Tag)
        .filter(
            or_(
                func.lower(Tag.nombre) == nombre.lower(),
                func.lower(Tag.slug) == slug.lower(),
            )
        )
        .first()
    )
    return tag


def editar_tag(tag_id: int, nombre: str, slug: str) -> Tag:
    """
    Edita el nombre y slug de un tag existente.
    Valida unicidad de nombre y slug excluyendo el propio tag.
    """
    if not slug:
        raise ValueError("Error en la creación del tag")

    tag = db.session.get(Tag, tag_id)
    if not tag:
        raise ValueError("El tag que se quiere editar no existe.")

    tag.nombre = nombre
    tag.slug = slug

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Error al actualizar el tag con los datos ingresados.")

    return tag


def obtener_todos_los_tags() -> list[Tag]:
    """Devuelve todos los tags existentes en el sistema."""
    return db.session.query(Tag).order_by(Tag.nombre.asc()).all()


def obtener_sitio_por_id(site_id: int):
    """Obtiene un sitio histórico por su ID."""
    stmt = select(SitioHistorico).filter(SitioHistorico.id_sitio == site_id)
    result = db.session.execute(stmt).scalar_one_or_none()

    return result


def obtener_imagen_por_id(image_id: int):
    """Obtiene una imagen por su ID."""
    imagen = db.session.get(Imagen, image_id)
    return imagen
