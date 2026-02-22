"""Modelo principal de SitioHistorico.

Representa un sitio histórico con su información básica, ubicación geográfica
y relaciones con ciudad, categoría, estado de conservación, historial y tags.
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
    Table,
    Column,
)
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

if TYPE_CHECKING:
    from core.localidad.ciudad import Ciudad
    from core.sitios_historicos.categoria import Categoria
    from core.sitios_historicos.estado_conservacion import EstadoConservacion
    from core.historial.historial_sitio import HistorialSitio
    from core.sitios_historicos.tag import Tag
    from core.resenias.resenia import Resenia
    from core.sitios_historicos.imagen import Imagen
    from core.auth.usuario import Usuario

sitios_tags = Table(
    "sitios_tags",
    Base.metadata,
    Column(
        "id_sitio",
        ForeignKey("sitios_historicos.id_sitio", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_tag",
        ForeignKey("tags.id_tag", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,
)

favoritos = Table(
    "favoritos",
    Base.metadata,
    Column(
        "id_usuario",
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_sitio",
        ForeignKey("sitios_historicos.id_sitio", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,
)


class SitioHistorico(Base):
    """Entidad que modela un sitio histórico.

    Atributos:
        id_sitio: Identificador único del sitio.
        nombre: Nombre del sitio histórico.
        descripcion_breve: Descripción corta.
        descripcion_completa: Descripción extendida del sitio.
        anio_inauguracion: Año de inauguración.
        location: Geometría tipo POINT (SRID 4326) con coordenadas lat/lon.
        es_visible: Indica si el sitio es visible públicamente.
        eliminado: Borrado lógico del registro.
        fecha_hora_alta: Fecha y hora de creación.
        fecha_hora_modificacion: Fecha y hora de última modificación.
        id_ciudad: Clave foránea a Ciudad.
        id_categoria: Clave foránea a Categoria.
        id_estado_cons: Clave foránea a EstadoConservacion.

    Relaciones:
        ciudad: Relación muchos-a-uno con Ciudad.
        categoria: Relación muchos-a-uno con Categoria.
        estado_conservacion: Relación muchos-a-uno con EstadoConservacion.
        historial_modificaciones_sitio: Relación uno-a-muchos con HistorialSitio.
        tags: Relación muchos-a-muchos con Tag.
    """

    __tablename__ = "sitios_historicos"

    id_sitio: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion_breve: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion_completa: Mapped[str] = mapped_column(Text, nullable=False)
    anio_inauguracion: Mapped[int] = mapped_column(nullable=False)

    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    es_visible: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
    eliminado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
    fecha_hora_alta: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    fecha_hora_modificacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=None,
        server_default=None,
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    id_ciudad: Mapped[int] = mapped_column(
        ForeignKey("ciudades.id_ciudad"), nullable=False
    )
    id_categoria: Mapped[int] = mapped_column(
        ForeignKey("categorias.id_categoria"), nullable=False
    )
    id_estado_cons: Mapped[int] = mapped_column(
        ForeignKey("estados_conservacion.id_estado_cons"), nullable=False
    )

    # Relación Many-to-One 'SitioHistorico-Ciudad'.
    ciudad: Mapped["Ciudad"] = relationship(
        "Ciudad", back_populates="sitios_historicos"
    )
    # Relación Many-to-One 'SitioHistorico-Categoria'.
    categoria: Mapped["Categoria"] = relationship(
        "Categoria", back_populates="sitios_historicos"
    )
    # Relación Many-to-One 'SitioHistorico-EstadoConservacion'.
    estado_conservacion: Mapped["EstadoConservacion"] = relationship(
        "EstadoConservacion", back_populates="sitios_historicos"
    )
    # Relación One-to-Many 'SitioHistorico-HistorialSitio'.
    historial_modificaciones_sitio: Mapped[List["HistorialSitio"]] = relationship(
        "HistorialSitio", back_populates="sitio_historico"
    )
    # Relación Many-to-Many 'SitioHistorico-Tag'.
    tags: Mapped[List["Tag"]] = relationship(
        secondary=sitios_tags,
        back_populates="sitios_historicos",
        cascade="save-update",
    )
    # Relación One-to-Many 'SitioHistorico-Resenia'.
    resenias: Mapped[List["Resenia"]] = relationship(
        "Resenia", back_populates="sitio_historico"
    )
    # Relación One-to-Many 'SitioHistorico-Imagen'.
    imagenes: Mapped[List["Imagen"]] = relationship(
        "Imagen", back_populates="sitio_historico"
    )
    # Relación Many-to-Many 'SitioHistorico-Usuario'.
    usuarios_favoritos: Mapped[List["Usuario"]] = relationship(
        secondary=favoritos, back_populates="sitios_favoritos"
    )

    @property
    def lat(self) -> float | None:
        """Latitud del sitio a partir de la geometría WKB.

        Returns:
            float | None: Latitud si existen coordenadas, de lo contrario None.
        """
        if self.location is None:
            return None
        punto = to_shape(self.location)
        return punto.y

    @property
    def lon(self) -> float | None:
        """Longitud del sitio a partir de la geometría WKB.

        Returns:
            float | None: Longitud si existen coordenadas, de lo contrario None.
        """
        if self.location is None:
            return None
        punto = to_shape(self.location)
        return punto.x

    def __repr__(self):
        """Devuelve una representación en string del modelo SitioHistorico."""
        return (
            f"\n<SitioHistorico("
            f"id_sitio={self.id_sitio}, "
            f"nombre={self.nombre}, "
            f"anio_inauguracion={self.anio_inauguracion}, "
            f"lat={self.lat}, lon={self.lon}, "
            f"es_visible={self.es_visible})>"
        )

    def to_list_dto(self):
        """
        DTO optimizado para la vista de listado.
        Incluye la URL de la portada (que fue precargada eficientemente).
        """

        portada_obj = self.imagenes[0] if self.imagenes else None

        return {
            "id_sitio": self.id_sitio,
            "nombre": self.nombre,
            "descripcion_breve": self.descripcion_breve,
            "descripcion_detallada": self.descripcion_completa,
            "anio_inauguracion": self.anio_inauguracion,
            "url_portada": portada_obj.url_publica if portada_obj else None,
            "alt_portada": (
                portada_obj.titulo_alt if portada_obj else f"Imagen de {self.nombre}"
            ),
            "ciudad": self.ciudad.nombre if self.ciudad else "N/A",
            "provincia": (
                self.ciudad.provincia.nombre
                if self.ciudad and self.ciudad.provincia
                else "N/A"
            ),
            "categoria": (self.categoria.descripcion if self.categoria else "N/A"),
            "estado": (
                self.estado_conservacion.descripcion
                if self.estado_conservacion
                else "N/A"
            ),
            "latitud": self.lat,
            "longitud": self.lon,
            "es_visible": self.es_visible,
            "eliminado": self.eliminado,
            "tags": [tag.nombre for tag in self.tags] if self.tags else [],
            "fecha_hora_alta": self.fecha_hora_alta.strftime("%Y-%m-%d %H:%M:%S"),
        }
