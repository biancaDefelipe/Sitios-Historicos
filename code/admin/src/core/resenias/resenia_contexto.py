"""Contexto del patrón State para las reseñas.

Implementa el patrón State para gestionar los cambios de estado de las reseñas,
delegando el comportamiento al estado actual.
"""

from core.estados_resenias.pendiente import Pendiente
from core.estados_resenias.aprobada import Aprobada
from core.estados_resenias.rechazada import Rechazada
from core.estados_resenias.eliminada import Eliminada


class ReseniaContexto:
    """Contexto del patrón State para las reseñas.

    Mantiene una referencia al modelo de reseña y al estado actual,
    delegando las operaciones de cambio de estado al objeto estado correspondiente.
    """

    def __init__(self, modelo_resenia):
        """Inicializa el contexto con el modelo de reseña.

        :param modelo_resenia: Instancia del modelo Resenia.
        """
        self.modelo = modelo_resenia
        self.estado_actual = self._estado_desde_modelo()

    def _estado_desde_modelo(self):
        """Crea el objeto de estado correspondiente según el id_estado_resenia.

        :return: Instancia del estado correspondiente.
        """
        id_estado = getattr(self.modelo, "id_estado_resenia", None)
        map_local = {1: Pendiente, 2: Aprobada, 3: Rechazada, 4: Eliminada}
        cls = map_local.get(id_estado, Pendiente)

        return cls(self)

    def aprobar(self):
        """Delega la aprobación de la reseña al estado actual."""
        self.estado_actual.aprobar()

    def rechazar(self, motivo: str):
        """Delega el rechazo de la reseña al estado actual.

        :param motivo: Motivo del rechazo.
        """
        self.estado_actual.rechazar(motivo)

    def eliminar(self):
        """Delega la eliminación de la reseña al estado actual."""
        self.estado_actual.eliminar()

    def pendiente(self, contenido: str):
        """Delega el cambio a estado pendiente al estado actual.

        :param contenido: Nuevo contenido de la reseña.
        """
        self.estado_actual.pendiente(contenido)
