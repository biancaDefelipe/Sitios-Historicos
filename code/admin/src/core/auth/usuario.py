"""Modelos de autenticación: entidad de Usuario.

Este módulo define el modelo SQLAlchemy para los usuarios del sistema y sus
relaciones con roles, feature flags y el historial de modificaciones.
"""

from ..database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Boolean,
    TIMESTAMP,
    String,
    ForeignKey,
    func,
    text,
)
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from core.sitios_historicos.sitio_historico import favoritos

if TYPE_CHECKING:
    from .rol import Rol
    from ..flags.feature_flag_usuario import FeatureFlagUsuario
    from ..historial.historial_sitio import HistorialSitio
    from ..resenias.resenia import Resenia
    from core.sitios_historicos.sitio_historico import SitioHistorico


class Usuario(Base):
    """Representa a una persona usuaria del sistema.

    Atributos:
        id_usuario: Identificador único autoincremental.
        email: Correo electrónico único del usuario.
        password: Hash de la contraseña.
        nombre: Nombre del usuario.
        apellido: Apellido del usuario.
        activo: Indica si la cuenta está activa.
        es_admin: Indica si posee privilegios de administración.
        eliminado: Borrado lógico del registro.
        fecha_hora_alta: Fecha y hora de creación.
        fecha_hora_modificacion: Fecha y hora de última modificación.
        id_rol: Clave foránea al rol asignado.

    Relaciones:
        rol: Relación muchos-a-uno con Rol.
        modificaciones_feature_flags: Relación uno-a-muchos con FeatureFlagUsuario.
        historial_modificaciones_sitio: Relación uno-a-muchos con HistorialSitio.
    """

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("TRUE"), nullable=False
    )
    es_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
    eliminado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("FALSE"), nullable=False
    )
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
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), nullable=True)

    # Relación Many-to-One 'Usuario-Rol'.
    rol: Mapped["Rol"] = relationship(back_populates="usuarios")
    # Relación One-to-Many 'Usuario-FeatureFlagUsuario'.
    modificaciones_feature_flags: Mapped[List["FeatureFlagUsuario"]] = relationship(
        back_populates="usuario"
    )
    # Relación One-to-Many 'Usuario-HistorialSitio'.
    historial_modificaciones_sitio: Mapped[List["HistorialSitio"]] = relationship(
        back_populates="usuario"
    )
    # Relación One-to-Many 'Usuario-Resenias'.
    resenias: Mapped[List["Resenia"]] = relationship(
        "Resenia", back_populates="usuario"
    )
    # Relación Many-to-Many 'Usuario-SitioHistorico'.
    sitios_favoritos: Mapped[List["SitioHistorico"]] = relationship(
        secondary=favoritos, back_populates="usuarios_favoritos"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Usuario."""
        return f"\n<Usuario(id={self.id_usuario}, email={self.email})>"
