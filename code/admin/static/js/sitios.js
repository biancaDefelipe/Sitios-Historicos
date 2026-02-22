
document.addEventListener("DOMContentLoaded", async () => {
  await loadFilters();
  await loadSitios(1);
});

document.getElementById("searchForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validarFechas()) return;
  await loadSitios(1);
});

document.getElementById("applyFiltersBtn")?.addEventListener("click", async (e) => {
  if (!validarFechas()) return;
  await loadSitios(1);
});

document.getElementById("exportarCsv")?.addEventListener("click", async (e) => {
  e.preventDefault();
  if (!validarFechas()) return;
  await exportarSitios(e);
});

async function loadFilters() {
  try {
    const [catsResp, estadosResp, provsResp, tagsResp] = await Promise.all([
      fetch("/sitios/categorias"),
      fetch("/sitios/estados"),
      fetch("/sitios/provincias"),
      fetch("/sitios/tags"),
    ]);

    const [categorias, estados, provincias, tags] = await Promise.all([
      catsResp.json(),
      estadosResp.json(),
      provsResp.json(),
      tagsResp.json()
    ]);

  
    const categoriaSelect = document.getElementById("categoriaFilter");
    categorias.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id_categoria;  
      opt.textContent = c.descripcion;
      categoriaSelect.appendChild(opt);
    });

 
    const estadoSelect = document.getElementById("estadoFilter");
    estados.forEach(e => {
      const opt = document.createElement("option");
      opt.value = e.id_estado_cons;  
      opt.textContent = e.descripcion;
      estadoSelect.appendChild(opt);
    });


    const provinciaSelect = document.getElementById("provinciaFilter");
    provincias.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.id_provincia;  
      opt.textContent = p.nombre;
      provinciaSelect.appendChild(opt);
    });

    const tagSelect = document.getElementById("tagFilter");
    tags.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t.id_tag;  
      opt.textContent = t.nombre;
      tagSelect.appendChild(opt);
    });

  } catch (err) {
    console.error("Error cargando filtros:", err);
  }
}

document.getElementById("clearFiltersBtn").addEventListener("click", limpiarFiltros);
function limpiarFiltros() {

  document.getElementById("ciudadFilter").value = "";
  document.getElementById("provinciaFilter").value = "";
  document.getElementById("categoriaFilter").value = "";
  document.getElementById("estadoFilter").value = "";
  document.getElementById("visibilidadFilter").value = "";
  document.getElementById("fechaDesdeFilter").value = "";
  document.getElementById("fechaHastaFilter").value = "";
  document.getElementById("orderSelect").value = "fecha_desc";
  document.getElementById("searchInput").value = "";
  document.getElementById("tagFilter").value = "";


  const fechaError = document.getElementById("fechaError");
  const fechaDesdeInput = document.getElementById("fechaDesdeFilter");
  const fechaHastaInput = document.getElementById("fechaHastaFilter");
  const errorDiv = document.getElementById("exportarError");

  fechaError.classList.add("hidden");
  fechaError.textContent = "";
  fechaDesdeInput.classList.remove("input-error");
  fechaHastaInput.classList.remove("input-error");

  errorDiv.classList.add("hidden");
  errorDiv.textContent = "";

  
  loadSitios(1);
}

