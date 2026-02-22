"""Modelo de Categoria para clasificar sitios históricos.

Define el modelo SQLAlchemy que representa una categoría a la cual pueden
pertenecer los sitios históricos.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico


class Categoria(Base):
    """Representa la categoría de un sitio histórico.

    Atributos:
        id_categoria: Identificador único autoincremental.
        descripcion: Descripción de la categoría.

    Relaciones:
        sitios_historicos: Relación uno-a-muchos con SitioHistorico.
    """

    __tablename__ = "categorias"

    id_categoria: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)

    sitios_historicos: Mapped[List["SitioHistorico"]] = relationship(
        back_populates="categoria"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Categoria."""
        return f"\n<Categoria(id_categoria={self.id_categoria})>"
