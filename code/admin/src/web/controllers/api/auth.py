"""
Módulo que define el blueprint y las rutas de la API para la autenticación de usuarios.

Maneja el flujo de login a través de proveedores de terceros (actualmente solo Google Sign-In)
y la generación de tokens de acceso JWT. También incluye un chequeo de mantenimiento
ejecutado antes de cada solicitud.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token
from web.schemas.auth import AuthTokenSchema
from core.auth import (
    crear_usuario,
    obtener_usuario_por_email,
)
from marshmallow import ValidationError
from web.utils.mantenimiento_utils import mantenimiento_portal_required
import os
import urllib.parse
import urllib.request
import json

auth_api_blueprint = Blueprint("auth_api", __name__, url_prefix="/auth")
"""Blueprint para las rutas de autenticación de la API."""


auth_token_schema = AuthTokenSchema()
"""Esquema de Marshmallow para serializar el token de autenticación."""


@auth_api_blueprint.post("/")
@cross_origin(expose_headers=["X-Maintenance-Mode"])
@mantenimiento_portal_required
def login():
    """
    POST /api/auth - Proceso de autenticación con Google Sign-In para obtener un token JWT.

    Esta ruta maneja el flujo de autenticación de Google, que incluye:
    1. Recibir el código de autorización ('code') de Google en el cuerpo de la solicitud.
    2. Intercambiar el 'code' por un access_token de Google.
    3. Usar el access_token para obtener la información del usuario ('userinfo') de Google.
    4. Buscar el usuario en la base de datos local por email. Si no existe, lo crea.
    5. Generar un token JWT propio para la aplicación.

    El campo 'provider' debe ser estrictamente "google".

    Returns:
        tuple[dict, int]: Un diccionario con el token JWT y su tiempo de expiración
                          en caso de **éxito** (HTTP 200).
        tuple[dict, int]: Un diccionario con la estructura de error y un código
                          HTTP 400 (proveedor inválido, código faltante, error de Google, validación)
                          o HTTP 401 (credenciales inválidas) en caso de **fallo**.
    """
    try:
        data = request.get_json() or {}
        provider = data.get("provider")

        if provider != "google":
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_provider",
                            "message": "Solo se permite autenticación con Google.",
                        }
                    }
                ),
                400,
            )

        code = data.get("code")
        if not code:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "missing_code",
                            "message": "Falta el código de autenticación de Google.",
                        }
                    }
                ),
                400,
            )

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
        }

        encoded_data = urllib.parse.urlencode(payload).encode()
        token_response = None

        try:

            req = urllib.request.Request(token_url, data=encoded_data, method="POST")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")

            with urllib.request.urlopen(req) as res:
                token_response = json.loads(res.read().decode())

        except urllib.error.HTTPError as e:
            error_details = e.read().decode()
            return jsonify({"error": f"Google error: {error_details}"}), 400

        except Exception as e:

            return (
                jsonify({"error": f"Error exchanging Google code: {str(e)}"}),
                400,
            )

        if not token_response:

            return jsonify({"error": "Google no devolvió datos de token"}), 400

        access_token = token_response.get("access_token")
        if not access_token:

            return jsonify({"error": "Google no devolvió access_token"}), 400

        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        req = urllib.request.Request(userinfo_url)
        req.add_header("Authorization", f"Bearer {access_token}")

        google_userinfo = None

        try:
            with urllib.request.urlopen(req) as res:
                google_userinfo = json.loads(res.read().decode())
        except Exception as e:

            return (
                jsonify({"error": f"Error obteniendo datos del usuario: {str(e)}"}),
                400,
            )

        if not google_userinfo:
            return (
                jsonify({"error": "Google no devolvió datos de usuario"}),
                400,
            )
        email = google_userinfo.get("email")
        nombre_completo = google_userinfo.get("name") or ""
        picture = google_userinfo.get("picture")

        partes = nombre_completo.split(" ", 1)
        nombre = partes[0]
        apellido = partes[1] if len(partes) > 1 else ""

        user = obtener_usuario_por_email(email)

        if not user:
            user = crear_usuario(email=email, nombre=nombre, apellido=apellido)

        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_in_seconds = int(expires_delta.total_seconds())

        token = create_access_token(
            identity=str(user.id_usuario),
            additional_claims={
                "avatar": picture,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
            },
        )

        return (
            auth_token_schema.dump({"token": token, "expires_in": expires_in_seconds}),
            200,
        )

    except ValidationError as err:

        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": err.messages,
                    }
                }
            ),
            400,
        )

    except ValueError as err:
        return (
            jsonify({"error": {"code": "invalid_credentials", "message": str(err)}}),
            401,
        )
