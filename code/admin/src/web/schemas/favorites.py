"""
Schemas de Marshmallow para la funcionalidad de Sitios Favoritos.

Este módulo define:
- Schemas de validación para los parámetros de consulta (query args)
  utilizados en los endpoints de favoritos.
- Schemas de serialización para la respuesta de sitios marcados como favoritos.
"""

from marshmallow import Schema, fields, validate
from web.schemas.image import ImageSchema


class FavoritesListQueryArgsSchema(Schema):
    """
    Schema para VALIDAR los parámetros de la URL (query args) de GET /api/me/favorites.
    """

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Pagina debe ser mayor o igual a 1"),
    )
    per_page = fields.Int(
        load_default=None,
        validate=validate.Range(min=1, error="Pagina debe ser mayor o igual a 1"),
    )

    class Meta:
        """
        Class Meta
        """

        unknown = "EXCLUDE"


class FavoriteSiteSchema(Schema):
    """
    Schema para serializar (SALIDA) un sitio favorito.
    Define explícitamente los campos a mostrar sin heredar de SiteSchema.
    """

    id = fields.Int(attribute="id_sitio")
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
        """
        Class Meta
        """

        ordered = True


class SiteIsFavoriteSchema(Schema):
    """
    Schema para serializar (SALIDA) la respuesta de si un sitio es favorito para un usuario autenticado.
    """

    site = fields.Nested(FavoriteSiteSchema, dump_only=True)
    site_is_favorite = fields.Bool(dump_only=True)
