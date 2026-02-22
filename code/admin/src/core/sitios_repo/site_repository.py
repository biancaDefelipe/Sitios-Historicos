"""Interfaces y repositorios de Sitios Históricos.

Define la interfaz abstracta ``SiteRepository``, siguiendo el patrón Repository,
"""

import abc
from typing import List

from web.dtos.site_dto import SiteDTO


class SiteRepository(abc.ABC):
    """
    Interfaz abstracta para el repositorio de sitios.

    Define el contrato que cualquier implementación de repositorio
    (SQL, NoSQL, memoria, etc.) debe cumplir.
    """

    @abc.abstractmethod
    def create(self, dto: SiteDTO) -> SiteDTO:
        """Crea un sitio y devuelve su DTO persistido."""
        pass

    @abc.abstractmethod
    def get(self, site_id: int) -> SiteDTO | None:
        """Obtiene un sitio por ID o None si no existe."""
        pass

    @abc.abstractmethod
    def list(
        self,
        filtros: dict | None = None,
        orden: str | None = None,
        page: int = 1,
        per_page: int | None = None,
        all: bool = False,
    ) -> tuple[list[SiteDTO], int]:
        """
        Lista sitios con filtros, orden y paginación.

        :param filtros: Diccionario de filtros (q, categoria, estado).
        :param orden: Criterio de ordenamiento.
        :param page: Página (1-based).
        :param per_page: Elementos por página.
        :param all: Si es True, ignora paginación.
        :returns: (items, total_pages)
        """
        pass

    @abc.abstractmethod
    def listar_para_exportar(self, filtros=None, orden=None) -> List[SiteDTO]:
        """Devuelve todos los sitios para exportación."""
        pass

    @abc.abstractmethod
    def update(self, site_id: int, dto: SiteDTO) -> SiteDTO:
        """Actualiza un sitio existente."""
        pass

    @abc.abstractmethod
    def delete(self, site_id: int):
        """Elimina (o marca eliminado) un sitio."""
        pass
