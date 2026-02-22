"""Manejadores de errores HTTP para la aplicación web.

Provee una estructura simple (``HttpError``) y helpers para renderizar
plantillas de error estandarizadas para códigos 400, 401, 404 y 500.
"""

from dataclasses import dataclass
from flask import render_template


@dataclass
class HttpError:
    """Estructura de datos para representar un error HTTP.

    Atributos:
        code: Código de estado HTTP (por ejemplo, 404).
        message: Mensaje corto ("Not Found", etc.).
        description: Descripción amigable a mostrar al usuario.
    """

    code: int
    message: str
    description: str


def bad_request_error(e):
    """Renderiza la página de error 400 (Bad Request)."""
    error = HttpError(
        code=400,
        message="Bad Request",
        description="Lo sentimos, ocurrió un error en la solicitud realizada.",
    )
    return render_template("error.html", error=error), 400


def unauthorized_error(e):
    """Renderiza la página de error 401 (Unauthorized)."""
    error = HttpError(
        code=401,
        message="Unauthorized",
        description="Lo sentimos, debe iniciar sesión para acceder a esta página.",
    )
    return render_template("error.html", error=error), 401


def forbidden_error(e):
    """Renderiza la página de error 403 (Forbidden)."""
    error = HttpError(
        code=403,
        message="Forbidden",
        description="Lo sentimos, no posee los permisos para acceder a esta página.",
    )
    return render_template("error.html", error=error), 403


def not_found_error(e):
    """Renderiza la página de error 404 (Not Found)."""
    error = HttpError(
        code=404,
        message="Not Found",
        description="Lo sentimos, la página que está buscando no existe.",
    )
    return render_template("error.html", error=error), 404


def internal_server_error(e):
    """Renderiza la página de error 500 (Internal Server Error)."""
    error = HttpError(
        code=500,
        message="Internal server error",
        description="Lo sentimos, ocurrió un error en el servidor.",
    )
    return render_template("error.html", error=error), 500
