"""
Módulo de gestión de historial de sitios históricos.

Este módulo contiene funciones para registrar, consultar y gestionar
el historial de cambios y eventos relacionados con los sitios históricos.
"""

from core.database import db
from core.sitios_historicos.sitio_historico import SitioHistorico
from core.historial.historial_sitio import HistorialSitio
from core.sitios_repo.repo_sitios_historicos import SiteRepo
from core.historial.accion import Accion
from web.dtos.site_dto import SiteDTO
from flask import current_app
from sqlalchemy import func
from core.utils.pagination import paginate
from sqlalchemy.orm import joinedload
from web.dtos.historial_dto import HistorialDTO
from core.auth.usuario import Usuario
from core.localidad.ciudad import Ciudad


def _obtener_id_accion(descripcion: str) -> int:
    """Busca el ID de la acción por su descripción."""
    accion = (
        db.session.query(Accion)
        .filter(func.lower(Accion.descripcion) == descripcion.lower())
        .first()
    )
    if not accion:
        raise ValueError(f"Acción '{descripcion}' no encontrada.")
    return accion.id_accion


def _registrar_cambio(
    sitio_id: int,
    user_id: int,
    accion_desc: str,
    campo: str,
    valor_anterior: str,
    valor_nuevo: str,
):
    """Crea un nuevo registro de HistorialSitio."""
    id_accion = _obtener_id_accion(accion_desc)
    registro = HistorialSitio(
        id_sitio=sitio_id,
        id_usuario=user_id,
        id_accion=id_accion,
        campo_modificado=campo,
        valor_anterior=str(valor_anterior),
        valor_nuevo=str(valor_nuevo),
    )
    db.session.add(registro)


def registrar_evento_simple(sitio_id: int, user_id: int, accion_desc: str):
    """Registra un evento simple que no implica un cambio de campo
    (Creación, Eliminación)."""
    try:
        id_accion = _obtener_id_accion(accion_desc)
        registro = HistorialSitio(
            id_sitio=sitio_id, id_usuario=user_id, id_accion=id_accion
        )
        db.session.add(registro)
    except Exception as e:
        current_app.logger.error(
            f"Error al registrar evento simple de historial para sitio {sitio_id}: {e}"
        )


def _to_historial_dto_general(model: HistorialSitio) -> HistorialDTO:
    """
    Convierte un modelo de HistorialSitio a HistorialDTO, 
    incluyendo el nombre del sitio y el nombre completo del usuario.
    """
    nombre_completo = f"{model.usuario.nombre} {model.usuario.apellido}"

    sitio_nombre = (
        model.sitio_historico.nombre
        if model.sitio_historico
        else "Sitio Desconocido/Eliminado"
    )
    fecha_original = model.fecha_hora_modificacion

    return HistorialDTO(
        id_registro=model.id_registro,
        fecha_hora=fecha_original,
        accion=model.accion.descripcion,
        usuario_nombre_completo=nombre_completo,
        sitio_id=model.id_sitio,
        sitio_nombre=sitio_nombre,
        usuario_id=model.id_usuario,
    )


def listar_historial_general(
    site_nombre=None,
    user_email=None,
    accion_desc=None,
    fecha_inicio=None,
    fecha_fin=None,
    page=1,
    per_page=25,
):
    """
    Lista y filtra el historial de modificaciones de manera general (todos los sitios).

    :param site_nombre: nombre del sitio para filtrar.
    :param user_email: email del usuario para filtrar.
    :param accion_desc: descripción de la acción para filtrar.
    :param fecha_inicio: fecha de inicio del rango de filtrado.
    :param fecha_fin: fecha de fin del rango de filtrado.
    :param page: número de página para la paginación.
    :param per_page: cantidad de registros por página.
    :return: lista de HistorialDTO y diccionario de paginación.
    """
    query = db.session.query(HistorialSitio).options(
        joinedload(HistorialSitio.usuario),
        joinedload(HistorialSitio.accion),
        joinedload(HistorialSitio.sitio_historico),
    )

    if site_nombre:
        query = query.filter(
            HistorialSitio.sitio_historico.has(
                SitioHistorico.nombre.ilike(f"%{site_nombre}%")
            )
        )

    if user_email:
        query = query.filter(HistorialSitio.usuario.has(Usuario.email == user_email))

    if accion_desc:
        query = query.filter(
            HistorialSitio.accion.has(Accion.descripcion == accion_desc)
        )

    if fecha_inicio:
        query = query.filter(HistorialSitio.fecha_hora_modificacion >= fecha_inicio)

    if fecha_fin:
        query = query.filter(HistorialSitio.fecha_hora_modificacion <= fecha_fin)

    query = query.order_by(HistorialSitio.fecha_hora_modificacion.desc())

    items, pagination = paginate(query, page, per_page)

    return [_to_historial_dto_general(item) for item in items], pagination


