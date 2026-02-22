"""Modelos de localidad: Provincia.

Define el modelo SQLAlchemy para provincias y su relación con ciudades.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.localidad.ciudad import Ciudad


class Provincia(Base):
    """Representa una provincia dentro del sistema de localidades.

    Atributos:
        id_provincia: Identificador único autoincremental de la provincia.
        nombre: Nombre de la provincia.

    Relaciones:
        ciudades: Relación uno-a-muchos con Ciudad.
    """

    __tablename__ = "provincias"
    __table_args__ = {"extend_existing": True}

    id_provincia: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    ciudades: Mapped[List["Ciudad"]] = relationship(
        "Ciudad", back_populates="provincia"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Provincia."""
        return f"\n<Provincia(id_provincia={self.id_provincia}, nombre={self.nombre})>"
