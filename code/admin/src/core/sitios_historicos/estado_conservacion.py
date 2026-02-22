"""Modelo de EstadoConservacion de sitios históricos.

Define el modelo SQLAlchemy que representa el estado de conservación de un
sitio histórico (por ejemplo, bueno, regular, malo).
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico


class EstadoConservacion(Base):
    """Representa el estado de conservación de un sitio histórico.

    Atributos:
        id_estado_cons: Identificador único autoincremental del estado.
        descripcion: Descripción del estado de conservación.

    Relaciones:
        sitios_historicos: Relación uno-a-muchos con SitioHistorico.
    """

    __tablename__ = "estados_conservacion"

    id_estado_cons: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)

    sitios_historicos: Mapped[List["SitioHistorico"]] = relationship(
        back_populates="estado_conservacion"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo EstadoConservacion."""
        return f"\n<EstadoConservacion(id_estado_cons={self.id_estado_cons})>"
