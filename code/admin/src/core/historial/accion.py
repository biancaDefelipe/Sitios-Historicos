"""Modelo de Accion para historial de modificaciones de sitios.

Define el modelo SQLAlchemy que representa el tipo de acción realizada sobre un
sitio histórico (crear, editar, borrar, etc.).
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.historial.historial_sitio import HistorialSitio


class Accion(Base):
    """Representa una acción que puede registrarse en el historial de un sitio.

    Atributos:
        id_accion: Identificador único autoincremental de la acción.
        descripcion: Descripción corta de la acción (por ejemplo, "CREAR").

    Relaciones:
        historial_modificaciones_sitio: Relación uno-a-muchos con HistorialSitio.
    """

    __tablename__ = "acciones"

    id_accion: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)

    historial_modificaciones_sitio: Mapped[List["HistorialSitio"]] = relationship(
        back_populates="accion"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Accion."""
        return f"\n<Accion(id_accion={self.id_accion}, descripcion={self.descripcion})>"
