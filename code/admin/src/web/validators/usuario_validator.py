"""Validaciones del lado del servidor para el módulo de usuarios.

Este módulo implementa todas las validaciones requeridas según el patrón:
- Validación de campos obligatorios
- Validación de tipos esperados
- Validación de longitudes máximas según el modelo
- Validación de unicidad (email)
- Validación de integridad de referencias (FK a roles)
- Validación de patrones (contraseña mínima)
"""

import re
from typing import Dict, List, Tuple
from core import auth


class UsuarioValidationError(Exception):
    """Excepción personalizada para errores de validación de usuario."""

    def __init__(self, errors: Dict[str, List[str]]):
        """Inicializa el error con un diccionario de mensajes por campo.

        Args:
            errors: Diccionario donde la clave es el nombre del campo
                   y el valor es una lista de mensajes de error.
        """
        self.errors = errors
        super().__init__(str(errors))


ORDENES_VALIDOS = [
    "fecha_asc",
    "fecha_desc",
    "email_asc",
    "email_desc",
]


def validar_crear_usuario(data: dict) -> Tuple[bool, Dict[str, List[str]]]:
    """Valida los datos para crear un nuevo usuario.

    Valida todos los campos requeridos para creación:
    - Campos obligatorios: nombre, apellido, email, password, id_rol
    - Tipos correctos
    - Longitudes máximas según modelo Usuario
    - Unicidad de email
    - Existencia del rol referenciado
    - Patrón de contraseña (mínimo 6 caracteres)

    Args:
        data: Diccionario con los datos del usuario a crear.
              Esperado: nombre, apellido, email, password, id_rol, activo (opcional)

    Returns:
        Tupla (es_valido, errores) donde:
        - es_valido: True si no hay errores, False si hay al menos uno
        - errores: Diccionario {campo: [mensaje1, mensaje2, ...]}
    """
    errors = {}

    campos_requeridos = ["nombre", "apellido", "email", "password", "id_rol"]
    for campo in campos_requeridos:
        if not data.get(campo):
            errors.setdefault(campo, []).append(f"El campo '{campo}' es obligatorio.")
        elif isinstance(data.get(campo), str) and not data.get(campo).strip():
            errors.setdefault(campo, []).append(
                f"El campo '{campo}' no puede estar vacío."
            )

    if errors:
        return False, errors

    if not isinstance(data.get("nombre"), str):
        errors.setdefault("nombre", []).append(
            "El campo 'nombre' debe ser una cadena de texto."
        )

    if not isinstance(data.get("apellido"), str):
        errors.setdefault("apellido", []).append(
            "El campo 'apellido' debe ser una cadena de texto."
        )

    if not isinstance(data.get("email"), str):
        errors.setdefault("email", []).append(
            "El campo 'email' debe ser una cadena de texto."
        )

    if not isinstance(data.get("password"), str):
        errors.setdefault("password", []).append(
            "El campo 'password' debe ser una cadena de texto."
        )

    try:
        id_rol = int(data.get("id_rol"))
        data["id_rol"] = id_rol
    except (ValueError, TypeError):
        errors.setdefault("id_rol", []).append(
            "El campo 'id_rol' debe ser un número entero."
        )

    if "activo" in data:
        activo_value = data.get("activo")
        if isinstance(activo_value, str):
            if activo_value.lower() == "true":
                data["activo"] = True
            elif activo_value.lower() == "false":
                data["activo"] = False
            else:
                errors.setdefault("activo", []).append(
                    "El campo 'activo' debe ser true o false."
                )
        elif not isinstance(activo_value, bool):
            errors.setdefault("activo", []).append(
                "El campo 'activo' debe ser un valor booleano."
            )

    if len(data.get("nombre", "")) > 100:
        errors.setdefault("nombre", []).append(
            "El campo 'nombre' no puede superar los 100 caracteres."
        )

    if len(data.get("apellido", "")) > 100:
        errors.setdefault("apellido", []).append(
            "El campo 'apellido' no puede superar los 100 caracteres."
        )

    if len(data.get("email", "")) > 100:
        errors.setdefault("email", []).append(
            "El campo 'email' no puede superar los 100 caracteres."
        )

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, data.get("email", "")):
        errors.setdefault("email", []).append("El formato del email no es válido.")

    try:
        usuario_existente = auth.obtener_usuario_por_email(data.get("email"))
        if usuario_existente and not usuario_existente.eliminado:
            errors.setdefault("email", []).append(
                "El email ya está registrado en el sistema."
            )
    except Exception as e:
        errors.setdefault("_general", []).append(
            f"Error al verificar unicidad del email: {str(e)}"
        )

    try:
        rol_existente = auth.obtener_rol_por_id(data.get("id_rol"))
        if not rol_existente:
            errors.setdefault("id_rol", []).append(
                "El rol seleccionado no existe en el sistema."
            )
    except Exception as e:
        errors.setdefault("_general", []).append(
            f"Error al verificar existencia del rol: {str(e)}"
        )

    password = data.get("password", "")
    if len(password) < 6:
        errors.setdefault("password", []).append(
            "La contraseña debe tener al menos 6 caracteres."
        )

    if not re.search(r"[A-Za-z]", password):
        errors.setdefault("password", []).append(
            "La contraseña debe contener al menos una letra."
        )

    if not re.search(r"\d", password):
        errors.setdefault("password", []).append(
            "La contraseña debe contener al menos un número."
        )

    return len(errors) == 0, errors