async function loadSitios(page = 1){
  try {

    const errorDiv = document.getElementById("exportarError");
    errorDiv.classList.add("hidden");
    errorDiv.textContent = "";

    const filtros = {
      categoria: document.getElementById("categoriaFilter")?.value || "",
      estado: document.getElementById("estadoFilter")?.value || "",
      ciudad: document.getElementById("ciudadFilter")?.value.trim() || "",
      provincia: document.getElementById("provinciaFilter")?.value || "",
      visibilidad: document.getElementById("visibilidadFilter")?.value || "",
      fecha_desde: document.getElementById("fechaDesdeFilter")?.value || "",
      fecha_hasta: document.getElementById("fechaHastaFilter")?.value || "",
      busqueda: document.getElementById("searchInput")?.value.trim() || "",
      tags: document.getElementById("tagFilter")?.value ? [document.getElementById("tagFilter")?.value] : []
    };

    const orden = document.getElementById("orderSelect")?.value || "fecha_desc";

    const resp = await fetch(`/sitios/listar?page=${page}&order=${orden}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filtros })
    });

    const data = await resp.json();

    const container = document.getElementById("sitios-container");
    if (!data.items.length) {
      container.innerHTML = `<div class="col-span-4 text-center text-gray-600">No se encontraron sitios históricos.</div>`;
      const pagDiv = document.getElementById("pagination");
      pagDiv.innerHTML ='';
      return;
    }

    container.innerHTML = "";
    data.items.forEach(s => {
      const card = document.createElement('div');
      card.className = "flex";
      let imageHtml = "";
      if (s.url_portada){
        imageHtml = `
        <img src="${s.url_portada}" alt="${s.alt_portada}" class="object-cover h-40 w-full rounded-t-xl"/>
        `;
      } else {
        imageHtml = `
        <div class="bg-[#F5F5F5] flex items-center justify-center h-40 rounded-t-xl">
          <span class="text-[#92A79C]">Sin imagen</span>
        </div>
        `;
      }
      card.innerHTML = `
        <div class="bg-white rounded-xl shadow-lg w-full flex flex-col border border-[#92A79C] transition-transform duration-300 ease-in-out hover:shadow-2xl hover:-translate-y-1">
                  
                  <div class="bg-[#F5F5F5] flex items-center justify-center h-40 rounded-t-xl overflow-hidden">
                    ${imageHtml}
                  </div>
                  
                  <div class="p-4 flex-1 flex flex-col">
                    <h5 class="text-lg font-semibold text-[#0B2F3A] mb-2 truncate" title="${s.nombre}">${s.nombre}</h5>
                    <p class="text-sm text-[#001F3F] mb-1"><i class="fas fa-map-marker-alt mr-1"></i> <span class="font-bold">${s.ciudad}</span>, ${s.provincia}</p>
                    <p class="text-sm text-[#001F3F] mb-1"><i class="fas fa-tag mr-1"></i> ${s.categoria}</p>
                    <p class="text-sm text-[#001F3F] mb-1"><i class="fas fa-clipboard-check mr-1"></i> Estado: ${s.estado}</p>
                    <p class="text-sm text-[#001F3F] mb-1"><i class="fas fa-calendar-alt mr-1"></i> Año: ${s.anio_inauguracion}</p>
                    <p class="text-sm text-[#001F3F] mb-1"><i class="fas fa-eye mr-1"></i> Visible: ${s.visible ? 'Sí' : 'No'}</p>
                    
                    <div class="flex flex-row flex-wrap gap-2 mt-4 pt-4 border-t">
                      <button aria-label="Ver sitio" type="button" class="bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs flex items-center view-btn"><i class="fas fa-eye mr-1"></i>Ver detalles</button>
                      <button aria-label="Eliminar sitio" type="button" class="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs flex items-center delete-btn"><i class="fas fa-trash mr-1"></i>Eliminar</button>
                      <button aria-label="Editar sitio" type="button" class="bg-yellow-600 hover:bg-yellow-700 text-white px-2 py-1 rounded text-xs flex items-center edit-btn"><i class="fas fa-edit mr-1"></i>Editar</button>
                    </div>
                  </div>
                </div>
      `;
     
      card.querySelector('.view-btn').addEventListener('click', () => openViewModal(s));

      card.querySelector('.delete-btn').addEventListener('click', () => openDeleteModal(s.id));
 
      card.querySelector('.edit-btn').addEventListener('click', () => window.location.href = `/sitios/editar/${s.id}`);
      container.appendChild(card);
    });


    renderPagination(data.pagination);
    
  } catch (err) {
    console.error("Error cargando sitios:", err);
  }
}

function renderPagination(pagination) {
  const pagDiv = document.getElementById("pagination");
  pagDiv.innerHTML = `
    <ul class="flex justify-between">
      <li>${pagination.has_prev ? `<a href="#" onclick="loadSitios(${pagination.page - 1})">Anterior</a>` : `<span class="text-gray-400">Anterior</span>`}</li>
      <li>Página ${pagination.page} de ${pagination.pages} — ${pagination.total} sitios </li>
      <li>${pagination.has_next ? `<a href="#" onclick="loadSitios(${pagination.page + 1})">Siguiente</a>` : `<span class="text-gray-400">Siguiente</span>`}</li>
    </ul>
  `;
}

async function exportarSitios(e) {
  e.preventDefault();

  const errorDiv = document.getElementById("exportarError");
  errorDiv.classList.add("hidden");
  errorDiv.textContent = "";

  
  const filtros = {
    categoria: document.getElementById("categoriaFilter")?.value || "",
    estado: document.getElementById("estadoFilter")?.value || "",
    ciudad: document.getElementById("ciudadFilter")?.value.trim() || "",
    provincia: document.getElementById("provinciaFilter")?.value || "",
    visibilidad: document.getElementById("visibilidadFilter")?.value || "",
    fecha_desde: document.getElementById("fechaDesdeFilter")?.value || "",
    fecha_hasta: document.getElementById("fechaHastaFilter")?.value || "",
    busqueda: document.getElementById("searchInput")?.value.trim() || ""
  };

  const orden = document.getElementById("orderSelect")?.value || "fecha_desc";


  generarSpinner("exportarCsv");
  try {
    const resp = await fetch("/sitios/exportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filtros, order: orden })
    });

 
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      const mensaje = err.error || "No se pudieron exportar los sitios.";
      errorDiv.textContent = mensaje;
      errorDiv.classList.remove("hidden");
      return;
    }


    const blob = await resp.blob();

  
    const disposition = resp.headers.get("Content-Disposition");
    let filename = "sitios.csv";
    if (disposition && disposition.includes("filename=")) {
      filename = disposition.split("filename=")[1].replace(/"/g, "");
    }

    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

  }
  catch (err) {
    console.error("Error exportando CSV:", err);
    alert("Error inesperado al generar el CSV.");
  }
  finally {
    quitarSpinner("exportarCsv")
  }
};

function validarFechas() {
    const fechaDesdeInput = document.getElementById("fechaDesdeFilter");
    const fechaHastaInput = document.getElementById("fechaHastaFilter");
    const fechaError = document.getElementById("fechaError");


    fechaDesdeInput.classList.remove("input-error");
    fechaHastaInput.classList.remove("input-error");
    fechaError.classList.add("hidden");
    fechaError.textContent = "";

    const desde = fechaDesdeInput.value;
    const hasta = fechaHastaInput.value;
    if (desde && hasta) {
        if (desde > hasta) {
       
            fechaDesdeInput.classList.add("input-error");
            fechaHastaInput.classList.add("input-error");
            
            fechaError.textContent = "La Fecha Desde no puede ser mayor que la Fecha Hasta";
            fechaError.classList.remove("hidden");
            return false;
        }
    }
    return true;
}


let viewModal = document.getElementById('viewModal');
let viewModalContent = document.getElementById('viewModalContent');
let viewMap;
function openViewModal(sitio) {
  viewModal.classList.remove('hidden');

  const tagsHtml = (sitio.tags && sitio.tags.length > 0)
    ? sitio.tags.join(', ')
    : 'Sin etiquetas';

  const modalTitle = document.getElementById('viewModalTitle');
  if (modalTitle) {
      modalTitle.textContent = `Detalles del sitio: ${sitio.nombre}`;
  } 

  let carouselHtml = '';
  if (sitio.images && sitio.images.length > 0) {
      
      const imagesTrack = sitio.images.map((img, index) => `
          <div class="carousel-slide flex-shrink-0 w-full flex flex-col">
              <!-- Contenedor de imagen con altura fija -->
              <div class="relative w-full bg-gray-100 rounded-lg flex items-center justify-center" style="height: 400px;">
                <img 
                  src="${img.url_publica}" 
                  alt="${img.titulo_alt || 'Imagen del sitio'}" 
                  class="max-w-full max-h-full object-contain rounded-lg shadow-md"
                  loading="${index === 0 ? 'eager' : 'lazy'}"
                />
              </div>
              <!-- Título de la imagen -->
              <p class="text-center text-sm text-gray-700 mt-3 px-2 font-medium">${img.titulo_alt || 'Sin descripción'}</p>
              <!-- Indicador de posición -->
              <p class="text-center text-xs text-gray-500 mt-1">${index + 1} / ${sitio.images.length}</p>
          </div>
      `).join('');

      const arrowsHtml = sitio.images.length > 1 ? `
          <button 
            class="modal-carousel-btn carousel-prev absolute top-1/2 left-2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70 transition-all z-10 shadow-lg"
            aria-label="Imagen anterior"
          >
              <i class="fas fa-chevron-left"></i>
          </button>
          <button 
            class="modal-carousel-btn carousel-next absolute top-1/2 right-2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70 transition-all z-10 shadow-lg"
            aria-label="Imagen siguiente"
          >
              <i class="fas fa-chevron-right"></i>
          </button>
      ` : '';

      carouselHtml = `
          <div class="relative w-full mb-6 rounded-lg overflow-hidden border border-gray-200" data-sitio-id="${sitio.id}">
              <div class="carousel-track flex transition-transform duration-300 ease-in-out">
                  ${imagesTrack}
              </div>
              ${arrowsHtml}
          </div>
      `;
  }  

  viewModalContent.innerHTML = `
    ${carouselHtml} 
    
    <p><span class='font-bold text-[#0B2F3A]'>Ciudad:</span> ${sitio.ciudad}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Provincia:</span> ${sitio.provincia}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Descripción Breve:</span> ${sitio.descripcion_breve}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Descripción Detallada:</span> ${sitio.descripcion_detallada}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Latitud:</span> ${sitio.latitud}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Longitud:</span> ${sitio.longitud}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Estado de conservación:</span> ${sitio.estado}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Año de inauguración:</span> ${sitio.anio_inauguracion}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Categoría:</span> ${sitio.categoria}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Fecha y hora de registro:</span> ${sitio.fecha_hora_alta}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Visible:</span> ${sitio.visible ? 'Sí' : 'No'}</p>
    <p><span class='font-bold text-[#0B2F3A]'>Etiquetas:</span> ${tagsHtml}</p>
  `;
  if (sitio.images && sitio.images.length > 1) {
      setupModalCarousel(viewModal, sitio.images.length); 
  }
  setTimeout(function() {
    const mapDiv = document.getElementById('viewMap');
    if (mapDiv) {
      mapDiv.innerHTML = "";
      mapDiv.style.height = "256px";
      mapDiv.style.minHeight = "256px";
      if (viewMap) {
        viewMap.remove();
        viewMap = null;
      }
      viewMap = L.map('viewMap', {scrollWheelZoom: false});
      viewMap.setView([parseFloat(sitio.latitud) || 0, parseFloat(sitio.longitud) || 0], 14);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors'
      }).addTo(viewMap);
      if (sitio.latitud && sitio.longitud) {
        L.marker([parseFloat(sitio.latitud), parseFloat(sitio.longitud)]).addTo(viewMap);
      }
      setTimeout(() => { viewMap.invalidateSize(); }, 400);
    }
  }, 350);
}
function closeViewModal() {
  viewModal.classList.add('hidden');
  if (viewMap) {
    viewMap.remove();
    viewMap = null;
  }
}

function setupModalCarousel(modalElement, totalImages) {
    const track = modalElement.querySelector('.carousel-track');
    const prevBtn = modalElement.querySelector('.carousel-prev');
    const nextBtn = modalElement.querySelector('.carousel-next');
    
    if (!track || !prevBtn || !nextBtn) return;

    let currentIndex = 0; 

    function updateCarousel() {
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    prevBtn.addEventListener('click', (e) => {
        e.stopPropagation(); 
        currentIndex = (currentIndex > 0) ? currentIndex - 1 : totalImages - 1;
        updateCarousel();
    });

    nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex < totalImages - 1) ? currentIndex + 1 : 0;
        updateCarousel();
    });

    currentIndex = 0;
    updateCarousel();
}


let deleteModal = document.getElementById('deleteModal');
let deleteForm = document.getElementById('deleteForm');
function openDeleteModal(sitioId) {
  if (deleteModal && deleteForm) {
    deleteModal.classList.remove('hidden');
    deleteForm.action = `/sitios/eliminar/${sitioId}`;
  }
}
function closeDeleteModal() {
  if (deleteModal && deleteForm) {
    deleteModal.classList.add('hidden');
    deleteForm.action = "";
  }
}

function generarSpinner(elementId){
  const boton = document.getElementById(elementId);
  boton.classList.add("opacity-70", "cursor-not-allowed");
  boton.style.pointerEvents = "none";
  boton.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>Exportar sitios`;
}

function quitarSpinner(elementId){
  const boton = document.getElementById(elementId);
  boton.classList.remove("opacity-70", "cursor-not-allowed");
  boton.style.pointerEvents = "auto";
  boton.innerHTML = `<i class="fas fa-file-export mr-2"></i>Exportar sitios`;
}