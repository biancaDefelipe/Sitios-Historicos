"""Modelo de Imagen asociada a sitios históricos.

Define las imágenes que pueden estar asociadas a un sitio histórico,
con información de URL, título alt, descripción y orden de visualización.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Boolean,
    TIMESTAMP,
    String,
    Text,
    ForeignKey,
    func,
    text,
)
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico


class Imagen(Base):
    """
    Representa una imagen asociada a un sitio histórico en la base de datos.

    Almacena metadatos sobre la imagen, su ubicación en el servicio de almacenamiento
    (MinIO), su descripción y su rol (portada, orden) dentro de la galería del sitio.
    """

    __tablename__ = "imagenes"

    id_imagen: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url_publica: Mapped[str] = mapped_column(Text, nullable=False)
    object_name_minio: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    titulo_alt: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(100), nullable=True)
    orden: Mapped[int] = mapped_column(nullable=False)
    es_portada: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
    fecha_hora_alta: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    id_sitio_historico: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id_sitio"), nullable=False
    )

    sitio_historico: Mapped["SitioHistorico"] = relationship(
        "SitioHistorico", back_populates="imagenes"
    )

    def __repr__(self):
        """Representación en string del modelo Imagen."""
        return (
            f"\n<Imagen("
            f"id_imagen={self.id_imagen}, "
            f"titulo_alt={self.titulo_alt}, "
            f"orden={self.orden}, "
            f"es_portada={self.es_portada}, "
            f"fecha_hora_alta={self.fecha_hora_alta})>"
        )

    def to_dto(self) -> dict:
        """Convierte el modelo Imagen a un diccionario/DTO simple."""

        return {
            "id_imagen": self.id_imagen,
            "id_sitio": self.id_sitio_historico,
            "url_publica": self.url_publica,
            "titulo_alt": self.titulo_alt,
            "descripcion": self.descripcion,
            "orden": self.orden,
            "es_portada": self.es_portada,
        }
