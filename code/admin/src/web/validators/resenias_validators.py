"""
Módulo de validaciones reutilizables para los filtros y parámetros
de paginación en la consulta de reseñas.
"""

from datetime import datetime, time


def validar_listar_resenias(filtros: dict, params: dict):
    """
    Valida los filtros y parámetros de paginación para la lista de reseñas.

    Si los filtros o parámetros no cumplen con las reglas definidas, se lanza un ValueError.
    Esta es la función principal que coordina todas las validaciones.

    Args:
        filtros (dict): Un diccionario con los parámetros de filtro (e.g., calificacion_min, estado, fecha_desde).
        params (dict): Un diccionario con los parámetros de paginación/ordenamiento (e.g., nro_pagina, orden).

    Raises:
        ValueError: Si algún filtro o parámetro es inválido (delegado a las funciones privadas).
    """
    if filtros is None:
        return
    _validar_calificacion(
        filtros.get("calificacion_min"), filtros.get("calificacion_max")
    )
    _validar_estado(filtros.get("estado"))
    _validar_sitio(filtros.get("sitio"))
    _validar_usuario(filtros.get("usuario"))
    _validar_fechas(filtros)
    _validar_nro_pagina(params.get("nro_pagina"))
    _validar_orden(params.get("orden"))


def _validar_calificacion(cal_min: str, cal_max: str):
    """
    Valida que las calificaciones mínimas y máximas sean números enteros entre 1 y 5,
    y que la calificación mínima no sea mayor que la máxima.

    Args:
        cal_min (str): El valor de la calificación mínima.
        cal_max (str): El valor de la calificación máxima.

    Raises:
        ValueError: Si los valores no son numéricos, no están en el rango [1, 5],
                    o si `cal_min` es mayor que `cal_max`.
    """
    for clave, valor in [
        ("calificacion_min", cal_min),
        ("calificacion_max", cal_max),
    ]:
        if valor and valor != "" and not valor.isspace():
            if not str(valor).isdigit():
                raise ValueError(f"{clave} debe ser numérico")

            valor_int = int(valor)
            if valor_int < 1 or valor_int > 5:
                raise ValueError(f"{clave} debe estar entre 1 y 5")

    if cal_min and cal_max and int(cal_min) > int(cal_max):
        raise ValueError(
            "El valor de calificacion_min no puede ser mayor que el valor de calificacion_max"
        )


def _validar_estado(estado: str):
    """
    Valida que el filtro de estado sea un valor numérico si está presente.

    Args:
        estado (str): El valor del estado de la reseña.

    Raises:
        ValueError: Si el valor de estado no es numérico.
    """
    if estado and estado != "" and not estado.isspace():
        if not str(estado).isdigit():
            raise ValueError("El valor de estado debe ser numérico")


def _validar_sitio(sitio: str):
    """
    Valida que el filtro de ID de sitio sea un valor numérico si está presente.

    Args:
        sitio (str): El ID del sitio para filtrar.

    Raises:
        ValueError: Si el valor de sitio no es numérico.
    """
    if sitio and sitio != "" and not sitio.isspace():
        if not str(sitio).isdigit():
            raise ValueError("El valor de sitio debe ser numérico")


def _validar_usuario(usuario: str):
    """
    Valida que el filtro de nombre de usuario no exceda los 100 caracteres.

    Args:
        usuario (str): El nombre de usuario para filtrar.

    Raises:
        ValueError: Si la longitud del nombre de usuario supera los 100 caracteres.
    """
    if usuario is not None:
        if len(usuario) > 100:
            raise ValueError("El valor de usuario no puede superar 100 caracteres")


def _validar_fechas(filtros: dict):
    """
    Valida el formato de las fechas de inicio (`fecha_desde`) y fin (`fecha_hasta`),
    y que la fecha de inicio no sea posterior a la fecha de fin.

    Args:
        filtros (dict): Diccionario que contiene las claves 'fecha_desde' y 'fecha_hasta'.

    Raises:
        ValueError: Si el formato de alguna fecha es incorrecto (YYYY-MM-DD) o
                    si `fecha_desde` es posterior a `fecha_hasta`.
    """
    fecha_desde = filtros.get("fecha_desde")
    fecha_hasta = filtros.get("fecha_hasta")

    formato_fecha = "%Y-%m-%d"

    def _parse_fecha(fecha_str, nombre, es_inicio=True):
        """
        Función interna para parsear y validar el formato de una cadena de fecha (YYYY-MM-DD).

        Args:
            fecha_str (str): La cadena de fecha a parsear.
            nombre (str): El nombre del campo (e.g., 'fecha_desde') para el mensaje de error.
            es_inicio (bool): Indica si se debe establecer la hora al inicio (min) o al final (max) del día.

        Returns:
            datetime: El objeto datetime parseado.

        Raises:
            ValueError: Si el formato de la cadena de fecha es incorrecto.
        """
        try:
            return datetime.combine(
                datetime.strptime(fecha_str, formato_fecha),
                time.min if es_inicio else time.max,
            )
        except ValueError:
            raise ValueError(
                f"El valor de {nombre} tiene un formato inválido, debe ser YYYY-MM-DD"
            )

    fecha_desde_formateada = (
        _parse_fecha(fecha_desde, "fecha_desde", es_inicio=True)
        if fecha_desde
        else None
    )
    fecha_hasta_formateada = (
        _parse_fecha(fecha_hasta, "fecha_hasta", es_inicio=False)
        if fecha_hasta
        else None
    )

    if (
        fecha_desde_formateada
        and fecha_hasta_formateada
        and fecha_desde_formateada > fecha_hasta_formateada
    ):
        raise ValueError(
            "El valor de fecha_desde no puede ser mayor que el valor de fecha_hasta"
        )


def _validar_nro_pagina(nro_pagina: int):
    """
    Valida que el parámetro de paginación (`nro_pagina`) sea un número entero positivo mayor a 0.

    Args:
        nro_pagina (int): El número de página solicitado.

    Raises:
        ValueError: Si `nro_pagina` no es un entero positivo válido.
    """
    if nro_pagina:
        if not str(nro_pagina).isdigit() or int(nro_pagina) <= 0:
            raise ValueError(
                "El valor de nro_pagina debe ser un número entero positivo mayor a 0"
            )


def _validar_orden(orden: str):
    """
    Valida que el parámetro de ordenamiento (`orden`) sea uno de los valores permitidos.

    Los valores válidos son: "fecha_asc", "fecha_desc", "calificacion_asc", "calificacion_desc".

    Args:
        orden (str): El criterio de ordenamiento.

    Raises:
        ValueError: Si el valor de `orden` no es un criterio de ordenamiento válido.
    """
    ordenes_validos = [
        "fecha_asc",
        "fecha_desc",
        "calificacion_asc",
        "calificacion_desc",
    ]

    if orden and orden != "" and not orden.isspace() and orden not in ordenes_validos:
        raise ValueError(f"El valor de orden ingresado '{orden}' es inválido")
