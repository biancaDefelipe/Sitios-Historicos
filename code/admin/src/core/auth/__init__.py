"""Módulo de autenticación y gestión de usuarios.

Este módulo provee funciones para:
- Crear, actualizar, eliminar y buscar usuarios
- Gestionar roles y permisos
- Autenticación y autorización
- Bloqueo/desbloqueo de cuentas
- Búsqueda y filtrado de usuarios con paginación
"""

from core.database import db
from core.auth.usuario import Usuario
from core.auth.rol import Rol
from core.auth.permiso import Permiso
from core.utils.pagination import paginate
from sqlalchemy import func, or_, select, update
from ..utils.hashing import guardar_pass, comprobar_pass
import logging
import re

logger = logging.getLogger(__name__)


def crear_rol(**kwargs):
    """
    Crea un nuevo rol en la base de datos.

    :param kwargs: Atributos del rol.
    :return: El objeto Rol creado.
    """

    rol = Rol(**kwargs)
    db.session.add(rol)
    db.session.commit()
    return rol


def bloquear_usuario(id_usuario: int):
    """
    Bloquea a un usuario específico.

    :param id_usuario: El ID del usuario a bloquear.
    :raise Exception: Indica que ocurrió un error inesperado.
    """
    try:
        query = (
            update(Usuario)
            .where(Usuario.id_usuario == id_usuario)
            .values(activo=False)
        )
        db.session.execute(query)
        db.session.commit()

    except Exception as e:
        logger.exception("Ocurrió un error inesperado al bloquear usuario.")
        db.session.rollback()
        raise e


def desbloquear_usuario(id_usuario: int):
    """
    Desbloquea a un usuario específico.

    :param id_usuario: El ID del usuario a desbloquear.
    :raise Exception: Indica que ocurrió un error inesperado.
    """
    try:
        query = (
            update(Usuario)
            .where(Usuario.id_usuario == id_usuario)
            .values(activo=True)
        )
        db.session.execute(query)
        db.session.commit()

    except Exception as e:
        logger.exception("Ocurrió un error inesperado al desbloquear usuario.")
        db.session.rollback()
        raise e


def crear_usuario(**kwargs) -> Usuario:
    """
    -Crea un nuevo usuario en la base de datos.

    -Hashea la contraseña del usuario y la almacena en la base de datos.

    :param kwargs: Atributos del usuario, incluyendo 'password'.
    :return: El objeto Usuario creado.
    """
    email = kwargs.get("email")
    validar_email_seguro(email)
    password = kwargs.pop("password", None)
    usuario = Usuario(**kwargs)

    if password:
        guardar_pass(usuario, password)

    db.session.add(usuario)
    db.session.commit()
    return usuario


def revivir_usuario(usuario: Usuario, nuevos_datos: dict) -> Usuario:
    """
    Revive un usuario eliminado y actualiza sus datos
    con los valores recibidos.
    """
    if "email" in nuevos_datos:
        validar_email_seguro(nuevos_datos["email"],
                             exclude_id=usuario.id_usuario)
        usuario.email = nuevos_datos["email"]

    if "nombre" in nuevos_datos:
        usuario.nombre = nuevos_datos["nombre"]

    if "apellido" in nuevos_datos:
        usuario.apellido = nuevos_datos["apellido"]

    if "id_rol" in nuevos_datos:
        usuario.id_rol = int(nuevos_datos["id_rol"])

    if "activo" in nuevos_datos:
        usuario.activo = nuevos_datos["activo"]

    if "password" in nuevos_datos and nuevos_datos["password"]:
        guardar_pass(usuario, nuevos_datos["password"])

    usuario.eliminado = False

    db.session.commit()
    return usuario


def buscar_permisos(id_usuario: int) -> list[str]:
    """
    Obtiene una lista de permisos para un usuario en específico.

    :param id_usuario: El ID del usuario para quién se obtendrán sus permisos.
    :return list[str]: La lista de permisos de un usuario en específico.
    """
    query = (
        select(Permiso.descripcion)
        .join(Permiso.roles)
        .join(Rol.usuarios)
        .where(Usuario.id_usuario == id_usuario)
    )
    return db.session.execute(query).scalars().all()


