"""Modelo de HistorialSitio para auditoría de cambios.

Define el registro histórico de modificaciones realizadas sobre sitios
históricos, con información del usuario, acción realizada y valores previos.
"""

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, ForeignKey, func, String, Text
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.sitios_historicos.sitio_historico import SitioHistorico
    from core.historial.accion import Accion
    from core.auth.usuario import Usuario


class HistorialSitio(Base):
    """Registro de auditoría para cambios en sitios históricos.

    Atributos:
        id_registro: Identificador único autoincremental del registro.
        fecha_hora_modificacion: Fecha y hora de la modificación.
        id_usuario: Usuario que realizó la acción.
        id_sitio: Sitio histórico afectado.
        id_accion: Acción ejecutada.
        campo_modificado: Nombre del campo modificado (si aplica).
        valor_anterior: Valor previo (si aplica).
        valor_nuevo: Valor nuevo (si aplica).

    Relaciones:
        usuario: Relación muchos-a-uno con Usuario.
        sitio_historico: Relación muchos-a-uno con SitioHistorico.
        accion: Relación muchos-a-uno con Accion.
    """

    __tablename__ = "historial_modificaciones_sitios"

    id_registro: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_hora_modificacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_sitio: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id_sitio"), nullable=False
    )
    id_accion: Mapped[int] = mapped_column(
        ForeignKey("acciones.id_accion"), nullable=False
    )
    campo_modificado: Mapped[str] = mapped_column(String(50), nullable=True)
    valor_anterior: Mapped[str] = mapped_column(Text, nullable=True)
    valor_nuevo: Mapped[str] = mapped_column(Text, nullable=True)

    # Relacion Many-to-One 'HistorialSitio-Usuario'.
    usuario: Mapped["Usuario"] = relationship(
        back_populates="historial_modificaciones_sitio"
    )
    # Relacion Many-to-One 'HistorialSitio-SitioHistorico'.
    sitio_historico: Mapped["SitioHistorico"] = relationship(
        back_populates="historial_modificaciones_sitio"
    )
    # Relacion Many-to-One 'HistorialSitio-Accion'.
    accion: Mapped["Accion"] = relationship(
        back_populates="historial_modificaciones_sitio"
    )

    def __repr__(self):
        """Devuelve una representación en string del modelo HistorialSitio."""
        return f"<HistorialSitio(id_registro={self.id_registro})>"
