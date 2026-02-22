import { validationRules, validateField, validateForm } from './validaciones_form.js'
import { EditImageManager } from './editar_sitio_imagenes.js';
  
  document.addEventListener("DOMContentLoaded", initEditarSitio);


  function initMap() {
    const defaultLat = -34.6037;
    const defaultLng = -58.3816;
    const latInput = document.getElementById("lat");
    const lngInput = document.getElementById("lng");
    let lat = latInput.value;
    let lng = lngInput.value;
    const map = L.map("map").setView([lat, lng], 7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);
    let marker = L.marker([lat, lng], { draggable: true }).addTo(map);
    marker.on("dragend", function (e) {
      const pos = marker.getLatLng();
      latInput.value = pos.lat.toFixed(6);
      lngInput.value = pos.lng.toFixed(6);
    });
    latInput.addEventListener("change", updateMarker);
    lngInput.addEventListener("change", updateMarker);
    function updateMarker() {
      const lat = parseFloat(latInput.value) || defaultLat;
      const lng = parseFloat(lngInput.value) || defaultLng;
      marker.setLatLng([lat, lng]);
      map.setView([lat, lng]);
    }
    map.on("click", function(e) {
      const lat = e.latlng.lat.toFixed(6);
      const lng = e.latlng.lng.toFixed(6);
      latInput.value = lat;
      lngInput.value = lng;
      marker.setLatLng(e.latlng);
      map.setView(e.latlng);
    });
  }


async function loadTags() {
  try {
    const resp = await fetch("/sitios/tags");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    const raw = Array.isArray(data) ? data : (data && Array.isArray(data.tags) ? data.tags : []);

    return raw.map(item => {
      if (typeof item === "string") {
        return item;
      }
      if (item && typeof item === "object") {
        
        return (item.nombre ?? item.name ?? item.descripcion ?? "").toString();
      }
      return String(item);
    }).filter(Boolean); 
  } catch (err) {
    console.error("Error cargando tags:", err);
    return [];
  }
}


async function tagsLogic() {
  const tagsContainer = document.getElementById('tags-container');
  const tagsHidden = document.querySelector('#tags');
  const selectContainer = document.getElementById('tags-select-container');
  const agregarBtn = document.getElementById('agregar-tag');

  if (!tagsContainer || !tagsHidden || !selectContainer || !agregarBtn) {
    console.error("Faltan elementos del DOM para la lógica de tags.");
    return;
  }

  const tagSelect = document.createElement('select');
  tagSelect.id = 'tag-select';
  tagSelect.className = 'border rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-primary transition-all';
  tagSelect.innerHTML = '<option value="">Selecciona un tag</option>';
  selectContainer.appendChild(tagSelect);

  let selectedTags = [];

  const backendTagNames = await loadTags();
  backendTagNames.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    tagSelect.appendChild(opt);
  });

  try {
    if (tagsHidden.value) {
      selectedTags = JSON.parse(tagsHidden.value);
    }
  } catch (e) {
    console.error("Error al parsear los tags iniciales:", e);
    selectedTags = [];
  }

  function renderTags() {
    tagsContainer.innerHTML = '';
    selectedTags.forEach((nombre, idx) => {
      const tagEl = document.createElement('div');
      tagEl.className = 'flex items-center bg-[#1C453A] text-white px-2 py-1 rounded-full text-sm mr-2 mb-2';
      tagEl.innerHTML = `
        <span>${nombre}</span>
        <button type="button" class="remove-tag ml-2 text-white hover:text-gray-200" data-idx="${idx}">&times;</button>
      `;
      tagsContainer.appendChild(tagEl);
    });
    tagsHidden.value = JSON.stringify(selectedTags);
  }

  renderTags();


  function addTagFromSelect() {
    const nombre = tagSelect.value;
    if (nombre && !selectedTags.includes(nombre)) {
      selectedTags.push(nombre);
      renderTags();
    }
    tagSelect.value = ''; 
  }
  agregarBtn.addEventListener('click', (e) => {
    e.preventDefault();
    addTagFromSelect();
  });

  tagsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-tag')) {
      const i = parseInt(e.target.getAttribute('data-idx'), 10);
      if (!isNaN(i)) {
        selectedTags.splice(i, 1);
        renderTags();
      }
    }
  });
}

function setupSubmitButton(imageManager) {
    const guardarBtn = document.getElementById('guardar-btn');
    const confirmModal = document.getElementById('confirmModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const confirmBtn = document.getElementById('confirmBtn');
    const form = document.getElementById('editForm'); 

    if (!guardarBtn || !confirmModal || !cancelBtn || !confirmBtn || !form) {
        console.error("Faltan elementos del DOM para el modal de confirmación.");
        return;
    }

    guardarBtn.addEventListener('click', function() {
        if (validateForm()) {
            confirmModal.classList.remove('hidden');
        } else {
            const firstError = document.querySelector('.border-red-500');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    cancelBtn.addEventListener('click', () => confirmModal.classList.add('hidden'));
    
    confirmBtn.addEventListener('click', () => {
        imageManager._syncHiddenInput();
        
        imageManager.estáGuardando = true;
        
        form.submit();
    });
}


  async function initEditarSitio() {
    
    initMap();
    await tagsLogic();
    
    const siteId = document.getElementById('siteIdHidden').value;
    const existingImagesJson = document.getElementById('existing-images-json').value;
    
    const imageManager = new EditImageManager(siteId, existingImagesJson);
    
    const cancelarBtn = document.getElementById('cancelar-btn');
    if (cancelarBtn) {
        
        cancelarBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (imageManager.imagenesTemporales.length === 0) {
                window.location.href = '/sitios';
                return;
            }

            const confirmar = confirm(
                '¿Estás seguro de que deseas cancelar?\n\n' +
                `Se eliminarán ${imageManager.imagenesTemporales.length} imagen(es) nueva(s) no guardada(s).`
            );
            
            if (confirmar) {
                cancelarBtn.disabled = true;
                cancelarBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Limpiando...';
                
                const success = await imageManager.limpiarImagenesTemporales();
                
                window.location.href = '/sitios';
            }
        });
    } else {
        console.error('❌ Botón Cancelar NO encontrado');
    }

    window.addEventListener('beforeunload', function(e) {
        if (imageManager.estáGuardando) {
            return; 
        }
        
        if (imageManager.imagenesTemporales.length > 0) {
            imageManager.limpiarConBeacon();
            
            e.preventDefault();
            e.returnValue = 'Hay imágenes nuevas sin guardar que se eliminarán.';
            return 'Hay imágenes nuevas sin guardar que se eliminarán.';
        }
    });
    
    for (const fieldId in validationRules){
      const field = document.getElementById(fieldId);
      if (field) {
        const eventType = (field.tagName === 'SELECT') ? 'change' : 'input';
            field.addEventListener(eventType, () => validateField(fieldId)); 
      }
    }
    setupSubmitButton(imageManager);

    setTimeout(() => {
        const flashSuccess = document.querySelector('.flash-success, .alert-success');
        const successModal = document.getElementById('successModal');
        if (flashSuccess && successModal) {
            successModal.classList.remove('hidden');
            const closeBtn = document.getElementById('closeSuccessBtn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => successModal.classList.add('hidden'));
            }
        }
    }, 300);
}