def buscar_usuario_por_email_y_contrasena(email, password):
    """
    Busca un usuario por email y contraseña.

    :param email: Email del usuario.
    :param password: Contraseña en texto plano.
    :return: El objeto Usuario si las credenciales son correctas, None si no.
    """

    usuario = (
        db.session.query(Usuario)
        .filter(Usuario.email == email)
        .filter(or_(Usuario.id_rol.isnot(None), Usuario.es_admin.is_(True)))
        .first()
    )

    if (
        usuario
        and not usuario.eliminado
        and ((usuario.rol and usuario.rol.es_asignable) or usuario.es_admin)
        and usuario.password
        and comprobar_pass(usuario, password)
    ):
        return usuario

    return None


def listar_usuarios():
    """
    Devuelve la lista completa de usuarios.
    """
    return db.session.execute(select(Usuario)).scalars().all()


def obtener_usuario_por_id(id_usuario: int) -> Usuario | None:
    """
    Obtiene un usuario por su ID.

    Args:
        id_usuario: ID del usuario a buscar.

    Returns:
        Usuario si existe y no está eliminado, None en caso contrario.
    """
    usuario = db.session.get(Usuario, id_usuario)
    if usuario and not usuario.eliminado:
        return usuario
    return None


def obtener_eliminado_por_id(id_usuario: int) -> bool | None:
    """
    Verifica si un usuario está eliminado.
    """
    stmt = select(Usuario.eliminado).where(Usuario.id_usuario == id_usuario)
    return db.session.scalar(stmt) is True


def obtener_usuario_por_email(email: str) -> Usuario | None:
    """
    Obtiene un usuario por su email.
    """
    return db.session.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalar_one_or_none()


def email_duplicado(email: str, exclude_id: int = None) -> bool:
    """
    Verifica si un email ya está registrado, excluyendo opcionalmente un ID.
    """
    query = select(Usuario).where(Usuario.email == email)
    if exclude_id:
        query = query.where(Usuario.id_usuario != exclude_id)
    return db.session.execute(query).scalar_one_or_none() is not None


def actualizar_usuario(id_usuario: int, datos: dict) -> Usuario | None:
    """
    Actualiza los datos de un usuario.
    """
    usuario = db.session.get(Usuario, id_usuario)

    if "email" in datos:
        validar_email_seguro(datos["email"], exclude_id=id_usuario)
    if usuario:
        if "nombre" in datos:
            usuario.nombre = datos["nombre"]
        if "apellido" in datos:
            usuario.apellido = datos["apellido"]
        if "email" in datos:
            usuario.email = datos["email"]
        if "id_rol" in datos and datos["id_rol"] and usuario.id_rol:
            usuario.id_rol = datos["id_rol"]

        if "password" in datos and datos["password"] and usuario.password:
            guardar_pass(usuario, datos["password"])

        db.session.commit()
        return usuario
    return None


def eliminar_usuario(id_usuario: int) -> bool:
    """
    Elimina un usuario por su ID.
    """
    usuario = db.session.get(Usuario, id_usuario)

    if not usuario or usuario.eliminado:
        raise ValueError("El usuario no existe o ya fue eliminado.")

    if usuario.es_admin:
        raise ValueError("No se puede eliminar a un usuario system admin.")

    if usuario.rol and not usuario.rol.es_prescindible:
        total_usuarios_rol_a_eliminar = (
            db.session.query(Usuario)
            .filter(~Usuario.eliminado, Usuario.id_rol == usuario.id_rol)
            .count()
        )
        if not total_usuarios_rol_a_eliminar > 1:
            raise ValueError(
                "No se puede eliminar al único usuario con este rol."
                )

    usuario.eliminado = True
    db.session.commit()
    return True


