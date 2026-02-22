"""Repositorio SQLAlchemy de Sitios Históricos.

Implementa las operaciones CRUD, filtrado, paginación, manejo de tags y
registro de historial de modificaciones.
"""

from core.sitios_historicos import existe_tag_nombre_slug
from core.utils.sitios_utils import aplicar_filtros_y_ordenamiento
from core.utils.pagination import paginate
from ..database import db
from flask import current_app
from core.sitios_historicos.sitio_historico import SitioHistorico, sitios_tags
from core.sitios_historicos.categoria import Categoria
from core.sitios_historicos.estado_conservacion import EstadoConservacion
from core.sitios_historicos.tag import Tag
from core.sitios_historicos.imagen import Imagen
from core.localidad.ciudad import Ciudad
from core.localidad.provincia import Provincia
from web.validators.file_validators import validate_image_file
from core.utils.storage_utils import (
    upload_file_to_minio,
    delete_file_from_minio,
    move_file_from_temp_to_site,
)
from web.dtos.site_dto import SiteDTO
from .site_repository import SiteRepository
from sqlalchemy import delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
from slugify import slugify
from core import historial
from geoalchemy2.elements import WKTElement
from core.localidad import (
    obtener_provincia_id,
    existe_ciudad_provincia,
    crear_ciudad,
)

