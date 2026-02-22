"""Funciones auxiliares para hash y verificación de contraseñas.

Estas utilidades envuelven ``bcrypt`` para guardar y comprobar passwords.
"""

import bcrypt


def guardar_pass(self, password_plain):
    """
    Hashea una contraseña en texto plano y la asigna al atributo 'password' del objeto.

    Utiliza bcrypt para generar un salt y hashear la contraseña de forma segura.
    El resultado se decodifica a UTF-8 para ser almacenado en la base de datos.

    """
    salt = bcrypt.gensalt()
    self.password = bcrypt.hashpw(password_plain.encode("utf-8"), salt).decode("utf-8")


def comprobar_pass(self, password_plain):
    """
    Verifica si una contraseña coincide con la contraseña hasheada del objeto.

    Returns:
        bool: True si la contraseña es correcta, False en caso contrario.
    """
    if password_plain is None or self.password is None:
        return False

    return bcrypt.checkpw(password_plain.encode("utf-8"), self.password.encode("utf-8"))
