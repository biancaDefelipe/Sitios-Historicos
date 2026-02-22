
import { 
    showFeedback, 
    handleDragStart as dragStartHelper,
    handleDragOver as dragOverHelper,
    handleDragEnd as dragEndHelper,
    handleDropWithCoverRestriction,
    recalculateOrder,
    updateImageCounter,
    cleanupWithBeacon,
    cleanupImagesAsync
} from './image_gallery_helpers.js';

export class EditImageManager {
    constructor(siteId, existingImagesJson) {
        this.siteId = parseInt(siteId, 10);

        this.gallery = document.getElementById('image-gallery-container');
        this.dropZone = document.getElementById('drop-zone');
        this.fileInput = document.getElementById('file-input');
        this.hiddenInput = document.getElementById('imagenes_json_data');

        if (!this.gallery || !this.dropZone || !this.fileInput || !this.siteId || !this.hiddenInput) {
            console.error("Faltan elementos del DOM o el siteId para EditImageManager.");
            return;
        }

        try {
            this.images = JSON.parse(existingImagesJson);
        } catch (e) {
            console.error("Error al parsear imágenes existentes:", e);
            this.images = [];
        }
        
        this.imagenesTemporales = [];
        this.estáGuardando = false;
        this.init();
    }

    init() {
        this.renderGallery();

        this.dropZone.addEventListener('click', (e) => {
            if (e.target.closest('label[for="file-input"]')) return;
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => this.handleFiles(e.target.files));

        ['dragover', 'dragleave', 'drop'].forEach(event => {
            this.dropZone.addEventListener(event, (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (event === 'dragover') this.dropZone.classList.add('border-blue-500', 'bg-blue-50');
                else this.dropZone.classList.remove('border-blue-500', 'bg-blue-50');
                if (event === 'drop') this.handleFiles(e.dataTransfer.files);
            });
        });

        this.gallery.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;
            
            const imageDiv = button.closest('[data-image-id]');
            if (!imageDiv) return;

            const imageId = imageDiv.dataset.imageId;
            
            if (button.classList.contains('btn-delete-img')) {
                e.preventDefault();
                this.deleteImage(imageId);
            }
            
            if (button.classList.contains('btn-set-cover')) {
                e.preventDefault();
                this.setCoverImage(imageId);
            }
        });

