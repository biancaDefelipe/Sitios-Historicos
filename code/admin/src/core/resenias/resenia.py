"""Modelo de la entidad Reseña.

Define la estructura de datos para las reseñas de sitios históricos,
incluyendo calificación, contenido, estado y relaciones con usuarios y sitios.
"""

from ..database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    TIMESTAMP,
    String,
    Text,
    ForeignKey,
    func,
)
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sitios_historicos.sitio_historico import SitioHistorico
    from ..auth.usuario import Usuario
    from ..resenias.estado_resenia import EstadoResenia


class Resenia(Base):
    """Modelo de la entidad Reseña.

    Representa una reseña realizada por un usuario sobre un sitio histórico,
    con su calificación, contenido, estado y fecha de creación.
    """

    __tablename__ = "resenias"

    id_resenia: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calificacion: Mapped[int] = mapped_column(Integer, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    motivo_rechazo: Mapped[str] = mapped_column(String(200), nullable=True)
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
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_sitio_historico: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id_sitio"), nullable=False
    )
    id_estado_resenia: Mapped[int] = mapped_column(
        ForeignKey("estados_resenias.id_estado_resenia"), nullable=False
    )

    # Relacion Many-to-One 'Resenia-SitioHistorico'.
    sitio_historico: Mapped["SitioHistorico"] = relationship(
        "SitioHistorico", back_populates="resenias"
    )
    # Relacion Many-to-One 'Resenia-Usuario'.
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="resenias")
    # Relación Many-to-One 'Resenia-EstadoResenia'.
    estado_resenia: Mapped["EstadoResenia"] = relationship(
        "EstadoResenia", back_populates="resenias"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo Resenia."""
        return f"\n<Resenia(id_resenia={self.id_resenia}, calificacion={self.calificacion}, id_estado_resenia={self.id_estado_resenia}, fecha_hora_alta={self.fecha_hora_alta})>"

    def serialize(self):
        """Serializa la entidad a un diccionario.

        :return: Diccionario con los datos de la reseña.
        """
        return {
            "id_resenia": self.id_resenia,
            "calificacion": self.calificacion,
            "contenido": self.contenido,
            "motivo_rechazo": self.motivo_rechazo,
            "fecha_hora_alta": self.fecha_hora_alta.strftime("%Y-%m-%d %H:%M:%S"),
            "email_usuario": self.usuario.email,
            "nombre_sitio_historico": self.sitio_historico.nombre,
            "descripcion_estado": self.estado_resenia.descripcion,
            "id_estado_resenia": self.id_estado_resenia,
            "sitio_ciudad": self.sitio_historico.ciudad.nombre,
            "sitio_provincia": self.sitio_historico.ciudad.provincia.nombre,
        }
