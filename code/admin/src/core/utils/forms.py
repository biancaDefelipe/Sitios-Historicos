"""Formularios WTForms para gestión de sitios históricos en el admin.

Define el formulario principal ``SiteForm`` y validaciones personalizadas.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
    Regexp,
)
from datetime import date
from web.validators.sites_validators import validate_nombre_propio, InList
import json
import re

TAG_REGEX = re.compile(r"^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚüÜ\s-]+$")


class SiteForm(FlaskForm):
    """Formulario para alta/edición de sitios históricos."""

    nombre = StringField(
        "Nombre del sitio",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=100),
            validate_nombre_propio,
        ],
    )
    descripcion_breve = TextAreaField(
        "Descripción breve",
        validators=[
            DataRequired(message="La descripción breve es obligatoria."),
            Length(max=100),
        ],
    )
    descripcion_detallada = TextAreaField(
        "Descripción detallada",
        validators=[DataRequired(message="La descripción detallada es obligatoria.")],
    )
    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(max=100),
            validate_nombre_propio,
        ],
    )

    provincia = SelectField(
        "Provincia",
        validators=[
            DataRequired(message="La provincia es obligatoria."),
            InList(message="La provincia seleccionada no es válida."),
        ],
    )
    estado = SelectField(
        "Estado de conservación",
        validators=[
            DataRequired(message="El estado es obligatorio."),
            InList(message="El estado seleccionado no es válido."),
        ],
    )
    categoria = SelectField(
        "Categoría",
        validators=[
            DataRequired(message="La categoría es obligatoria."),
            InList(message="La categoría seleccionada no es válida."),
        ],
    )

    anio_inauguracion = IntegerField(
        "Año de inauguración",
        validators=[
            DataRequired(message="El año es obligatorio."),
            NumberRange(
                min=1000,
                max=date.today().year,
                message=f"El año debe ser entre 1000 y {date.today().year}.",
            ),
        ],
    )

    HOY = date.today().strftime("%Y-%m-%d")
    fecha_registro = StringField(
        "Fecha de Registro",
        default=HOY,
        validators=[
            DataRequired(message="La fecha de registro es obligatoria."),
            Regexp(
                r"^\d{4}-\d{2}-\d{2}$",
                message="El formato de fecha debe ser AAAA-MM-DD.",
            ),
        ],
    )

    visible = SelectField(
        "Visible",
        choices=[("True", "Sí"), ("False", "No")],
        validators=[
            DataRequired(),
            InList(message="La opción de visibilidad no es válida."),
        ],
    )

    latitud = StringField(
        "Latitud",
        validators=[DataRequired(message="La latitud es obligatoria.")],
    )
    longitud = StringField(
        "Longitud",
        validators=[DataRequired(message="La longitud es obligatoria.")],
    )

    tags = HiddenField(validators=[Optional()])

    def validate_latitud(form, field):
        """Valida que la latitud sea un número entre -90 y 90."""
        try:
            val = float(field.data)
            if not (-90 <= val <= 90):
                raise ValueError
        except (TypeError, ValueError):
            raise ValidationError(
                "Latitud inválida. Debe ser un número entre -90 y 90."
            )

    def validate_longitud(form, field):
        """Valida que la longitud sea un número entre -180 y 180."""
        try:
            val = float(field.data)
            if not (-180 <= val <= 180):
                raise ValueError
        except (TypeError, ValueError):
            raise ValidationError(
                "Longitud inválida. Debe ser un número entre -180 y 180."
            )

    def validate_tags(self, field):
        """
        Valida que si el campo de tags tiene datos, sea un JSON válido
        y que cada tag individualmente tenga un formato correcto.
        """
        if not field.data:
            return

        try:
            tags_list = json.loads(field.data)

            if not isinstance(tags_list, list):
                raise ValidationError("El formato de etiquetas debe ser una lista.")

            for tag in tags_list:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValidationError("Las etiquetas no pueden estar vacías.")

                if not TAG_REGEX.match(tag.strip()):
                    raise ValidationError(
                        f"La etiqueta '{tag}' contiene caracteres no válidos."
                    )

        except json.JSONDecodeError:
            raise ValidationError("Formato de etiquetas (JSON) inválido.")
