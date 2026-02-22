
/**
 * Muestra un feedback temporal en la esquina superior derecha.
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de feedback: 'success', 'warning', 'error'
 * @param {number} duration - Duración en milisegundos (default: 2000)
 */
export function showFeedback(message, type = 'success', duration = 2000) {
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    const icons = {
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-exclamation-circle'
    };
    
    const feedback = document.createElement('div');
    feedback.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        background-color: ${colors[type]};
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: opacity 0.3s ease-in-out;
        opacity: 1;
    `;
    feedback.innerHTML = `<i class="fas ${icons[type]}"></i><span>${message}</span>`;
    document.body.appendChild(feedback);
    
    setTimeout(() => {
        feedback.style.opacity = '0';
        setTimeout(() => feedback.remove(), 300);
    }, duration);
}

/**
 * Maneja el inicio del drag and drop.
 * @param {DragEvent} e - Evento de drag
 * @param {string} dataAttribute - Nombre del atributo data a usar ('data-temp-id' o 'data-image-id')
 * @returns {Object} - Objeto con draggedElement y draggedId
 */
export function handleDragStart(e, dataAttribute) {
    const draggedElement = e.target.closest(`[${dataAttribute}]`);
    const draggedId = draggedElement.dataset[dataAttribute.replace('data-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase())];
    
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', draggedElement.innerHTML);
    draggedElement.classList.add('opacity-50');
    
    return { draggedElement, draggedId };
}

/**
 * Maneja el drag over.
 * @param {DragEvent} e - Evento de drag
 * @param {string} dataAttribute - Nombre del atributo data a usar
 * @param {HTMLElement} draggedElement - Elemento siendo arrastrado
 */
export function handleDragOver(e, dataAttribute, draggedElement) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    
    const targetElement = e.target.closest(`[${dataAttribute}]`);
    if (targetElement && targetElement !== draggedElement) {
        targetElement.classList.add('border-blue-500', 'border-2');
    }
    return false;
}

/**
 * Maneja el fin del drag.
 * @param {DragEvent} e - Evento de drag
 * @param {HTMLElement} draggedElement - Elemento siendo arrastrado
 * @param {string} dataAttribute - Nombre del atributo data a usar
 */
export function handleDragEnd(e, draggedElement, dataAttribute) {
    if (draggedElement) {
        draggedElement.classList.remove('opacity-50');
    }
    
    
    const allItems = document.querySelectorAll(`[${dataAttribute}]`);
    allItems.forEach(item => {
        item.classList.remove('border-blue-500', 'border-2');
    });
}

/**
 * Maneja la lógica de drop con restricción de portada.
 * @param {DragEvent} e - Evento de drop
 * @param {Array} images - Array de imágenes
 * @param {string} draggedId - ID de la imagen arrastrada
 * @param {string} dataAttribute - Nombre del atributo data a usar
 * @param {Function} findImageFn - Función para encontrar imagen por ID
 * @returns {Object|null} - { reordered: boolean, images: Array } o null si no hubo cambios
 */
export function handleDropWithCoverRestriction(e, images, draggedId, dataAttribute, findImageFn) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }

    const targetElement = e.target.closest(`[${dataAttribute}]`);
    if (!targetElement) {
        return null;
    }

    
    const targetIdKey = dataAttribute.replace('data-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    const targetId = targetElement.dataset[targetIdKey];
    
    
    const draggedIndex = images.findIndex(img => findImageFn(img, draggedId));
    const targetIndex = images.findIndex(img => findImageFn(img, targetId));

    if (draggedIndex === -1 || targetIndex === -1 || draggedIndex === targetIndex) {
        return null;
    }

    const draggedImage = images[draggedIndex];
    const targetImage = images[targetIndex];
    
    if (!draggedImage.es_portada && targetIndex === 0 && targetImage.es_portada) {
        showFeedback(
            'La imagen portada se muestra primera por defecto. Colocando en posición 2.',
            'warning',
            3000
        );
        
        const [movedImage] = images.splice(draggedIndex, 1);
        images.splice(1, 0, movedImage);
    } else {
        const [movedImage] = images.splice(draggedIndex, 1);
        images.splice(targetIndex, 0, movedImage);
    }
    
    images.forEach((img, idx) => {
        img.orden = idx + 1;
    });
    
    const shouldShowSuccessFeedback = draggedImage.es_portada || targetIndex !== 0;
    
    return {
        reordered: true,
        images: images,
        showSuccessFeedback: shouldShowSuccessFeedback
    };
}

/**
 * Recalcula el orden de las imágenes después de una eliminación.
 * @param {Array} images - Array de imágenes
 * @returns {Array} - Array con orden recalculado
 */
export function recalculateOrder(images) {
    images.forEach((img, idx) => {
        img.orden = idx + 1;
    });
    return images;
}

/**
 * Actualiza el contador de imágenes y deshabilita/habilita inputs según el límite.
 * @param {Array} images - Array de imágenes
 * @param {HTMLElement} dropZone - Elemento del drop zone
 * @param {HTMLElement} fileInput - Input de archivos
 * @param {number} maxImages - Límite máximo de imágenes (default: 10)
 */
export function updateImageCounter(images, dropZone, fileInput, maxImages = 10) {
   
    let counterElement = document.getElementById('image-counter');
    if (!counterElement) {
    
        counterElement = document.createElement('div');
        counterElement.id = 'image-counter';
        counterElement.className = 'text-sm font-medium mb-2';
        

        dropZone.parentNode.insertBefore(counterElement, dropZone);
    }
    
    const count = images.length;
    const isAtLimit = count >= maxImages;
    
 
    if (isAtLimit) {
        counterElement.className = 'text-sm font-medium mb-2 text-red-600';
        counterElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${count}/${maxImages} imágenes (límite alcanzado)`;

        fileInput.disabled = true;
        dropZone.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        counterElement.className = 'text-sm font-medium mb-2 text-gray-700';
        counterElement.innerHTML = `<i class="fas fa-images"></i> ${count}/${maxImages} imágenes`;
   
        fileInput.disabled = false;
        dropZone.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

/**
 * Limpia imágenes temporales usando sendBeacon (para beforeunload).
 * @param {Array} objectNames - Array de object_name_minio a eliminar
 * @param {string} endpoint - Endpoint para la limpieza (ej: '/sitios/imagenes/delete_temporal')
 */
export function cleanupWithBeacon(objectNames, endpoint) {
    if (!objectNames || objectNames.length === 0) return;

    let sentCount = 0;

    for (const objectName of objectNames) {
        const data = JSON.stringify({ object_name_minio: objectName });
        const blob = new Blob([data], { type: 'application/json' });
        
        if (navigator.sendBeacon) {
            const sent = navigator.sendBeacon(endpoint, blob);
            if (sent) {
                sentCount++;
            } else {
                console.warn('❌ sendBeacon falló para', objectName);
            }
        } else {
            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: data,
                keepalive: true
            }).catch(err => console.error('Error en fallback fetch:', err));
        }
    }
}

/**
 * Limpia imágenes temporales de forma asíncrona (para limpieza manual).
 * @param {Array} objectNames - Array de object_name_minio a eliminar
 * @param {string} endpoint - Endpoint para la limpieza
 * @returns {Promise<Object>} - { deletedCount, errorCount }
 */
export async function cleanupImagesAsync(objectNames, endpoint) {
    if (!objectNames || objectNames.length === 0) {
        return { deletedCount: 0, errorCount: 0 };
    }

    let deletedCount = 0;
    let errorCount = 0;

    for (const objectName of objectNames) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ object_name_minio: objectName })
            });

            if (response.ok) {
                deletedCount++;
            } else {
                const errorData = await response.json();
                console.error('❌ Error eliminando', objectName, ':', errorData.error);
                errorCount++;
            }
        } catch (error) {
            console.error('❌ Error de red eliminando', objectName, ':', error);
            errorCount++;
        }
    }

    return { deletedCount, errorCount };
}
