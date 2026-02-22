"""
Módulo que define el blueprint y las rutas de la API para obtener la configuración pública.

Estas rutas consultan el estado de las Feature Flags para informar al frontend sobre
el modo de mantenimiento, mensajes asociados y la disponibilidad de ciertas funcionalidades.
"""

from flask import Blueprint, jsonify
from core.flags import esta_activo, obtener_mensaje_mantenimiento

config_api_blueprint = Blueprint("config_api", __name__, url_prefix="/config")
"""Blueprint para las rutas de configuración pública de la API."""


@config_api_blueprint.route("/", methods=["GET"])
def get_public_config():
    """
    GET /api/config - Devuelve la configuración pública basada en Feature Flags.

    Esta función consulta diferentes flags de configuración (como el modo de
    mantenimiento y la habilitación de reviews) para informar al frontend sobre
    el estado actual de ciertas características del portal.

    Returns:
        tuple[dict, int]: Un diccionario JSON con los siguientes campos y código HTTP 200:
            * **maintenance_mode** (bool): Indica si el modo de mantenimiento está activo.
            * **maintenance_message** (str): El mensaje a mostrar si el mantenimiento está activo.
            * **reviews_enabled** (bool): Indica si la funcionalidad de reviews está habilitada.
    """

    mantenimiento_activo = esta_activo("modo_mantenimiento_portal_publico")
    mensaje_mantenimiento = obtener_mensaje_mantenimiento(
        "modo_mantenimiento_portal_publico"
    )

    reviews_habilitadas = esta_activo("reviews_habilitadas")

    return (
        jsonify(
            {
                "maintenance_mode": mantenimiento_activo,
                "maintenance_message": mensaje_mantenimiento,
                "reviews_enabled": reviews_habilitadas,
            }
        ),
        200,
    )
