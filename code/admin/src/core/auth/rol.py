"""Modelo de Rol y asociación con permisos y usuarios.

Este módulo define el modelo SQLAlchemy para roles de usuario y la tabla
asociativa que vincula roles con permisos.
"""

from ..database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .usuario import Usuario
    from .permiso import Permiso

roles_permisos = Table(
    "roles_permisos",
    Base.metadata,
    Column("id_rol", ForeignKey("roles.id_rol"), primary_key=True),
    Column("id_permiso", ForeignKey("permisos.id_permiso"), primary_key=True),
)


class Rol(Base):
    """Rol asignado a usuarios, con permisos asociados.

    Atributos:
        id_rol: Identificador único autoincremental del rol.
        descripcion: Descripción del rol.

    Relaciones:
        usuarios: Relación uno-a-muchos con Usuario.
        permisos: Relación muchos-a-muchos con Permiso mediante ``roles_permisos``.
    """

    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)
    es_bloqueable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    es_asignable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    es_prescindible: Mapped[bool] = mapped_column(Boolean, nullable=False)

    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="rol")
    permisos: Mapped[List["Permiso"]] = relationship(
        secondary=roles_permisos, back_populates="roles"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Rol."""
        return f"\n<Rol(id_rol={self.id_rol}, descripcion={self.descripcion})>"
