"""
Módulo de autenticación y gestión de usuarios.

Contiene funciones para buscar usuarios, validar credenciales y
realizar operaciones básicas de seguridad.
"""

from core.database import db
from core.auth.usuario import Usuario
from core.utils.hashing import comprobar_pass


def buscar_usuario_por_email_y_contrasena(email, password):
    """
    Busca un usuario por email y contraseña.

    :param email: Email del usuario.
    :param password: Contraseña en texto plano.
    :return: El objeto Usuario si las credenciales son correctas, None si no.
    """

    usuario = db.session.query(Usuario).filter_by(email=email).first()

    if usuario and not usuario.eliminado and comprobar_pass(usuario, password):
        return usuario

    raise ValueError("Credenciales inválidas.")
