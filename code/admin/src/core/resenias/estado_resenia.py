"""Modelo de la entidad Estado de Reseña.

Define los posibles estados en los que puede encontrarse una reseña
(pendiente, aprobada, rechazada, eliminada).
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..resenias.resenia import Resenia


class EstadoResenia(Base):
    """Modelo de la entidad Estado de Reseña.

    Representa los diferentes estados que puede tener una reseña en el sistema.
    """

    __tablename__ = "estados_resenias"

    id_estado_resenia: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)

    resenias: Mapped[List["Resenia"]] = relationship(back_populates="estado_resenia")

    def __repr__(self):
        """Devuelve una representación en string del modelo EstadoResenia."""
        return f"\n<EstadoResenia(id_estado_resenia={self.id_estado_resenia}, descripcion={self.descripcion})>"
