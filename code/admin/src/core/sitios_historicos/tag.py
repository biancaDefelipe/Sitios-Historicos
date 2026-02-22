"""Modelo de Tag para etiquetar sitios históricos.

Define el modelo SQLAlchemy para etiquetas (tags) que pueden asociarse a uno o
varios sitios históricos.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, TIMESTAMP, func
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from core.sitios_historicos.sitio_historico import sitios_tags

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico


class Tag(Base):
    """Representa una etiqueta asignable a sitios históricos.

    Atributos:
        id_tag: Identificador único autoincremental de la etiqueta.
        nombre: Nombre visible de la etiqueta.
        slug: Identificador URL-amigable único.
        fecha_hora_alta: Fecha y hora de creación.
        fecha_hora_modificacion: Fecha y hora de última modificación.

    Relaciones:
        sitios_historicos: Relación muchos-a-muchos con SitioHistorico.
    """

    __tablename__ = "tags"

    id_tag: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
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

    sitios_historicos: Mapped[List["SitioHistorico"]] = relationship(
        secondary=sitios_tags, back_populates="tags"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Tag."""
        return f"<Tag(id_tag={self.id_tag})>"
