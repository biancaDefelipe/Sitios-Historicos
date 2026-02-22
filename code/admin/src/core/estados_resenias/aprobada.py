"""Estado Aprobada para reseñas.

Define el comportamiento de una reseña en estado aprobado.
"""

from core.estados_resenias.eliminada import Eliminada
from core.estados_resenias.estado_resenia import EstadoResenia


class Aprobada(EstadoResenia):
    """Representa el estado Aprobada de una reseña.

    Una reseña aprobada puede ser eliminada o volver a pendiente,
    pero no puede ser rechazada ni aprobada nuevamente.
    """

    def aprobar(self):
        """Intenta aprobar una reseña ya aprobada.

        Raises:
            Exception: Siempre, ya que la reseña ya está aprobada.
        """
        raise Exception("Ya está aprobada.")

    def rechazar(self, motivo: str):
        """Intenta rechazar una reseña aprobada.

        Args:
            motivo: Razón del rechazo.

        Raises:
            Exception: Siempre, no se puede rechazar una reseña aprobada.
        """
        raise Exception("No se puede rechazar una aprobada.")

    def eliminar(self):
        """Elimina una reseña aprobada."""
        self.context.modelo.id_estado_resenia = 4
        self.context.estado_actual = Eliminada(self.context)

    def pendiente(self, contenido: str):
        """Cambia una reseña aprobada a estado pendiente.

        Args:
            contenido: Nuevo contenido de la reseña.
        """
        from core.estados_resenias.pendiente import Pendiente

        self.context.modelo.id_estado_resenia = 1
        self.context.modelo.contenido = contenido
        self.context.estado_actual = Pendiente(self.context)
