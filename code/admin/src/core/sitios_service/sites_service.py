"""Servicios de dominio para Sitios Históricos.

Capa de orquestación entre controladores y repositorios para validar y
coordinar operaciones sobre sitios históricos.
"""

from flask import current_app
from web.dtos.site_dto import SiteDTO


def _repo():
    """Obtiene la instancia de repositorio configurada en la app."""
    return current_app.config["SITE_REPO"]


def get_site(site_id: int) -> SiteDTO | None:
    """Devuelve el sitio por ID o ``None`` si no existe."""
    return _repo().get(site_id)


def update_site(site_id: int, dto: SiteDTO) -> SiteDTO:
    """Valida datos y delega la actualización del sitio al repositorio."""

    if not dto.nombre or not dto.nombre.strip():
        raise ValueError("El nombre es obligatorio.")

    if not dto.descripcion_breve or not dto.descripcion_breve.strip():
        raise ValueError("La descripción breve es obligatoria.")

    if not dto.descripcion_detallada or not dto.descripcion_detallada.strip():
        raise ValueError("La descripción detallada es obligatoria.")

    if dto.anio_inauguracion is None:
        raise ValueError("El año de inauguración es obligatorio.")

    if dto.latitud is None or dto.longitud is None:
        raise ValueError("La latitud y longitud son obligatorias.")

    if dto.ciudad_id is None:
        raise ValueError(
            f"La Ciudad '{dto.ciudad}' en Provincia '{dto.provincia}' no se encontró."
        )

    if dto.categoria_id is None:
        raise ValueError(f"La Categoría '{dto.categoria}' no fue encontrada.")

    if dto.estado_id is None:
        raise ValueError(f"El Estado '{dto.estado}' no fue encontrado.")

    return _repo().update(site_id, dto)


def delete_site(site_id: int) -> None:
    """Elimina (o marca eliminado) un sitio por ID."""
    return _repo().delete(site_id)


def export_sites(
    q: str | None,
    categoria: str | None,
    estado: str | None,
    order: str | None,
    limit: int = 10000,
):
    """Obtiene un conjunto extendido de sitios para exportación."""

    filtros = {
        "q": q,
        "categoria": categoria,
        "estado": estado,
    }

    orden = order

    items, _ = _repo().list(
        filtros=filtros,
        orden=orden,
        page=1,
        per_page=limit,
        all=True,
    )
    return items


def list_sites(
    q=None,
    categoria=None,
    estado=None,
    order=None,
    page=1,
    per_page=None,
):
    """Obtiene sitios paginados aplicando filtros."""

    filtros = {
        "q": q,
        "categoria": categoria,
        "estado": estado,
    }

    orden = order

    return _repo().list(
        filtros=filtros,
        orden=orden,
        page=page,
        per_page=per_page,
    )


def listar_categorias() -> list[dict]:
    """Devuelve el listado de categorías disponibles."""
    return _repo().listar_categorias()


def listar_estados() -> list[dict]:
    """Devuelve el listado de estados posibles de un sitio."""
    return _repo().listar_estados()


def listar_provincias() -> list[dict]:
    """Devuelve el listado de provincias registradas."""
    return _repo().listar_provincias()


def obtener_categoria_id(nombre_categoria: str) -> int | None:
    """Obtiene el ID de una categoría a partir de su nombre."""
    return _repo().obtener_categoria_id(nombre_categoria)


def obtener_estado_id(nombre_estado: str) -> int | None:
    """Obtiene el ID de un estado a partir de su nombre."""
    return _repo().obtener_estado_id(nombre_estado)


def obtener_tags_sitio(site_id: int) -> list[str]:
    """Devuelve los tags asociados a un sitio."""
    return _repo().obtener_tags_sitio(site_id)


def obtener_categoria_nombre(categoria_id: int) -> str | None:
    """Obtiene el nombre de una categoría a partir de su ID."""
    return _repo().obtener_categoria_nombre(categoria_id)


def obtener_estado_nombre(estado_id: int) -> str | None:
    """Obtiene el nombre de un estado a partir de su ID."""
    return _repo().obtener_estado_nombre(estado_id)
