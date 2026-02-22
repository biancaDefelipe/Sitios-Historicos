"""Estado Rechazada para reseñas.

Define el comportamiento de una reseña en estado rechazado.
"""

from core.estados_resenias.eliminada import Eliminada
from core.estados_resenias.estado_resenia import EstadoResenia


class Rechazada(EstadoResenia):
    """Representa el estado Rechazada de una reseña.

    Una reseña rechazada puede volver a pendiente o ser eliminada,
    pero no puede ser aprobada ni rechazada nuevamente.
    """

    def aprobar(self):
        """Intenta aprobar una reseña rechazada.

        Raises:
            Exception: Siempre, no se puede aprobar una reseña rechazada.
        """
        raise Exception("No se puede aprobar una reseña rechazada.")

    def rechazar(self, motivo: str):
        """Intenta rechazar una reseña ya rechazada.

        Args:
            motivo: Razón del rechazo.

        Raises:
            Exception: Siempre, la reseña ya está rechazada.
        """
        raise Exception("La reseña ya está rechazada.")

    def pendiente(self, contenido: str):
        """Cambia una reseña rechazada a estado pendiente.

        Args:
            contenido: Nuevo contenido de la reseña.
        """
        from core.estados_resenias.pendiente import Pendiente

        self.context.modelo.id_estado_resenia = 1
        self.context.modelo.contenido = contenido
        self.context.estado_actual = Pendiente(self.context)

    def eliminar(self):
        """Elimina una reseña rechazada."""
        self.context.modelo.id_estado_resenia = 4
        self.context.estado_actual = Eliminada(self.context)