def buscar_usuarios_filtrados(
    id_usuario: int,
    email: str = None,
    activo: bool = None,
    id_rol: int = None,
    orden: str = "fecha_desc",
    pagina: int = 1,
    por_pagina: int = None,
) -> dict:
    """
    Busca usuarios con filtros opcionales, paginación y ordenamiento.

    Args:
        id_usuario(int): id del usuario actual
        email (str): Texto para buscar en el email (búsqueda parcial)
        activo (bool): Filtrar por estado activo (True/False)
        id_rol (int): Filtrar por ID de rol
        orden (str): Criterio de ordenamiento
        ('fecha_asc', 'fecha_desc', 'nombre_asc', 'nombre_desc').
        Si el valor no es válido, se ordena por 'fecha_desc'.
        pagina (int): Página actual (inicia en 1)
        por_pagina (int): Registros por página.

    Returns:
        dict: Contiene 'usuarios', 'total', 'paginas', 'pagina_actual',
        'tiene_anterior', 'tiene_siguiente'
    """

    query = (
        db.session.query(
            Usuario,
            func.coalesce(Rol.descripcion, "-").label("rol_descripcion"),
        )
        .outerjoin(Usuario.rol)
        .filter(~Usuario.eliminado)
    )

    if email:
        query = query.filter(Usuario.email.ilike(f"%{email}%"))

    if activo is not None:
        query = query.filter(Usuario.activo == activo)

    if id_rol:

        rol = db.session.get(Rol, id_rol)

        if not rol:
            raise ValueError("El id de rol ingresado no existe.")
        if rol.es_asignable:
            query = query.filter(Usuario.id_rol == id_rol)
        else:
            query = query.filter(Usuario.id_rol.is_(None))

    if id_usuario:
        query = query.filter(Usuario.id_usuario != id_usuario)

    if orden == "fecha_asc":
        query = query.order_by(Usuario.fecha_hora_alta.asc())
    elif orden == "fecha_desc":
        query = query.order_by(Usuario.fecha_hora_alta.desc())
    elif orden == "nombre_asc":
        query = query.order_by(Usuario.nombre.asc(), Usuario.apellido.asc())
    elif orden == "nombre_desc":
        query = query.order_by(Usuario.nombre.desc(), Usuario.apellido.desc())
    else:
        query = query.order_by(Usuario.fecha_hora_alta.desc())

    usuarios_list, paginacion = paginate(
        query=query, page=pagina, per_page=por_pagina
        )

    usuarios = []
    for usuario_obj, descripcion in usuarios_list:
        setattr(usuario_obj, "rol_descripcion", descripcion)
        usuarios.append(usuario_obj)

    return {
        "usuarios": usuarios,
        "total": paginacion["total"],
        "paginas": paginacion["total_pages"],
        "pagina_actual": paginacion["page"],
        "tiene_anterior": paginacion["has_prev"],
        "tiene_siguiente": paginacion["has_next"],
        "por_pagina": paginacion["per_page"],
    }


def listar_roles() -> list[Rol]:
    """
    Devuelve la lista completa de roles.
    """
    return db.session.execute(select(Rol)).scalars().all()


def listar_roles_asignables() -> list[Rol]:
    """
    Devuelve la lista de roles que son asignables.
    """
    return db.session.execute(
        select(Rol).where(Rol.es_asignable.is_(True))
        ).scalars().all()


def obtener_rol_por_id(id_rol: int) -> Rol | None:
    """
    Obtiene un rol por su ID.
    """
    return db.session.get(Rol, id_rol)


def validar_email_seguro(email: str, exclude_id: int = None):
    """
    Valida el formato del email y verifica que no esté duplicado.
    Se ejecuta tanto en creación como en actualización de usuarios.
    """
    if not email or not isinstance(email, str):
        raise ValueError("El email es requerido.")

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValueError("El formato del email no es válido.")

    query = select(Usuario).where(Usuario.email == email)

    if exclude_id:
        query = query.where(Usuario.id_usuario != exclude_id)

    existente = db.session.execute(query).scalar_one_or_none()
    if existente and not existente.eliminado:
        raise ValueError("El email ya está registrado.")

    return True