class SiteRepo(SiteRepository):
    """Repositorio de sitios basado en SQLAlchemy."""

    def _to_dto(self, model: SitioHistorico) -> SiteDTO:
        """Convierte un modelo Sitio Historico a un objeto DTO."""

        all_images_dto = [img.to_dto() for img in model.imagenes]

        sorted_images = sorted(
            all_images_dto,
            key=lambda img: (not img["es_portada"], img["orden"]),
        )
        portada_obj = sorted_images[0] if sorted_images else None
        ciudad_nombre = model.ciudad.nombre if model.ciudad else "N/A"
        provincia_nombre = (
            model.ciudad.provincia.nombre
            if model.ciudad and model.ciudad.provincia
            else "N/A"
        )
        categoria_desc = model.categoria.descripcion if model.categoria else "N/A"
        estado_desc = (
            model.estado_conservacion.descripcion
            if model.estado_conservacion
            else "N/A"
        )

        return SiteDTO(
            id=model.id_sitio,
            nombre=model.nombre,
            descripcion_breve=model.descripcion_breve,
            descripcion_detallada=model.descripcion_completa,
            anio_inauguracion=model.anio_inauguracion,
            ciudad=ciudad_nombre,
            provincia=provincia_nombre,
            latitud=model.lat,
            longitud=model.lon,
            visible=model.es_visible,
            eliminado=model.eliminado,
            categoria=categoria_desc,
            estado=estado_desc,
            tags=[t.nombre for t in model.tags] if model.tags else [],
            fecha_hora_alta=(
                model.fecha_hora_alta.strftime("%Y-%m-%d %H:%M:%S")
                if model.fecha_hora_alta
                else None
            ),
            images=sorted_images,
            url_portada=portada_obj["url_publica"] if portada_obj else None,
            alt_portada=(
                portada_obj["titulo_alt"]
                if portada_obj
                else f"Imagen de {model.nombre}"
            ),
        )

    def create(self, dto: SiteDTO, user_id: int, imagenes_data: list = None) -> SiteDTO:
        """Crea un sitio histórico y registra el historial de creación."""
        try:
            id_provincia = obtener_provincia_id(dto.provincia)
            if not id_provincia:
                raise ValueError(f"La provincia '{dto.provincia}' no fue encontrada.")

            ciudad_id = existe_ciudad_provincia(dto.ciudad, dto.provincia)
            if ciudad_id is None:
                try:
                    ciudad_id = crear_ciudad(dto.ciudad, id_provincia, commit=False)
                except Exception as e:
                    current_app.logger.error(
                        f"Error al crear la ciudad '{dto.ciudad}': {e}"
                    )
                    raise e

            new_site = SitioHistorico(
                nombre=dto.nombre,
                descripcion_breve=dto.descripcion_breve,
                descripcion_completa=dto.descripcion_detallada,
                anio_inauguracion=dto.anio_inauguracion,
                es_visible=dto.visible,
                id_categoria=dto.categoria_id,
                id_estado_cons=dto.estado_id,
                id_ciudad=ciudad_id,
            )

            if dto.tags:
                tag_objects = self._get_tags(dto.tags)
                new_site.tags = tag_objects

            if dto.latitud is not None and dto.longitud is not None:
                new_site.location = WKTElement(
                    f"POINT({dto.longitud} {dto.latitud})", srid=4326
                )

            db.session.add(new_site)

            db.session.flush()

            if imagenes_data:
                self._procesar_imagenes_temporales(
                    new_site.id_sitio, imagenes_data
                )

            historial.registrar_evento_simple(new_site.id_sitio, user_id, "Creacion")

            db.session.commit()

            return self._to_dto(new_site)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Error de integridad al crear sitio: {e}")
            raise e
        except ValueError as ve:
            db.session.rollback()
            current_app.logger.error(
                f"Error al crear sitio a partir de los datos ingresados: {ve}"
            )
            raise ve

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error inesperado al crear sitio: {e}")
            raise e

    def get(self, site_id: int) -> SiteDTO | None:
        """Obtiene un sitio por ID devolviendo su DTO o ``None`` si no existe."""
        site = (
            db.session.query(SitioHistorico)
            .options(
                selectinload(SitioHistorico.imagenes),
                selectinload(SitioHistorico.tags),
                joinedload(SitioHistorico.ciudad).joinedload(Ciudad.provincia),
                joinedload(SitioHistorico.categoria),
                joinedload(SitioHistorico.estado_conservacion),
            )
            .filter(SitioHistorico.id_sitio == site_id)
            .filter(SitioHistorico.eliminado == False)
            .one_or_none()
        )

        if site:
            return self._to_dto(site)
        return None

    def list(self, filtros=None, orden=None, page=1, per_page=None):
        """Lista sitios con filtros, orden y paginación, devolviendo DTOs y metadatos."""
        query = db.session.query(SitioHistorico).filter(
            SitioHistorico.eliminado == False
        )
        query_con_filtros = aplicar_filtros_y_ordenamiento(query, filtros, orden)
        query_completa = query_con_filtros.options(
            selectinload(SitioHistorico.imagenes),
            joinedload(SitioHistorico.ciudad).joinedload(Ciudad.provincia),
            joinedload(SitioHistorico.categoria),
            joinedload(SitioHistorico.estado_conservacion),
            joinedload(SitioHistorico.tags),
        )

        items, pagination = paginate(query_completa, page, per_page)
        return [self._to_dto(item) for item in items], pagination

    def listar_para_exportar(self, filtros=None, orden=None):
        """Retorna la query filtrada completa para exportar sin paginación."""
        query = db.session.query(SitioHistorico).filter(
            SitioHistorico.eliminado == False
        )

        query_completa = aplicar_filtros_y_ordenamiento(query, filtros, orden)

        return query_completa.all()

    from geoalchemy2.elements import WKTElement
    from geoalchemy2.shape import to_shape

    def update(
        self,
        site_id: int,
        dto: SiteDTO,
        user_id: int,
        imagenes_data: list = None,
    ) -> SiteDTO:
        """Actualiza campos del sitio, ubicación y relaciones; registra historial."""
        site = db.session.get(SitioHistorico, site_id)
        if not site:
            raise ValueError("Sitio no encontrado.")

        try:
            dto.categoria_id = self.obtener_categoria_id(dto.categoria)
            dto.estado_id = self.obtener_estado_id(dto.estado)
            id_provincia_nueva = obtener_provincia_id(dto.provincia)
            if not id_provincia_nueva:
                raise ValueError(f"La provincia '{dto.provincia}' no fue encontrada.")

            ciudad_id_nueva = existe_ciudad_provincia(dto.ciudad, dto.provincia)
            if ciudad_id_nueva is None:
                try:
                    ciudad_id_nueva = crear_ciudad(
                        dto.ciudad, id_provincia_nueva, commit=False
                    )
                except Exception as e:
                    current_app.logger.error(
                        f"Error al crear la ciudad '{dto.ciudad}': {e}"
                    )
                    raise e

            dto.ciudad_id = ciudad_id_nueva

            historial.registrar_cambios_update(site, dto, user_id, self)
            site.nombre = dto.nombre.strip()
            site.descripcion_breve = dto.descripcion_breve
            site.descripcion_completa = dto.descripcion_detallada
            site.anio_inauguracion = dto.anio_inauguracion
            site.es_visible = dto.visible
            site.id_categoria = dto.categoria_id
            site.id_estado_cons = dto.estado_id
            site.id_ciudad = dto.ciudad_id

            if dto.latitud is not None and dto.longitud is not None:
                site.location = WKTElement(
                    f"POINT({dto.longitud} {dto.latitud})", srid=4326
                )

            if dto.tags is not None:
                nuevos_tags_obj = self._get_tags(dto.tags)
                site.tags.clear()
                for tag_obj in nuevos_tags_obj:
                    site.tags.append(tag_obj)

            if imagenes_data:
                self._actualizar_estado_imagenes(site_id, imagenes_data, user_id)

            db.session.commit()

            return self._to_dto(site)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error de integridad al actualizar el  sitio: {e}"
            )
            raise e

        except ValueError as ve:
            db.session.rollback()
            current_app.logger.error(
                f"Error al actualizar el sitio a partir de los datos ingresados: {ve}"
            )
            raise ve

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"ERROR AL ACTUALIZAR SITIO {site_id}: {e}")
            raise ValueError(f"No se pudo actualizar el sitio. Error: {e}")

    def delete(self, site_id: int, user_id: int):
        """Marca como eliminado un sitio y registra el evento en el historial."""
        site = db.session.get(SitioHistorico, site_id)
        if not site:
            raise ValueError("Sitio no encontrado.")
        else:
            historial.registrar_evento_simple(site.id_sitio, user_id, "Eliminacion")

            stmt_delete_tags = delete(sitios_tags).where(
                sitios_tags.c.id_sitio == site_id
            )
            db.session.execute(stmt_delete_tags)

            site.eliminado = True
            db.session.commit()

    def _procesar_imagenes_temporales(
        self, site_id: int, imagenes_data: list
    ) -> List[Imagen]:
        """
        Mueve imágenes de temp/ a sitios/<id>/ y crea los registros en la BD.

        Esta función es reutilizable tanto para crear como para editar sitios.

        :param site_id: ID del sitio al que pertenecerán las imágenes
        :param imagenes_data: Lista de diccionarios con los datos de las imágenes temporales
                              [{"object_name_minio": "public/temp/...", "titulo_alt": "...", ...}]
        :return: Lista de objetos Imagen creados
        """
        imagenes_creadas = []

        for img_data in imagenes_data:
            temp_object_name = img_data.get("object_name_minio")

            if not temp_object_name:
                current_app.logger.warning("Imagen sin object_name_minio, saltando...")
                continue

            if not temp_object_name.startswith("public/temp/"):
                current_app.logger.warning(
                    f"Imagen '{temp_object_name}' no está en carpeta temporal, saltando..."
                )
                continue

            try:
                new_url, new_object_name = move_file_from_temp_to_site(
                    temp_object_name, site_id
                )

                titulo_alt_raw = img_data.get("titulo_alt", "Sin título")
                titulo_alt = (
                    titulo_alt_raw[:50] if len(titulo_alt_raw) > 50 else titulo_alt_raw
                )

                descripcion_raw = img_data.get("descripcion")
                descripcion = (
                    descripcion_raw[:100]
                    if descripcion_raw and len(descripcion_raw) > 100
                    else descripcion_raw
                )

                nueva_imagen = Imagen(
                    id_sitio_historico=site_id,
                    url_publica=new_url,
                    object_name_minio=new_object_name,
                    titulo_alt=titulo_alt,
                    descripcion=descripcion,
                    es_portada=img_data.get("es_portada", False),
                    orden=img_data.get("orden", 0),
                )

                db.session.add(nueva_imagen)
                imagenes_creadas.append(nueva_imagen)

            except Exception as e:
                current_app.logger.error(
                    f"Error procesando imagen temporal {temp_object_name}: {e}"
                )
                continue

        return imagenes_creadas

    def _get_tags(self, tag_names: List[str]) -> List[Tag]:
        """
        Convierte una lista de nombres de tags (strings) en una lista de objetos Tag
        existentes.
        """
        tags = []

        for nombre in tag_names:
            clean_name = nombre.strip().lower()
            if not clean_name:
                continue

            slug = slugify(clean_name)

            tag = existe_tag_nombre_slug(clean_name, slug)

            if not tag:
                raise ValueError(f"El tag '{nombre}' no existe.")

            tags.append(tag)

        return tags

    def _actualizar_estado_imagenes(
        self, site_id: int, imagenes_data: list, user_id: int = None
    ):
        """
        Actualiza el estado (portada, orden) de las imágenes de un sitio.
        También procesa imágenes temporales (sin id_imagen) y las mueve a la carpeta definitiva.

        :param site_id: ID del sitio
        :param imagenes_data: Lista de diccionarios con los datos de las imágenes
                              [{"id_imagen": 1, "es_portada": True, "orden": 1}, ...]
                              o [{"object_name_minio": "temp/...", "titulo_alt": "...", ...}]
        :param user_id: ID del usuario que realiza el cambio (para registrar en historial)
        """

        hay_cambios = False

        imagenes_existentes = [img for img in imagenes_data if img.get("id_imagen")]
        imagenes_temporales = [img for img in imagenes_data if not img.get("id_imagen")]

        if imagenes_temporales:
            imagenes_creadas = self._procesar_imagenes_temporales(
                site_id, imagenes_temporales
            )
            if imagenes_creadas:
                hay_cambios = True

        for imagen_data in imagenes_existentes:
            imagen_id = imagen_data.get("id_imagen")
            es_portada = imagen_data.get("es_portada", False)
            orden = imagen_data.get("orden", 0)

            imagen = db.session.query(Imagen).filter_by(id_imagen=imagen_id).first()
            if imagen and imagen.id_sitio_historico == site_id:
                if imagen.es_portada != es_portada or imagen.orden != orden:
                    hay_cambios = True

                imagen.es_portada = es_portada
                imagen.orden = orden
            else:
                current_app.logger.warning(
                    f"Imagen {imagen_id} no encontrada o no pertenece al sitio {site_id}"
                )

        if hay_cambios and user_id:
            try:
                historial.registrar_evento_simple(
                    sitio_id=site_id,
                    user_id=user_id,
                    accion_desc="Cambio de Imagenes",
                )
            except Exception as e:
                current_app.logger.warning(
                    f"No se pudo registrar el historial de actualización de imágenes: {e}"
                )

    def obtener_tags(self, site_id: int) -> List[Dict]:
        """Devuelve los tags de un sitio en formato de lista de diccionarios."""
        site = (
            db.session.query(SitioHistorico)
            .filter(SitioHistorico.id_sitio == site_id)
            .first()
        )
        if site:
            return [
                {"id_tag": tag.id_tag, "nombre": tag.nombre, "slug": tag.slug}
                for tag in site.tags
            ]
        return []

    def listar_tags(self) -> List[Dict]:
        """Lista todos los tags disponibles ordenados alfabéticamente."""
        tags = db.session.query(Tag).order_by(Tag.nombre.asc()).all()
        return [{"id_tag": t.id_tag, "nombre": t.nombre} for t in tags]

    def obtener_nombres_tags(self, site_id: int) -> List[str]:
        """Devuelve solo los nombres de los tags asociados a un sitio."""
        site = (
            db.session.query(SitioHistorico)
            .filter(SitioHistorico.id_sitio == site_id)
            .first()
        )
        if site:
            return [tag.nombre for tag in site.tags]
        return []

    def listar_nombre_localidad(self) -> List[Dict]:
        """
        Lista el ID, el nombre, la ciudad y la provincia de todos los Sitios Históricos.
        """
        datos_sitios = (
            db.session.query(
                SitioHistorico.id_sitio,
                SitioHistorico.nombre.label("nombre_sitio"),
                Ciudad.nombre.label("ciudad"),
                Provincia.nombre.label("provincia"),
            )
            .join(Ciudad, SitioHistorico.id_ciudad == Ciudad.id_ciudad)
            .join(Provincia, Ciudad.id_provincia == Provincia.id_provincia)
            .order_by(SitioHistorico.nombre.asc())
            .filter(SitioHistorico.eliminado == False)
            .all()
        )

        return [
            {
                "id_sitio": dato.id_sitio,
                "nombre": dato.nombre_sitio,
                "ciudad": dato.ciudad,
                "provincia": dato.provincia,
            }
            for dato in datos_sitios
        ]

    def listar_categorias(self) -> List[Dict]:
        """Lista categorías (id y descripción) ordenadas alfabéticamente."""
        categorias = (
            db.session.query(Categoria).order_by(Categoria.descripcion.asc()).all()
        )
        return [
            {"id_categoria": c.id_categoria, "descripcion": c.descripcion}
            for c in categorias
        ]

    def listar_estados(self) -> List[Dict]:
        """Lista estados de conservación (id y descripción)."""
        estados = (
            db.session.query(EstadoConservacion)
            .order_by(EstadoConservacion.descripcion.asc())
            .all()
        )
        return [
            {"id_estado_cons": e.id_estado_cons, "descripcion": e.descripcion}
            for e in estados
        ]

    def listar_provincias(self) -> List[Dict]:
        """Lista provincias (id y nombre) ordenadas alfabéticamente."""
        provincias = db.session.query(Provincia).order_by(Provincia.nombre.asc()).all()
        return [
            {"id_provincia": p.id_provincia, "nombre": p.nombre} for p in provincias
        ]

    def obtener_tags_sitio(self, site_id: int) -> List[Tag]:
        """Devuelve los nombres de tags asociados a un sitio."""
        site = (
            db.session.query(SitioHistorico)
            .filter(SitioHistorico.id_sitio == site_id)
            .first()
        )
        if site:
            return [tag.nombre for tag in site.tags]
        return []

    def obtener_categoria_nombre(self, categoria_id: int) -> str | None:
        """Obtiene la descripción de una categoría a partir de su ID."""
        categoria = (
            db.session.query(Categoria)
            .filter(Categoria.id_categoria == categoria_id)
            .first()
        )
        return categoria.descripcion if categoria else None

    def obtener_estado_nombre(self, estado_id: int) -> str | None:
        """Obtiene la descripción del estado de conservación por ID."""
        estado = (
            db.session.query(EstadoConservacion)
            .filter(EstadoConservacion.id_estado_cons == estado_id)
            .first()
        )
        return estado.descripcion if estado else None

    def obtener_categoria_id(self, nombre_categoria: str) -> int | None:
        """Busca una Categoría por su nombre y devuelve su ID."""
        categoria = (
            db.session.query(Categoria)
            .filter(Categoria.descripcion.ilike(nombre_categoria.strip()))
            .first()
        )
        return categoria.id_categoria if categoria else None

    def obtener_estado_id(self, nombre_estado: str) -> int | None:
        """Busca un Estado de Conservación por su descripción y devuelve su ID."""
        estado = (
            db.session.query(EstadoConservacion)
            .filter(EstadoConservacion.descripcion.ilike(nombre_estado.strip()))
            .first()
        )
        return estado.id_estado_cons if estado else None

    def get_site_name_by_id(self, site_id: int) -> str | None:
        """Devuelve solo el nombre de un sitio por su ID."""
        sitio = (
            db.session.query(SitioHistorico.nombre)
            .filter(SitioHistorico.id == site_id)
            .first()
        )
        return sitio.nombre if sitio else None

    def eliminar_imagen(self, id_imagen: int, user_id: int = None):
        """
        Elimina una imagen del sistema (MinIO y base de datos).

        Si la imagen a eliminar es portada y hay otras imágenes disponibles,
        automáticamente marca la primera imagen restante como portada.
        No permite eliminar la única imagen del sitio si es portada.

        :param user_id: ID del usuario que realiza la acción (para registrar en historial)
        """
        imagen = db.session.get(Imagen, id_imagen)

        if not imagen:
            current_app.logger.warning(
                f"Intento de eliminar imagen no encontrada: ID {id_imagen}"
            )
            raise ValueError("Imagen no encontrada.")

        id_sitio = imagen.id_sitio_historico

        total_imagenes = (
            db.session.query(Imagen).filter_by(id_sitio_historico=id_sitio).count()
        )

        if total_imagenes == 1 and imagen.es_portada:
            raise ValueError("No se puede eliminar la única imagen del sitio.")

        if imagen.es_portada and total_imagenes > 1:
            otra_imagen = (
                db.session.query(Imagen)
                .filter(
                    Imagen.id_sitio_historico == id_sitio,
                    Imagen.id_imagen != id_imagen,
                )
                .order_by(Imagen.orden.asc())
                .first()
            )

            if otra_imagen:
                otra_imagen.es_portada = True

        delete_file_from_minio(imagen.object_name_minio)

        db.session.delete(imagen)
        db.session.commit()

        if user_id:
            try:
                historial.registrar_evento_simple(
                    sitio_id=id_sitio,
                    user_id=user_id,
                    accion_desc="Cambio de Imagenes",
                )
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(
                    f"No se pudo registrar el historial de imagen eliminada: {e}"
                )

    def upload_imagen_temporal(self, file_storage):
        """
        Valida y sube una imagen a MinIO de forma temporal (carpeta temp/).
        No la guarda en la base de datos.
        Devuelve un diccionario con la URL y el nombre del objeto.
        """
        validate_image_file(file_storage)

        url_publica, object_name = upload_file_to_minio(file_storage, site_id=None)

        return {"url_publica": url_publica, "object_name_minio": object_name}

    def delete_temporal_image(self, object_name: str):
        """
        Elimina un archivo de MinIO que fue subido temporalmente.
        """
        if not object_name:
            raise ValueError("Falta el nombre del objeto a eliminar.")

        delete_file_from_minio(object_name)
