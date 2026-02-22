"""Estado Pendiente para reseñas.

Define el comportamiento de una reseña en estado pendiente de aprobación.
"""

from core.estados_resenias.estado_resenia import EstadoResenia
from core.estados_resenias.eliminada import Eliminada


class Pendiente(EstadoResenia):
    """Representa el estado Pendiente de una reseña.

    Una reseña pendiente puede ser aprobada, rechazada o eliminada.
    """

    def aprobar(self):
        """Aprueba una reseña pendiente."""
        from core.estados_resenias.aprobada import (
            Aprobada,
        )

        self.context.modelo.id_estado_resenia = 2
        self.context.estado_actual = Aprobada(self.context)

    def rechazar(self, motivo: str):
        """Rechaza una reseña pendiente.

        Args:
            motivo: Razón del rechazo (obligatorio, máx 200 caracteres).

        Raises:
            ValueError: Si el motivo está vacío o es demasiado largo.
        """
        from core.estados_resenias.rechazada import Rechazada

        if not motivo or not motivo.strip():
            raise ValueError("Motivo obligatorio para rechazar.")
        if len(motivo) > 200:
            raise ValueError("Motivo demasiado largo (máx 200).")
        self.context.modelo.motivo_rechazo = motivo.strip()
        self.context.modelo.id_estado_resenia = 3
        self.context.estado_actual = Rechazada(self.context)

    def eliminar(self):
        """Elimina una reseña pendiente."""
        self.context.modelo.id_estado_resenia = 4
        self.context.estado_actual = Eliminada(self.context)

    def pendiente(self, contenido: str):
        """Intenta cambiar a pendiente una reseña ya pendiente.

        Args:
            contenido: Contenido de la reseña.

        Raises:
            Exception: Siempre, ya que la reseña ya está pendiente.
        """
        raise Exception("La reseña ya está pendiente.")
