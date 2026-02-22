
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

export class CreateImageManager {
    constructor() {
        this.gallery = document.getElementById('image-gallery-container');
        this.dropZone = document.getElementById('drop-zone');
        this.fileInput = document.getElementById('file-input');
        this.hiddenInput = document.getElementById('imagenes_json_data'); 
        
        if (!this.gallery || !this.dropZone || !this.fileInput || !this.hiddenInput) {
            console.error("Faltan elementos del DOM para CreateImageManager.");
            return;
        }

        this.images = []; 
        this.estáGuardando = false;
        this.init();
    }

    init() {
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
            
            const imageDiv = button.closest('[data-temp-id]');
            if (!imageDiv) return;

            const tempId = imageDiv.dataset.tempId;
            if (button.classList.contains('btn-delete-img')) {
                this.deleteImage(tempId);
            }
            if (button.classList.contains('btn-set-cover')) {
                this.setCoverImage(tempId);
            }
        });
    }

    _syncHiddenInput() {
        this.hiddenInput.value = JSON.stringify(this.images);
    }

    setCoverImage(tempId) {
        const selectedIndex = this.images.findIndex(img => img.id_imagen_temp === tempId);
        
        if (selectedIndex === -1) return;
        
        this.images.forEach(img => img.es_portada = false);
        
        this.images[selectedIndex].es_portada = true;
        
        const [selectedImage] = this.images.splice(selectedIndex, 1);
        
        this.images.unshift(selectedImage);
        
        recalculateOrder(this.images);
        
        this.renderGallery();
        showFeedback('Orden actualizado');
    }
    

    renderGallery() {
        this.gallery.innerHTML = '';
        
        this.images.sort((a, b) => (a.orden || 0) - (b.orden || 0));
        
        updateImageCounter(this.images, this.dropZone, this.fileInput);
        
        this.images.forEach((imagen, index) => {
            if (!imagen.orden || imagen.orden === 0) {
                imagen.orden = index + 1;
            }

            const div = document.createElement('div');
            div.className = 'relative group border rounded-lg overflow-hidden shadow cursor-move';
            div.setAttribute('data-temp-id', imagen.id_imagen_temp);
            div.setAttribute('draggable', 'true');

            const portadaBadge = imagen.es_portada 
                ? '<span class="absolute top-2 left-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded-full z-10">Portada</span>' 
                : '';
            
            const ordenBadge = `<span class="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full z-10">#${imagen.orden}</span>`;
            
            const starButton = !imagen.es_portada
                ? '<button type="button" title="Marcar como portada" class="btn-set-cover bg-yellow-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-yellow-600"><i class="fas fa-star"></i></button>'
                : '';
            
            const deleteButton = !imagen.es_portada
                ? '<button type="button" title="Eliminar" class="btn-delete-img bg-red-600 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-700"><i class="fas fa-trash"></i></button>'
                : '';
            
            div.innerHTML = `
                ${portadaBadge}
                ${ordenBadge}
                <img src="${imagen.url_publica}" alt="${imagen.titulo_alt}" class="w-full h-32 object-cover pointer-events-none">
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
        this._syncHiddenInput();
    }

    handleFiles(files) {
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
            
            this.uploadFile(file, nombreFinal);
        }
    }

    async uploadFile(file, titulo_alt) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/sitios/imagenes/upload_temporal', { method: 'POST', body: formData });
            if (!response.ok) throw new Error((await response.json()).error);
            
            const data = await response.json();
            
            const esPortada = this.images.length === 0;
            
            const nuevoOrden = this.images.length + 1;
            
            this.images.push({
                id_imagen_temp: `temp-${Date.now()}`,
                url_publica: data.url_publica,
                object_name_minio: data.object_name_minio,
                titulo_alt: titulo_alt,
                descripcion: "",
                es_portada: esPortada,
                orden: nuevoOrden
            });
            this.renderGallery();
        } catch (error) {
            alert(`Error al subir: ${error.message}`);
        }
    }

    async deleteImage(tempId) {
        const imgData = this.images.find(img => img.id_imagen_temp === tempId);
        if (!imgData) return;
        
        if (imgData.es_portada) {
            alert('No puedes eliminar la imagen portada. Marca otra imagen como portada primero.');
            return;
        }
        
        if (!confirm('¿Seguro que quieres eliminar esta imagen?')) return;

        try {
            const response = await fetch('/sitios/imagenes/delete_temporal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ object_name_minio: imgData.object_name_minio })
            });
            if (!response.ok) throw new Error((await response.json()).error);
            
            this.images = this.images.filter(img => img.id_imagen_temp !== tempId);
            
            recalculateOrder(this.images);
            
            this.renderGallery();
        } catch (error) {
            alert(`Error al eliminar: ${error.message}`);
        }
    }

    handleDragStart(e) {
        const result = dragStartHelper(e, 'data-temp-id');
        this.draggedElement = result.draggedElement;
        this.draggedTempId = result.draggedId;
    }

    handleDragOver(e) {
        return dragOverHelper(e, 'data-temp-id', this.draggedElement);
    }

    handleDrop(e) {
        const findImageFn = (img, id) => img.id_imagen_temp === id;
        
        const result = handleDropWithCoverRestriction(
            e,
            this.images,
            this.draggedTempId,
            'data-temp-id',
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
        dragEndHelper(e, this.draggedElement, 'data-temp-id');
        this.draggedElement = null;
        this.draggedTempId = null;
    }
    
    async limpiarTodasLasImagenesTemporales() {
        const objectNames = this.images
            .filter(img => img.object_name_minio)
            .map(img => img.object_name_minio);
        
        const result = await cleanupImagesAsync(objectNames, '/sitios/imagenes/delete_temporal');
        
        this.images = [];
        this.renderGallery();
        
        return result.errorCount === 0;
    }

    limpiarConBeacon() {
        const objectNames = this.images
            .filter(img => img.object_name_minio)
            .map(img => img.object_name_minio);
        
        cleanupWithBeacon(objectNames, '/sitios/imagenes/delete_temporal');
    }
}
