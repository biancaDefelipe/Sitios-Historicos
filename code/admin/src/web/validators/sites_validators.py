"""
Módulo de validaciones reutilizables para los datos de entrada
de los endpoints relacionados con Sitios (sites) y otros recursos.

Contiene funciones de validación para filtros de fechas, tipos de datos,
y clases validadoras personalizadas para WTForms.
"""

from wtforms.validators import Regexp, ValidationError
from datetime import datetime, time


def validar_filtros(filtros: dict):
    """
    Valida que el argumento 'filtros' sea un diccionario.

    Args:
        filtros (dict): El objeto a validar, que se espera sea un diccionario (JSON).

    Raises:
        TypeError: Si el argumento `filtros` no es una instancia de `dict`.
    """
    if not isinstance(filtros, dict):
        raise TypeError("El campo 'filtros' debe ser un objeto (JSON).")


def validar_rango_fechas(fecha_desde: str, fecha_hasta: str):
    """
    Valida el formato y el orden lógico de un rango de fechas.

    Comprueba que, si ambas fechas están presentes, `fecha_desde` no sea posterior a `fecha_hasta`.
    Asume que el formato de entrada de las fechas es YYYY-MM-DD.

    Args:
        fecha_desde (str): La fecha de inicio del rango (formato YYYY-MM-DD).
        fecha_hasta (str): La fecha de fin del rango (formato YYYY-MM-DD).

    Raises:
        ValueError: Si `fecha_desde` es posterior a `fecha_hasta`.
    """

    f_desde = (
        datetime.combine(datetime.strptime(fecha_desde, "%Y-%m-%d"), time.min)
        if fecha_desde
        else None
    )
    f_hasta = (
        datetime.combine(datetime.strptime(fecha_hasta, "%Y-%m-%d"), time.max)
        if fecha_hasta
        else None
    )
    if fecha_desde and fecha_hasta and f_desde > f_hasta:
        raise ValueError("La fecha_desde no puede ser mayor que la fecha_hasta.")


validate_nombre_propio = Regexp(
    r"^[a-zA-ZñÑáéíóúÁÉÍÓÓúüÜ\s'-]+$",
    message="El campo contiene caracteres no válidos. Solo se permiten letras, espacios, guiones y apóstrofes.",
)
"""
Regexp validator para WTForms que restringe un campo a contener solo letras (incluyendo Ñ y acentos),
espacios, guiones (-) y apóstrofes ('). Ideal para nombres y apellidos.
"""


class InList:
    """
    Validador personalizado para WTForms que verifica si el valor de un campo está dentro de una lista permitida.

    Este validador funciona revisando las opciones (`choices`) configuradas en el campo de WTForms.

    Attributes:
        message (str): El mensaje de error a mostrar si la validación falla.
    """

    def __init__(self, message=None):
        """
        Inicializa el validador InList.

        Args:
            message (str, optional): Mensaje de error personalizado.
                                     Defaults a "El valor seleccionado no es válido.".
        """
        if not message:
            message = "El valor seleccionado no es válido."
        self.message = message

    def __call__(self, form, field):
        """
        Realiza la validación.

        Args:
            form: El formulario que se está validando.
            field: El campo de formulario a validar.

        Raises:
            ValidationError: Si el valor del campo no se encuentra en la lista de opciones válidas (`field.choices`).
        """
        valid_options = [choice[0] for choice in field.choices]
        if field.data not in valid_options:
            raise ValidationError(self.message)
