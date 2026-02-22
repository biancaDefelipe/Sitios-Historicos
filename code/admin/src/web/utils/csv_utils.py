"""Utilidades para generar y exportar datos a CSV."""

import csv
import io
from datetime import datetime


FORMATO_FECHA_HORA = "%Y%m%d_%H%M"


def generar_csv(data: list[dict], headers: list[str], prefijo_archivo="export"):
    """
    Genera un CSV en memoria y devuelve el contenido como bytes.

    :param data: Lista con el contenido (filas)
    :param headers: Lista con los encabezados (columnas)
    :param prefijo_archivo: Prefijo para el nombre del archivo.
    :return: (filename, csv_bytes)
    """
    fecha_hora = datetime.now().strftime(FORMATO_FECHA_HORA)
    nombre_archivo = f"{prefijo_archivo}_{fecha_hora}.csv"

    archivo = io.StringIO(newline="")
    writer = csv.DictWriter(
        archivo, fieldnames=headers, delimiter=",", quoting=csv.QUOTE_ALL
    )
    writer.writeheader()

    for fila in data:
        writer.writerow(fila)

    return nombre_archivo, archivo.getvalue().encode("utf-8")


def obtener_data_headers_sitios(sitios):
    """Arma datos y encabezados para exportar sitios a CSV.

    Args:
        sitios: Iterable de objetos SitioHistorico.

    Returns:
        tuple[list[dict], list[str]]: Tupla con la lista de filas y headers.
    """
    data = []
    for sitio in sitios:
        tags = ", ".join([t.nombre for t in sitio.tags]) if sitio.tags else ""
        data.append(
            {
                "ID": sitio.id_sitio,
                "Nombre": sitio.nombre,
                "Descripción breve": sitio.descripcion_breve,
                "Ciudad": sitio.ciudad.nombre,
                "Provincia": sitio.ciudad.provincia.nombre,
                "Estado Conservación": sitio.estado_conservacion.descripcion,
                "Fecha y Hora Alta": sitio.fecha_hora_alta.strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
                "Coordenadas (Lat,Lon)": f"{sitio.lat},{sitio.lon}",
                "Tags": tags,
            }
        )

    headers = [
        "ID",
        "Nombre",
        "Descripción breve",
        "Ciudad",
        "Provincia",
        "Estado Conservación",
        "Fecha y Hora Alta",
        "Coordenadas (Lat,Lon)",
        "Tags",
    ]

    return data, headers
