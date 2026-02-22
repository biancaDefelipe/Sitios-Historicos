import { validationRules, validateField, validateForm } from './validaciones_form.js';
import { CreateImageManager } from './crear_sitio_imagenes.js';

document.addEventListener("DOMContentLoaded", initCrearSitio);



  function setFechaRegistro() {
    const fechaInput = document.getElementById("fecha_registro");
    const hoy = new Date();
    const yyyy = hoy.getFullYear();
    const mm = String(hoy.getMonth() + 1).padStart(2, '0');
    const dd = String(hoy.getDate()).padStart(2, '0');
    fechaInput.value = `${yyyy}-${mm}-${dd}`;
  }


  function initMap() {
    const defaultLat = -34.6037;
    const defaultLng = -58.3816;
    const latInput = document.getElementById("lat");
    const lngInput = document.getElementById("lng");
    let lat = defaultLat;
    let lng = defaultLng;
    const map = L.map("map").setView([lat, lng], 13);
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
  
  const tagsHidden = document.getElementById('#tags');
  const selectContainer = document.getElementById('tags-select-container');
  const agregarBtn = document.getElementById('agregar-tag');

  if (!tagsContainer) {
    console.error("No se encontró #tags-container en el DOM.");
    return { selectedTags: [], renderTags: () => {} };
  }
  if (!selectContainer) {
    console.error("No se encontró #tags-select-container en el DOM.");
    return { selectedTags: [], renderTags: () => {} };
  }

  const tagSelect = document.createElement('select');
  tagSelect.id = 'tag-select';
  tagSelect.className = 'border rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-primary transition-all';
  tagSelect.innerHTML = '<option value="">Selecciona un tag</option>';
  selectContainer.appendChild(tagSelect);

  const selectedTags = []; 

  const backendTagNames = await loadTags();
  backendTagNames.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    tagSelect.appendChild(opt);
  });

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
    if (tagsHidden) tagsHidden.value = JSON.stringify(selectedTags);
  }

    function addTagFromSelect() {
      const nombre = tagSelect.value;
      if (!nombre) return;
      if (selectedTags.includes(nombre)) {
        tagSelect.value = '';
        return;
      }
      selectedTags.push(nombre);
      renderTags();
      tagSelect.value = '';
    }


  function removeTag(idx) {
    if (idx < 0 || idx >= selectedTags.length) return;
    selectedTags.splice(idx, 1);
    renderTags();
  }

  if (agregarBtn) {
    agregarBtn.addEventListener('click', function(e) {
      e.preventDefault();
      addTagFromSelect();
    });
  } else {
    tagSelect.addEventListener('change', addTagFromSelect);
  }

  tagsContainer.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-tag')) {
      const i = parseInt(e.target.getAttribute('data-idx'), 10);
      if (!Number.isNaN(i)) removeTag(i);
    }
  });

  return { selectedTags, renderTags };
}


  function setupSubmitButton(imageManager) {
    const guardarBtn = document.getElementById('guardar-btn');
    const confirmModal = document.getElementById('confirmModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const confirmBtn = document.getElementById('confirmBtn');
    const form = document.getElementById('createForm');

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

  async function initCrearSitio() {
    setFechaRegistro();
    initMap();
    await tagsLogic();
    
    const imageManager = new CreateImageManager();
    
    const cancelarBtn = document.getElementById('cancelar-btn');
    if (cancelarBtn) {
        
        
        cancelarBtn.addEventListener('click', async function(e) {
            e.preventDefault(); 
            
            
            
            if (imageManager.images.length === 0) {
                
                window.location.href = '/sitios';
                return;
            }

            const confirmar = confirm(
                '¿Estás seguro de que deseas cancelar?\n\n' +
                `Se eliminarán ${imageManager.images.length} imagen(es).`
            );
            
            
            
            if (confirmar) {
                cancelarBtn.disabled = true;
                cancelarBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Limpiando...';
                
                const success = await imageManager.limpiarTodasLasImagenesTemporales();
                
                
                if (success) {
                    window.location.href = '/sitios';
                } else {
                    alert('Hubo algunos problemas al limpiar las imágenes. Redirigiendo de todas formas...');
                    console.warn('⚠️ Limpieza con errores, redirigiendo igual');
                    window.location.href = '/sitios';
                }
            }
        });
    }

    window.addEventListener('beforeunload', function(e) {
        if (imageManager.estáGuardando) {
            return;
        }
        
        if (imageManager.images.length > 0) {
            imageManager.limpiarConBeacon();
            
            e.preventDefault();
            e.returnValue = 'Hay imágenes sin guardar que se eliminarán.';
            return 'Hay imágenes sin guardar que se eliminarán.';
        }
    });
    
    for (const fieldId in validationRules) {
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
        closeBtn.addEventListener('click', function() {
          successModal.classList.add('hidden');
        });
      }
    }
  }, 300);}




