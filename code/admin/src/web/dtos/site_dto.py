"""DTOs para transferencia de datos de Sitios Históricos."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class SiteDTO:
    """Objeto para la transferencia de datos de Sitios Históricos."""

    nombre: str
    descripcion_breve: str
    ciudad: str
    provincia: str
    latitud: float
    longitud: float
    tags: Optional[List[str]] = field(default_factory=list)
    descripcion_detallada: str | None = None
    anio_inauguracion: int | None = None
    visible: bool | None = None
    eliminado: bool | None = None
    categoria: str | None = None
    estado: str | None = None
    ciudad_id: int | None = None
    categoria_id: int | None = None
    estado_id: int | None = None
    id: int | None = None
    fecha_hora_alta: datetime | None = None
    url_portada: str | None = None
    alt_portada: str | None = None
    images: Optional[List[Dict[str, Any]]] = field(default_factory=list)

    def to_dict(self):
        """Convierte el DTO a un diccionario serializable (p.ej., para JSON)."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion_breve": self.descripcion_breve,
            "descripcion_detallada": self.descripcion_detallada,
            "anio_inauguracion": self.anio_inauguracion,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "visible": self.visible,
            "categoria": self.categoria,
            "estado": self.estado,
            "tags": self.tags,
            "fecha_hora_alta": self.fecha_hora_alta,
            "url_portada": self.url_portada,
            "alt_portada": self.alt_portada,
            "images": self.images,
        }
