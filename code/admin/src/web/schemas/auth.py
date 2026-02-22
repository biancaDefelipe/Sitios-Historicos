"""
Módulo que define los esquemas de Marshmallow para la validación de entrada
y la serialización de salida relacionados con las rutas de autenticación (Auth).

Incluye esquemas para validar las credenciales de login y para estructurar
la respuesta del token JWT.
"""

from marshmallow import Schema, fields


class AuthLoginSchema(Schema):
    """
    Schema para la ENTRADA (validación) del endpoint POST /auth.
    Valida que el JSON tenga 'user' (email) y 'password'.
    """

    user = fields.Str(
        required=True,
        attribute="email",
    )
    password = fields.Str(required=True)

    class Meta:
        """
        Configuración del esquema.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serialización.
        """

        ordered = True
        fields = ("user", "password")


class AuthTokenSchema(Schema):
    """
    Schema para la SALIDA (serialización) del endpoint POST /auth.
    Devuelve el token y el tiempo de expiración.
    """

    token = fields.Str(dump_only=True)
    expires_in = fields.Int(dump_only=True, dump_default=3600)

    class Meta:
        """
        Configuración del esquema.
        ordered=True: Mantiene el orden de los campos en el JSON generado.
        fields: Define explícitamente la lista y el orden de los campos a incluir en la serialización.
        """

        ordered = True
        fields = ("token", "expires_in")