def listar_acciones():
    """Devuelve una lista de descripciones de todas las acciones disponibles."""
    acciones = db.session.query(Accion.descripcion).all()
    return [a[0] for a in acciones]


def registrar_cambios_update(
    sitio_original: SitioHistorico, dto_nuevo: SiteDTO, user_id: int, repo: SiteRepo
):
    """
    Compara un SitioHistorico con un SiteDTO y registra todos los cambios.

    :param sitio_original: sitio histórico antes de la actualización.
    :param dto_nuevo: DTO con los nuevos datos del sitio.
    :param user_id: ID del usuario que realiza la modificación.
    :param repo: repositorio de sitios para obtener nombres de categorías/estados.
    """
    if sitio_original.nombre != dto_nuevo.nombre.strip():
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Nombre",
            sitio_original.nombre,
            dto_nuevo.nombre.strip(),
        )

    if sitio_original.descripcion_breve != dto_nuevo.descripcion_breve:
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Descripción Breve",
            sitio_original.descripcion_breve,
            dto_nuevo.descripcion_breve,
        )

    if sitio_original.descripcion_completa != dto_nuevo.descripcion_detallada:
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Descripción Detallada",
            sitio_original.descripcion_completa,
            dto_nuevo.descripcion_detallada,
        )

    if sitio_original.anio_inauguracion != dto_nuevo.anio_inauguracion:
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Año de Inauguración",
            sitio_original.anio_inauguracion,
            dto_nuevo.anio_inauguracion,
        )

    if sitio_original.es_visible != dto_nuevo.visible:
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Visibilidad",
            "Visible" if sitio_original.es_visible else "Oculto",
            "Visible" if dto_nuevo.visible else "Oculto",
        )

    if sitio_original.id_categoria != dto_nuevo.categoria_id:
        nombre_cat_anterior = repo.obtener_categoria_nombre(sitio_original.id_categoria)
        nombre_cat_nueva = repo.obtener_categoria_nombre(dto_nuevo.categoria_id)
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Categoría",
            nombre_cat_anterior,
            nombre_cat_nueva,
        )

    if sitio_original.id_estado_cons != dto_nuevo.estado_id:
        nombre_estado_anterior = repo.obtener_estado_nombre(
            sitio_original.id_estado_cons
        )
        nombre_estado_nuevo = repo.obtener_estado_nombre(dto_nuevo.estado_id)
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Cambio de Estado",
            "Estado de Conservación",
            nombre_estado_anterior,
            nombre_estado_nuevo,
        )

    tags_anteriores = {tag.nombre for tag in sitio_original.tags}
    tags_nuevos = set(dto_nuevo.tags or [])
    if tags_anteriores != tags_nuevos:
        tags_añadidos = tags_nuevos - tags_anteriores
        tags_removidos = tags_anteriores - tags_nuevos
        for tag in tags_añadidos:
            _registrar_cambio(
                sitio_original.id_sitio,
                user_id,
                "Cambio de Tags",
                "Tag Añadido",
                "",
                tag,
            )
        for tag in tags_removidos:
            _registrar_cambio(
                sitio_original.id_sitio,
                user_id,
                "Cambio de Tags",
                "Tag Removido",
                tag,
                "",
            )

    if sitio_original.id_ciudad != dto_nuevo.ciudad_id:
        ubicacion_anterior = (
            f"{sitio_original.ciudad.nombre}, {sitio_original.ciudad.provincia.nombre}"
        )
        nueva_ciudad = db.session.get(Ciudad, dto_nuevo.ciudad_id)
        ubicacion_nueva = f"{nueva_ciudad.nombre}, {nueva_ciudad.provincia.nombre}"
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Ubicación (Ciudad)",
            ubicacion_anterior,
            ubicacion_nueva,
        )

    if float(sitio_original.lat) != float(dto_nuevo.latitud) or float(
        sitio_original.lon
    ) != float(dto_nuevo.longitud):
        coords_anteriores = f"Lat: {sitio_original.lat}, Lon: {sitio_original.lon}"
        coords_nuevas = f"Lat: {dto_nuevo.latitud}, Lon: {dto_nuevo.longitud}"
        _registrar_cambio(
            sitio_original.id_sitio,
            user_id,
            "Edicion",
            "Coordenadas",
            coords_anteriores,
            coords_nuevas,
        )
