"""Modelos de localidad: Ciudad.

Define el modelo SQLAlchemy para ciudades y su relación con provincias y
sitios históricos.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico
    from core.localidad.provincia import Provincia


class Ciudad(Base):
    """Representa una ciudad perteneciente a una provincia.

    Atributos:
        id_ciudad: Identificador único autoincremental de la ciudad.
        nombre: Nombre de la ciudad.
        id_provincia: Clave foránea a la provincia.

    Relaciones:
        sitios_historicos: Relación uno-a-muchos con SitioHistorico.
        provincia: Relación muchos-a-uno con Provincia.
    """

    __tablename__ = "ciudades"
    __table_args__ = (
        UniqueConstraint("nombre", "id_provincia", name="uq_ciudad_provincia"),
        {"extend_existing": True},
    )

    id_ciudad: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    id_provincia: Mapped[int] = mapped_column(
        ForeignKey("provincias.id_provincia"), nullable=False
    )

    # Relación One-to-Many 'Ciudad-SitioHistorico'.
    sitios_historicos: Mapped[List["SitioHistorico"]] = relationship(
        back_populates="ciudad"
    )
    # Relación Many-to-One 'Ciudad-Provincia'.
    provincia: Mapped["Provincia"] = relationship(
        "Provincia", back_populates="ciudades"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Ciudad."""
        return f"\n<Ciudad(id_ciudad={self.id_ciudad})>"
