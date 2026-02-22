"""Modelo de Permiso para control de acceso.

Define el modelo SQLAlchemy que representa un permiso del sistema y su
relación muchos-a-muchos con los roles.
"""

from ..database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING
from core.auth.rol import roles_permisos

if TYPE_CHECKING:
    from .rol import Rol


class Permiso(Base):
    """Representa un permiso que puede ser asignado a uno o más roles.

    Atributos:
        id_permiso: Identificador único autoincremental del permiso.
        descripcion: Descripción corta del permiso.

    Relaciones:
        roles: Relación muchos-a-muchos con Rol mediante la tabla asociativa
            ``roles_permisos``.
    """

    __tablename__ = "permisos"

    id_permiso: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)

    roles: Mapped[List["Rol"]] = relationship(
        secondary=roles_permisos, back_populates="permisos"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Permiso."""
        return (
            f"\n<Permiso(id={self.id_permiso}, descripcion={self.descripcion})>"
        )
