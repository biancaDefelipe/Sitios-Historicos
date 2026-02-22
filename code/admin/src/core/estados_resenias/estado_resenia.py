"""Clase abstracta base para estados de reseñas.

Define la interfaz común para todos los estados de una reseña
usando el patrón State.
"""

from abc import ABC, abstractmethod


class EstadoResenia(ABC):
    """Clase abstracta que define el comportamiento de un estado de reseña.

    Atributos:
        context: Instancia de ReseniaContexto que mantiene el estado actual.
    """

    def __init__(self, context):
        """Inicializa el estado con su contexto.

        Args:
            context: Instancia de ReseniaContexto.
        """
        self.context = context

    @abstractmethod
    def aprobar(self):
        """Aprueba la reseña si el estado lo permite."""
        ...

    @abstractmethod
    def rechazar(self, motivo: str):
        """Rechaza la reseña con un motivo.

        Args:
            motivo: Razón del rechazo.
        """
        ...

    @abstractmethod
    def eliminar(self):
        """Elimina la reseña si el estado lo permite."""
        ...

    @abstractmethod
    def pendiente(self, contenido: str):
        """Cambia la reseña a estado pendiente.

        Args:
            contenido: Nuevo contenido de la reseña.
        """
        ...
