"""Modelo de asociación entre FeatureFlag y Usuario.

Registra las modificaciones de estado de una FeatureFlag realizadas por un
usuario en un momento dado.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, TIMESTAMP, ForeignKey, func
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.flags.feature_flag import FeatureFlag
    from core.auth.usuario import Usuario


class FeatureFlagUsuario(Base):
    """Asociación que registra cambios de flags por usuario.

    Atributos:
        id_registro: Identificador único autoincremental del registro.
        fecha_hora_modificacion: Fecha y hora de la modificación.
        id_flag: Identificador de la FeatureFlag modificada.
        id_usuario: Identificador del Usuario que modificó la flag.

    Relaciones:
        usuario: Relación muchos-a-uno con Usuario.
        feature_flag: Relación muchos-a-uno con FeatureFlag.
    """

    __tablename__ = "feature_flags_usuarios"

    id_registro: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_hora_modificacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    id_flag: Mapped[int] = mapped_column(
        ForeignKey("feature_flags.id_flag"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), nullable=False
    )

    # Relacion Many-to-One 'FeatureFlagUsuario-Usuario'.
    usuario: Mapped["Usuario"] = relationship(
        back_populates="modificaciones_feature_flags"
    )
    # Relacion Many-to-One 'FeatureFlagUsuario-FeatureFlag'.
    feature_flag: Mapped["FeatureFlag"] = relationship(
        back_populates="modificaciones_usuarios"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo FeatureFlagUsuario."""
        return f"<FeatureFlagUsuario(id={self.id_registro}, id_flag={self.id_flag})>"