        this.setupDragAndDrop();
    }

    renderGallery() {
        this.gallery.innerHTML = '';

        if (!this.images || this.images.length === 0) {
            this.gallery.innerHTML = '<p class="text-gray-500 text-center">No hay imágenes cargadas.</p>';
            updateImageCounter(this.images, this.dropZone, this.fileInput); 
            return;
        }

        this.images.sort((a, b) => (a.orden || 0) - (b.orden || 0));
        
        updateImageCounter(this.images, this.dropZone, this.fileInput);

        this.images.forEach((imagen, index) => {
            if (imagen.eliminado === true) return;

            const imgId = imagen.id_imagen || imagen.object_name_minio;
            const titulo = imagen.titulo_alt || 'Sin título';
            const urlPublica = imagen.url_publica;
            const esPortada = imagen.es_portada;
            const orden = imagen.orden !== undefined ? imagen.orden : index + 1;

            const div = document.createElement('div');
            div.className = 'relative group border rounded-lg overflow-hidden shadow cursor-move';
            div.setAttribute('data-image-id', imgId);
            div.setAttribute('draggable', 'true');

            const portadaBadge = esPortada 
                ? '<span class="absolute top-2 left-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded-full z-10">Portada</span>' 
                : '';
            
            const ordenBadge = `<span class="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full z-10">#${orden}</span>`;
            
            const starButton = !esPortada
                ? '<button type="button" title="Marcar como portada" class="btn-set-cover bg-yellow-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-yellow-600"><i class="fas fa-star"></i></button>'
                : '';
            
            const deleteButton = !esPortada
                ? '<button type="button" title="Eliminar" class="btn-delete-img bg-red-600 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-700"><i class="fas fa-trash"></i></button>'
                : '';
            
            div.innerHTML = `
                ${portadaBadge}
                ${ordenBadge}
                <img src="${urlPublica}" alt="${titulo}" class="w-full h-32 object-cover pointer-events-none">
                <div class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                    <button type="button" title="Mover (Arrastra para ordenar)" class="btn-drag-hint bg-gray-600 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-700"><i class="fas fa-arrows-alt"></i></button>
                    ${starButton}
                    ${deleteButton}
                </div>
            `;
            
            div.addEventListener('dragstart', (e) => this.handleDragStart(e));
            div.addEventListener('dragover', (e) => this.handleDragOver(e));
            div.addEventListener('drop', (e) => this.handleDrop(e));
            div.addEventListener('dragend', (e) => this.handleDragEnd(e));
            
            this.gallery.appendChild(div);
        });
    }

    setupDragAndDrop() {
    }

    handleDragStart(e) {
        const result = dragStartHelper(e, 'data-image-id');
        this.draggedElement = result.draggedElement;
        this.draggedImageId = result.draggedId;
    }

    handleDragOver(e) {
        return dragOverHelper(e, 'data-image-id', this.draggedElement);
    }

    handleDrop(e) {
        const findImageFn = (img, id) => 
            (img.id_imagen && img.id_imagen == id) || 
            (img.object_name_minio === id);
        
        const result = handleDropWithCoverRestriction(
            e,
            this.images,
            this.draggedImageId,
            'data-image-id',
            findImageFn
        );

        if (result && result.reordered) {
            this.images = result.images;
            this.renderGallery();
            
            if (result.showSuccessFeedback) {
                showFeedback('Orden actualizado');
            }
        }

        return false;
    }

    handleDragEnd(e) {
        dragEndHelper(e, this.draggedElement, 'data-image-id');
        this.draggedElement = null;
        this.draggedImageId = null;
    }

    setCoverImage(imageId) {
        const selectedIndex = this.images.findIndex(img => 
            (img.id_imagen && img.id_imagen == imageId) || 
            (img.object_name_minio === imageId)
        );
        
        if (selectedIndex === -1) return;
        
        this.images.forEach(img => img.es_portada = false);
        
        this.images[selectedIndex].es_portada = true;
        
        const [selectedImage] = this.images.splice(selectedIndex, 1);
        
        this.images.unshift(selectedImage);
        
        recalculateOrder(this.images);
        
        this.renderGallery();
        showFeedback('Orden actualizado');
    }

    async handleFiles(files) {
        for (const file of files) {
            if (this.images.length >= 10) {
                alert('Has alcanzado el límite de 10 imágenes por sitio.');
                break;
            }
            
            let titulo_alt = prompt(`Ingresa un nombre alternativo para la imagen:`, file.name);
            
            if (titulo_alt === null) {
                continue;
            }
            
            let nombreFinal = titulo_alt.trim() === '' ? file.name : titulo_alt.trim();
            
            if (nombreFinal.length > 50) {
                const truncado = nombreFinal.substring(0, 50);
                const confirmar = confirm(
                    `El nombre "${nombreFinal}" es demasiado largo (máx. 50 caracteres).\n\n` +
                    `Se truncará a: "${truncado}"\n\n` +
                    `¿Continuar?`
                );
                
                if (!confirmar) {
                    continue; 
                }
                
                nombreFinal = truncado;
            }
            
            await this.uploadFile(file, nombreFinal);
        }
    }

    async uploadFile(file, titulo_alt) {
        if (!file.type.startsWith('image/')) {
            alert('Solo se permiten archivos de imagen.');
            return;
        }

        const maxSizeMB = 5;
        if (file.size > maxSizeMB * 1024 * 1024) {
            alert(`El archivo ${file.name} supera el tamaño máximo de ${maxSizeMB} MB.`);
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('titulo_alt', titulo_alt);

        try {
            const response = await fetch(`/sitios/imagenes/upload_temporal`, { 
                method: 'POST', 
                body: formData 
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al subir la imagen');
            }

            const newImageData = await response.json();

            const imagenTemporal = {
                object_name_minio: newImageData.object_name_minio,
                url_publica: newImageData.url_publica,
                titulo_alt: titulo_alt,
                es_portada: this.images.length === 0,
                orden: this.images.length + 1,
            };

            this.images.push(imagenTemporal);
            this.imagenesTemporales.push(newImageData.object_name_minio);
            
            this.renderGallery();

        } catch (error) {
            console.error('Error al subir imagen temporal:', error);
            alert(`Error al subir la imagen: ${error.message}`);
        }
    }

    async deleteImage(imageId) {
        const imgData = this.images.find(img => 
            (img.id_imagen && img.id_imagen == imageId) || 
            (img.object_name_minio === imageId)
        );

        if (!imgData) {
            console.warn('Imagen no encontrada:', imageId);
            return;
        }

        const confirmar = confirm(`¿Eliminar la imagen "${imgData.titulo_alt || 'Sin título'}"?`);
        if (!confirmar) return;

        try {
            let response;
            
            if (imgData.id_imagen) {
                response = await fetch(`/sitios/${this.siteId}/imagenes/${imgData.id_imagen}`, { 
                    method: 'DELETE' 
                });
            } else {
                response = await fetch(`/sitios/imagenes/delete_temporal`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ object_name_minio: imgData.object_name_minio })
                });
                
                const index = this.imagenesTemporales.indexOf(imgData.object_name_minio);
                if (index > -1) {
                    this.imagenesTemporales.splice(index, 1);
                }
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al eliminar la imagen');
            }

            this.images = this.images.filter(img => {
                const esEstaImagen = (img.id_imagen && img.id_imagen == imageId) || 
                                     (img.object_name_minio === imageId);
                return !esEstaImagen; 
            });

            recalculateOrder(this.images);

            this.renderGallery();

        } catch (error) {
            console.error('Error al eliminar imagen:', error);
            alert(`Error al eliminar la imagen: ${error.message}`);
        }
    }

    getImagesForSubmit() {
        return this.images
            .filter(img => !img.eliminado)
            .map((img, index) => {
                if (img.id_imagen) {
                    return {
                        id_imagen: img.id_imagen,
                        titulo_alt: img.titulo_alt,
                        es_portada: img.es_portada,
                        orden: index + 1
                    };
                } else {
                    return {
                        object_name_minio: img.object_name_minio,
                        titulo_alt: img.titulo_alt,
                        es_portada: img.es_portada,
                        orden: index + 1
                    };
                }
            });
    }

    _syncHiddenInput() {
        const imagenesData = this.getImagesForSubmit();
        this.hiddenInput.value = JSON.stringify(imagenesData);
    }

    async limpiarImagenesTemporales() {
        const objectNames = this.imagenesTemporales;
        const result = await cleanupImagesAsync(objectNames, '/sitios/imagenes/delete_temporal');
        
        this.imagenesTemporales = [];
        return result.errorCount === 0;
    }

    limpiarConBeacon() {
        cleanupWithBeacon(this.imagenesTemporales, '/sitios/imagenes/delete_temporal');
    }
}