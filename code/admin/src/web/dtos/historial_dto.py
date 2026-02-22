"""DTO para representar registros del historial de modificaciones."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistorialDTO:
    """Estructura de datos para exponer el historial de cambios."""

    id_registro: int
    fecha_hora: datetime
    accion: str
    usuario_nombre_completo: str
    sitio_id: int
    sitio_nombre: str
    usuario_id: int

    def to_dict(self):
        """Convierte el DTO a un diccionario serializable para jsonify/JSON."""
        return {
            "id_registro": self.id_registro,
            "fecha_hora": (
                self.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_hora
                else None
            ),
            "accion": self.accion,
            "usuario_nombre_completo": self.usuario_nombre_completo,
            "sitio_id": self.sitio_id,
            "sitio_nombre": self.sitio_nombre,
        }
