"""Modelo de FeatureFlag para gestión de funcionalidades.

Define el modelo SQLAlchemy para flags de funcionalidades, que permiten activar
o desactivar comportamientos específicos en el sistema.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Text, text
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.flags.feature_flag_usuario import FeatureFlagUsuario


class FeatureFlag(Base):
    """Representa una bandera de funcionalidad configurable.

    Atributos:
        id_flag: Identificador único autoincremental de la flag.
        nombre: Nombre único de la flag.
        estado: Estado por defecto de la flag (activada/desactivada).
        descripcion: Descripción del propósito de la flag.
        mensaje_mantenimiento: Mensaje a mostrar en caso de mantenimiento.

    Relaciones:
        modificaciones_usuarios: Relación uno-a-muchos con FeatureFlagUsuario.
    """

    __tablename__ = "feature_flags"

    id_flag: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    estado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    mensaje_mantenimiento: Mapped[str] = mapped_column(String(100), nullable=False)

    modificaciones_usuarios: Mapped[List["FeatureFlagUsuario"]] = relationship(
        back_populates="feature_flag"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo FeatureFlag."""
        return f"\n<FeatureFlag(id={self.id_flag}, nombre={self.nombre})>"
