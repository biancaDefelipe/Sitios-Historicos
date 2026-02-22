"""
Módulo que define los esquemas de Marshmallow para la validación y serialización
de datos relacionados con las reseñas (reviews) de sitios históricos.

Incluye esquemas para la creación, edición, serialización de salida, manejo
de argumentos de consulta para listas, y validación de IDs en rutas.
"""

from marshmallow import Schema, fields, validate, pre_load, ValidationError


class ReviewCreateSchema(Schema):
    """
    Schema para la ENTRADA (validación) al crear una reseña (POST).

    Valida la calificación (1-5), el comentario (contenido) y asegura
    que el ID del sitio se carga internamente.
    """

    rating = fields.Int(
        required=True,
        attribute="calificacion",
        validate=validate.Range(min=1, max=5, error="Must be between 1 and 5"),
    )

    comment = fields.Str(
        required=True,
        attribute="contenido",
        validate=validate.Length(
            min=20,
            max=1000,
            error="El comentario debe tener entre 20 y 1000 caracteres",
        ),
    )

    site_id = fields.Int(
        required=True,
        attribute="id_sitio_historico",
        load_only=True,
    )


class ReviewEditSchema(Schema):
    """
    Schema para la ENTRADA (validación) al editar una reseña (PUT).

    Valida la calificación y el comentario, permitiendo que otros campos
    no definidos sean excluidos (`unknown = "EXCLUDE"`).
    """

    rating = fields.Int(
        required=True,
        attribute="calificacion",
        validate=validate.Range(min=1, max=5),
    )

    comment = fields.Str(
        required=True,
        attribute="contenido",
        validate=validate.Length(min=20, max=1000),
    )

    class Meta:
        """
        Configuración del esquema.
        unknown="EXCLUDE": Ignora los campos desconocidos en la entrada
        """

        unknown = "EXCLUDE"


class ReviewSchema(Schema):
    """
    Schema para la SALIDA (serialización) de las reseñas individuales (GET).

    Serializa todos los campos de lectura, incluyendo un alias generado
    a partir del nombre y apellido del usuario.
    """

    id = fields.Int(dump_only=True, attribute="id_resenia")
    site_id = fields.Int(dump_only=True, attribute="id_sitio_historico")

    rating = fields.Int(dump_only=True, attribute="calificacion")

    comment = fields.Str(
        dump_only=True,
        attribute="contenido",
        validate=validate.Length(min=20, max=1000),
    )

    inserted_at = fields.DateTime(
        dump_only=True, attribute="fecha_hora_alta", format="%Y-%m-%d %H:%M:%S"
    )

    updated_at = fields.DateTime(
        dump_only=True,
        attribute="fecha_hora_modificacion",
        format="%Y-%m-%d %H:%M:%S",
    )

    alias = fields.Method("get_alias", dump_only=True)

    def get_alias(self, obj):
        """Genera el alias combinando nombre y apellido del usuario."""
        if obj.usuario:
            nombre = obj.usuario.nombre or ""
            apellido = obj.usuario.apellido or ""
            return f"{nombre} {apellido}".strip()
        return None

    class Meta:
        """Configuración del esquema de salida.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serialización.
        """

        ordered = True
        fields = (
            "id",
            "alias",
            "site_id",
            "rating",
            "comment",
            "inserted_at",
            "updated_at",
        )


class UserReviewSchema(Schema):
    """
    Schema para la SALIDA (serialización) de listas de reseñas
    asociadas a un usuario específico (e.g., /me/reviews).

    Incluye el nombre del sitio y el estado de la reseña.
    """

    id = fields.Int(dump_only=True, attribute="id_resenia")
    site_id = fields.Int(dump_only=True, attribute="id_sitio_historico")
    site_name = fields.Str(
        dump_only=True,
        attribute="sitio_historico.nombre",
        validate=validate.Length(max=100),
    )

    rating = fields.Int(dump_only=True, attribute="calificacion")

    state_id = fields.Int(dump_only=True, attribute="id_estado_resenia")

    comment = fields.Str(
        dump_only=True,
        attribute="contenido",
        validate=validate.Length(min=20, max=1000),
    )

    inserted_at = fields.DateTime(
        dump_only=True, attribute="fecha_hora_alta", format="%Y-%m-%d %H:%M:%S"
    )

    updated_at = fields.DateTime(
        dump_only=True,
        attribute="fecha_hora_modificacion",
        format="%Y-%m-%d %H:%M:%S",
    )

    alias = fields.Method("get_alias", dump_only=True)

    def get_alias(self, obj):
        """Genera el alias combinando nombre y apellido del usuario."""
        if obj.usuario:
            nombre = obj.usuario.nombre or ""
            apellido = obj.usuario.apellido or ""
            return f"{nombre} {apellido}".strip()
        return None

    class Meta:
        """Configuracion del esquema de salida.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serialización.
        """

        ordered = True
        fields = (
            "id",
            "state_id",
            "alias",
            "site_id",
            "rating",
            "comment",
            "inserted_at",
            "updated_at",
            "site_name",
        )


class ReviewListQueryArgsSchema(Schema):
    """
    Schema para VALIDAR los parámetros de consulta (query args) de las rutas GET
    que listan reseñas con paginación y ordenamiento.
    """

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Must be greater than or equal to 1"),
        error_messages={"invalid": "Must be a valid integer"},
    )
    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100, error="Must be between 1 and 100"),
        error_messages={"invalid": "Must be a valid integer"},
    )
    order = fields.Str(load_default="desc", validate=validate.OneOf(["asc", "desc"]))

    @pre_load
    def validate_order_availability(self, data, **kwargs):
        """
        Valida si el ordenamiento está habilitado en el contexto actual.
        Si 'order' está presente en los datos y 'ordering_enabled' es False en el contexto,
        lanza un error de validación.
        """
        if "order" in data and not self.context.get("ordering_enabled", True):
            raise ValidationError(
                "Ordering is not supported for this endpoint",
                field_name="order",
            )
        return data

    class Meta:
        """Configuración del esquema.
        unknown="EXCLUDE": Ignora los campos desconocidos en la entrada
        """

        unknown = "EXCLUDE"


class ReviewIdPathSchema(Schema):
    """
    Schema para VALIDAR el ID de la reseña en la ruta (path parameter).
    """

    review_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Must be a positive integer"),
    )


class ReviewDataSchema(Schema):
    """
    Schema para la SALIDA (serialización) de datos de una reseña de usuario
    que incluye el estado de eliminación. (GET /me/reviews).
    """

    deleted = fields.Bool(dump_only=True)
    review = fields.Nested(UserReviewSchema, dump_only=True)

    class Meta:
        """Configuracion del esquema de salida.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serial
        """

        ordered = True
        fields = ("deleted", "review")


class UserReviewPathSchema(Schema):
    """
    Schema para VALIDAR el ID del sitio en la ruta (path parameter)
    para obtener la reseña de un usuario.
    """

    site_id = fields.Int(required=True)