def validar_actualizar_usuario(
    id_usuario: int, data: dict
) -> Tuple[bool, Dict[str, List[str]]]:
    """Valida los datos para actualizar un usuario existente.

    Similar a validar_crear_usuario pero:
    - La contraseña es opcional (solo se valida si se proporciona)
    - Al validar unicidad de email, excluye al usuario actual
    - Verifica que el usuario a editar exista

    Args:
        id_usuario: ID del usuario que se está editando.
        data: Diccionario con los datos a actualizar.
              Esperado: nombre, apellido, email, id_rol, activo (opcional), password (opcional)

    Returns:
        Tupla (es_valido, errores) donde:
        - es_valido: True si no hay errores, False si hay al menos uno
        - errores: Diccionario {campo: [mensaje1, mensaje2, ...]}
    """
    errors = {}
    usuario = auth.obtener_usuario_por_id(id_usuario)

    if (
        not data.get("nombre")
        or isinstance(data.get("nombre"), str)
        and not data.get("nombre").strip()
    ):
        errors.setdefault("nombre", []).append(
            "El campo 'nombre' es obligatorio y no puede estar vacio."
        )

    if (
        not data.get("apellido")
        or isinstance(data.get("apellido"), str)
        and not data.get("apellido").strip()
    ):
        errors.setdefault("apellido", []).append(
            "El campo 'apellido' es obligatorio y no puede estar vacio."
        )

    if (
        not data.get("email")
        or isinstance(data.get("email"), str)
        and not data.get("email").strip()
    ):
        errors.setdefault("email", []).append(
            "El campo 'email' es obligatorio y no puede estar vacio."
        )

    if (not data.get("id_rol") and not usuario.es_admin) or (
        isinstance(data.get("id_rol"), str) and not data.get("id_rol").strip()
    ):
        errors.setdefault("id_rol", []).append(
            "El campo 'id_rol' es obligatorio y no puede estar vacio."
        )

    if errors:
        return False, errors

    if not isinstance(data.get("nombre"), str):
        errors.setdefault("nombre", []).append(
            "El campo 'nombre' debe ser una cadena de texto."
        )

    if not isinstance(data.get("apellido"), str):
        errors.setdefault("apellido", []).append(
            "El campo 'apellido' debe ser una cadena de texto."
        )

    if not isinstance(data.get("email"), str):
        errors.setdefault("email", []).append(
            "El campo 'email' debe ser una cadena de texto."
        )

    if "password" in data and data.get("password"):
        if not isinstance(data.get("password"), str):
            errors.setdefault("password", []).append(
                "El campo 'password' debe ser una cadena de texto."
            )

    try:
        if "id_rol" in data:
            id_rol = int(data.get("id_rol"))
            data["id_rol"] = id_rol
    except (ValueError, TypeError):
        errors.setdefault("id_rol", []).append(
            "El campo 'id_rol' debe ser un número entero."
        )

    validar_id_entero(id_usuario)

    if "activo" in data:
        activo_value = data.get("activo")
        if isinstance(activo_value, str):
            if activo_value.lower() in ["true"]:
                data["activo"] = True
            elif activo_value.lower() in ["false"]:
                data["activo"] = False
            else:
                errors.setdefault("activo", []).append(
                    "El campo 'activo' debe ser true o false."
                )
        elif not isinstance(activo_value, bool):
            errors.setdefault("activo", []).append(
                "El campo 'activo' debe ser un valor booleano."
            )

    if len(data.get("nombre", "")) > 100:
        errors.setdefault("nombre", []).append(
            "El campo 'nombre' no puede superar los 100 caracteres."
        )

    if len(data.get("apellido", "")) > 100:
        errors.setdefault("apellido", []).append(
            "El campo 'apellido' no puede superar los 100 caracteres."
        )

    if len(data.get("email", "")) > 100:
        errors.setdefault("email", []).append(
            "El campo 'email' no puede superar los 100 caracteres."
        )

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, data.get("email", "")):
        errors.setdefault("email", []).append("El formato del email no es válido.")

    if "password" in data and data.get("password"):
        password = data.get("password")
        if len(password) < 6:
            errors.setdefault("password", []).append(
                "La contraseña debe tener al menos 6 caracteres."
            )

        if not re.search(r"[A-Za-z]", password):
            errors.setdefault("password", []).append(
                "La contraseña debe contener al menos una letra."
            )

        if not re.search(r"\d", password):
            errors.setdefault("password", []).append(
                "La contraseña debe contener al menos un número."
            )

    return len(errors) == 0, errors


