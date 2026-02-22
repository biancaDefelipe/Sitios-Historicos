"""
Módulo que define el esquema de Marshmallow para la serialización y validación
de la información de una imagen asociada a un sitio histórico.

Este esquema mapea los nombres de atributos internos del modelo de imagen
a los nombres utilizados en la respuesta JSON pública de la API.
"""

from marshmallow import Schema, fields


class ImageSchema(Schema):
    """
    Schema para la serialización (SALIDA) de un objeto de imagen.

    Mapea los atributos del modelo de imagen (usando `attribute=...`) a
    los nombres de campo públicos.
    """

    id = fields.Int(attribute="id_imagen")
    public_url = fields.Str(attribute="url_publica")
    alt_text = fields.Str(attribute="titulo_alt")
    description = fields.Str(attribute="descripcion")
    order = fields.Int(attribute="orden")
    is_cover = fields.Bool(attribute="es_portada")

    class Meta:
        """
        Configuración del esquema.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        """

        ordered = True
