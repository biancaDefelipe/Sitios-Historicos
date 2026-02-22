"""Estado Eliminada para reseñas.

Define el comportamiento de una reseña en estado eliminado.
"""

from core.estados_resenias.estado_resenia import EstadoResenia


class Eliminada(EstadoResenia):
    """Representa el estado Eliminada de una reseña.

    Una reseña eliminada no permite ninguna transición de estado.
    """

    def aprobar(self):
        """Intenta aprobar una reseña eliminada.

        Raises:
            Exception: Siempre, la reseña está eliminada.
        """
        raise Exception("La reseña está eliminada.")

    def rechazar(self, motivo: str):
        """Intenta rechazar una reseña eliminada.

        Args:
            motivo: Razón del rechazo.

        Raises:
            Exception: Siempre, la reseña está eliminada.
        """
        raise Exception("La reseña está eliminada.")

    def eliminar(self):
        """Intenta eliminar una reseña ya eliminada.

        Raises:
            Exception: Siempre, la reseña ya está eliminada.
        """
        raise Exception("La reseña está eliminada.")

    def pendiente(self, contenido: str):
        """Intenta cambiar a pendiente una reseña eliminada.

        Args:
            contenido: Contenido de la reseña.

        Raises:
            Exception: Siempre, la reseña está eliminada.
        """
        raise Exception("La reseña está eliminada.")