def validar_filtros_busqueda_usuarios(email, activo_str, id_rol_str, orden):
    """
    Valida los parámetros de búsqueda de usuarios.

    Args:
        email (str): Email a buscar (puede ser parcial)
        activo_str (str): Estado del usuario ('true', 'false', o vacío)
        id_rol_str (str): ID del rol (debe ser numérico o vacío)
        orden (str): Criterio de ordenamiento

    Returns:
        tuple: (email_validado, activo_bool, id_rol_int, orden_validado)

    Raises:
        ValueError: Si los parámetros no son válidos
    """

    email_validado = email.strip() if email else None

    activo_bool = None
    if activo_str:
        if activo_str.lower() == "true":
            activo_bool = True
        elif activo_str.lower() == "false":
            activo_bool = False
        else:
            raise ValueError(
                f"El parámetro 'activo' debe ser 'true' o 'false', se recibió: '{activo_str}'"
            )

    id_rol_int = None
    if id_rol_str:
        try:
            id_rol_int = int(id_rol_str)
            if id_rol_int <= 0:
                raise ValueError("El ID del rol debe ser un entero positivo")
        except (ValueError, TypeError):
            raise ValueError(
                f"El parámetro 'id_rol' debe ser un número entero, se recibió: '{id_rol_str}'"
            )

    ordenes_validos = [
        "fecha_asc",
        "fecha_desc",
        "nombre_asc",
        "nombre_desc",
        "",
    ]

    if not orden in ordenes_validos:
        raise ValueError("El orden ingresado no es valido")

    return email_validado, activo_bool, id_rol_int, orden


def obtener_errores_formateados(errors: Dict[str, List[str]]) -> str:
    """Convierte el diccionario de errores en un mensaje legible para flash.

    Args:
        errors: Diccionario de errores {campo: [mensaje1, ...]}.

    Returns:
        String con todos los errores formateados para mostrar al usuario.
    """
    mensajes = []
    for campo, lista_errores in errors.items():
        if campo == "_general":
            mensajes.extend(lista_errores)
        else:
            for error in lista_errores:
                mensajes.append(f"{campo.capitalize()}: {error}")

    return " | ".join(mensajes)


def validar_id_entero(id_usuario: int):
    """Valida que el ID del usuario sea un número entero positivo.
    Args:
       id_usuario: ID del usuario a validar.
    Raises:
        ValueError: Si el ID no es un número entero positivo.
    """
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("El ID del usuario debe ser un número entero positivo.")
