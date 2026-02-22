"""
Schema para VALIDAR y CARGAR los datos de entrada al crear un sitio.
Está basado ESTRICTAMENTE en la especificación de la cátedra.
No incluye 'anio_inauguracion' porque no viene en la petición.
"""

from marshmallow import Schema, fields, validate
from web.schemas.image import ImageSchema


class SiteCreateSchema(Schema):
    """
    Schema para VALIDAR y CARGAR los datos de entrada al crear un sitio.
    Está basado ESTRICTAMENTE en la especificación de la cátedra.
    No incluye 'anio_inauguracion' porque no viene en la petición.
    """

    name = fields.Str(required=True)
    short_description = fields.Str(required=True)
    description = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(required=True)
    country = fields.Str(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    tags = fields.List(fields.Str(), required=True)
    state_of_conservation = fields.Str(required=True)

    class Meta:
        """Configuración del esquema.

        unknown="EXCLUDE": Ignora los campos desconocidos en la entrada
        en lugar de lanzar un error de validación.
        """

        unknown = "EXCLUDE"


class SiteSchema(Schema):
    """
    Schema para MOSTRAR (dump) un objeto SitioHistorico.
    Usa 'attribute' para traducir los nombres de las columnas de la base de datos
    a los nombres de los campos del JSON de salida.
    """

    id = fields.Int(dump_only=True, attribute="id_sitio")
    name = fields.Str(attribute="nombre")

    short_description = fields.Str(attribute="descripcion_breve")
    description = fields.Str(attribute="descripcion_completa")

    images = fields.Nested(ImageSchema, many=True, attribute="imagenes")

    city = fields.Str(attribute="ciudad.nombre")
    province = fields.Str(attribute="ciudad.provincia.nombre")

    country = fields.Str(dump_default="AR")

    rank = fields.Float(attribute="rank")

    lat = fields.Float()
    long = fields.Float(attribute="lon")

    tags = fields.Function(
        lambda obj: [tag.nombre for tag in obj.tags] if obj.tags else []
    )

    state_of_conservation = fields.Str(attribute="estado_conservacion.descripcion")

    inserted_at = fields.DateTime(attribute="fecha_hora_alta", format="iso")
    updated_at = fields.DateTime(attribute="fecha_hora_modificacion", format="iso")

    class Meta:
        """Configuración del esquema de salida.

        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serialización.
        """

        ordered = True
        fields = (
            "id",
            "name",
            "short_description",
            "description",
            "images",
            "city",
            "province",
            "country",
            "rank",
            "lat",
            "long",
            "tags",
            "state_of_conservation",
            "inserted_at",
            "updated_at",
        )


class SiteIdPathSchema(Schema):
    """
    Schema para VALIDAR el ID del sitio en la ruta (path parameter).
    """

    site_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Must be a positive integer"),
    )


class SiteListQueryArgsSchema(Schema):
    """
    Schema para VALIDAR los parámetros de la URL (query args) de GET /api/sites.
    """

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Must be greater than or equal to 1"),
    )
    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100, error="Must be between 1 and 100"),
    )

    name = fields.Str(load_default=None)
    description = fields.Str(load_default=None)

    city = fields.Str(load_default=None)
    province = fields.Str(load_default=None)
    tags = fields.Str(load_default=None)

    favorites = fields.Bool(load_default=False)

    order_by = fields.Str(
        load_default="latest",
        validate=validate.OneOf(
            [
                "rating-5-1",
                "rating-1-5",
                "latest",
                "oldest",
                "name-asc",
                "name-desc",
            ],
            error="El 'order_by' no es válido.",
        ),
    )

    lat = fields.Float(
        load_default=None,
        validate=validate.Range(min=-90, max=90, error="Must be a valid latitude"),
        error_messages={"invalid": "Must be a valid latitude"},
    )
    long = fields.Float(
        load_default=None,
        validate=validate.Range(min=-180, max=180, error="Must be a valid longitude"),
        error_messages={"invalid": "Must be a valid longitude"},
    )
    radius = fields.Float(
        load_default=None,
        validate=validate.Range(min=0, error="El radio debe ser un número positivo."),
        error_messages={"invalid": "Must be a valid number"},
    )

    class Meta:
        """Configuración del esquema.

        unknown="EXCLUDE": Ignora los campos desconocidos en la entrada
        en lugar de lanzar un error de validación.
        """

        unknown = "EXCLUDE"
