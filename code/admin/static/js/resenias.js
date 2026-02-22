document.addEventListener("DOMContentLoaded", async () => {
  await cargarFiltrosSelectores();
  await cargarResenias(1);
});

document.getElementById("applyFiltersBtn")?.addEventListener("click", async (e) => {
  if (!validarFechas() | !validarCalificaciones()) return;
  await cargarResenias(1);
});

async function cargarFiltrosSelectores() {
  try {
    const [sitiosResponse, estadosResponse] = await Promise.all([
      fetch("/sitios/nombre_localidad"), 
      fetch("/resenias/estados_resenias") 
    ]);

    const [sitios, estadosResenias] = await Promise.all([
      sitiosResponse.json(), 
      estadosResponse.json() 
    ]);


    const sitiosSelect = document.getElementById("sitioFilter");
    sitios.forEach(sitio => {
      const option = document.createElement("option");
      option.value = sitio.id_sitio;
      option.textContent = sitio.nombre + " (" + sitio.ciudad + ", " + sitio.provincia + ")";
     
      sitiosSelect.appendChild(option);
    });


    const estadosSelect = document.getElementById("estadoFilter");
    estadosResenias.forEach(estado => {
      const option = document.createElement("option");
      option.value = estado.id_estado_resenia;
      option.textContent = estado.descripcion;
      estadosSelect.appendChild(option);
    });

  } catch (e) {
    console.error("Error cargando selectores de filtros:", e);
  }
}


function escapeHtml(str){
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function btnHtml({ label, classes = "", onClick = "", title = "" }) {
  
  const t = escapeHtml(title);
  return `<button title="${t}" class="${classes}" onclick="${onClick}">${escapeHtml(label)}</button>`;
}

function actionButtonsHtml(resenia) {

  const estado = (resenia.descripcion_estado || "").toUpperCase();


  const btnVer = btnHtml({
    label: "Ver",
    classes: "px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700 hover:bg-gray-200",
    onClick: `verResenia(${encodeURIComponent(resenia.id_resenia)})`,
    title: "Ver detalle"
  });


  const showAprobar = (estado === "PENDIENTE");
  const showRechazar = (estado === "PENDIENTE");
  const showEliminar = (estado !== "ELIMINADA");

  const btnAprobar = showAprobar ? btnHtml({
    label: "Aprobar",
    classes: "px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-700 hover:bg-green-200",
    onClick: `aprobarResenia(${encodeURIComponent(resenia.id_resenia)})`,
    title: "Aprobar reseña"
  }) : "";

  const btnRechazar = showRechazar ? btnHtml({
    label: "Rechazar",
    classes: "px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-700 hover:bg-blue-200",
    onClick: `rechazarResenia(${encodeURIComponent(resenia.id_resenia)})`,
    title: "Rechazar reseña"
  }) : "";

  const btnEliminar = showEliminar ? btnHtml({
    label: "Eliminar",
    classes: "px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-700 hover:bg-red-200",
    onClick: `eliminarResenia(${encodeURIComponent(resenia.id_resenia)})`,
    title: "Eliminar reseña"
  }): ""; 

  return `<div class="flex flex-wrap gap-2">
            ${btnVer}
            ${btnAprobar}
            ${btnRechazar}
            ${btnEliminar}
          </div>`;
}



async function cargarResenias(nroPagina = 1) {

  try {
    const filtros = obtenerFiltros();
    const orden = document.getElementById("ordenSelect")?.value || "fecha_desc";

    const response = await fetch(`/resenias/listar?nro_pagina=${nroPagina}&orden=${orden}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filtros }),
      credentials: "same-origin"
    });

    const data = await response.json();

    const tbody = document.getElementById("resenias-tbody");
    tbody.innerHTML = "";

    const tablaContainer = document.getElementById("tablaContainer");
    const sinResultadosContainer = document.getElementById("sinResultadosContainer");
    const msjSinResultados = document.getElementById("msjSinResultados");

    const items = data.items || [];

    if (items.length === 0) {
      tablaContainer.classList.add("hidden");
      sinResultadosContainer.classList.remove("hidden");
      msjSinResultados.textContent = "No hay reseñas para mostrar.";
      return;
    } else {
      tablaContainer.classList.remove("hidden");
      sinResultadosContainer.classList.add("hidden");
      msjSinResultados.textContent = "";
    }

    items.forEach(resenia => {
      const tr = document.createElement("tr");
      tr.classList.add("hover:bg-gray-50");


      const estadoUpper = (resenia.descripcion_estado || "").toUpperCase();
      const estadoColor= getEstiloEstado(resenia.id_estado_resenia)

      const email = escapeHtml(resenia.email_usuario || "");
      const sitio = escapeHtml(resenia.nombre_sitio_historico || "");
     
      const fecha = escapeHtml(resenia.fecha_hora_alta || "");
      const calificacion = Number(resenia.calificacion) || "";
      const calText = escapeHtml(calificacionATexto(calificacion));
      let ciudad = resenia.sitio_ciudad
      let provincia = resenia.sitio_provincia
      tr.innerHTML = `
        <td class="px-4 py-3">${email}</td>
        <td class="px-4 py-3">${sitio}
          <p class="text-gray-600">${ciudad}, ${provincia}</p> 
        </td>
        <td class="px-4 py-3">${calificacion} (${calText})</td>
        <td class="px-4 py-3">${fecha}</td>
        <td class="px-4 py-3">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${estadoColor}">
            ${escapeHtml(estadoUpper)}
          </span>
        </td>
        <td class="px-4 py-3">
          ${actionButtonsHtml(resenia)}
        </td>
      `;
 
      tbody.appendChild(tr);
    });
    
    renderPagination(data.pageable);
  } catch (e) {
    console.error("Ocurrió un error inesperado al intentar cargar reseñas: ", e);
  }
}


function obtenerFiltros(){
    return {
        calificacion_min: document.getElementById("calificacionMinFilter")?.value || "",
        calificacion_max: document.getElementById("calificacionMaxFilter")?.value || "",
        fecha_desde: document.getElementById("fechaDesdeFilter")?.value || "",
        fecha_hasta: document.getElementById("fechaHastaFilter")?.value || "",
        usuario: document.getElementById("usuarioFilter")?.value.trim() || "",
        sitio: document.getElementById("sitioFilter")?.value || "",
        estado: document.getElementById("estadoFilter")?.value || ""
    };
}

document.getElementById("clearFiltersBtn").addEventListener("click", limpiarFiltros);
function limpiarFiltros() {
 
    document.getElementById("calificacionMinFilter").value = "";
    document.getElementById("calificacionMaxFilter").value = "";
    document.getElementById("fechaDesdeFilter").value = "";
    document.getElementById("fechaHastaFilter").value = "";
    document.getElementById("usuarioFilter").value = "";
    document.getElementById("sitioFilter").value = "";
    document.getElementById("estadoFilter").value = "";
    document.getElementById("ordenSelect").value = "fecha_desc";


    const fechaError = document.getElementById("fechaError");
    const calificacionError = document.getElementById("calificacionError");
    const fechaDesdeInput = document.getElementById("fechaDesdeFilter");
    const fechaHastaInput = document.getElementById("fechaHastaFilter");
    const calificacionMinInput = document.getElementById("calificacionMinFilter");
    const calificacionMaxInput = document.getElementById("calificacionMaxFilter");

    const tablaContainer = document.getElementById("tablaContainer");
    const sinResultadosContainer = document.getElementById("sinResultadosContainer");
    const msjSinResultados = document.getElementById("msjSinResultados");
    
    fechaError.classList.add("hidden");
    calificacionError.classList.add("hidden");
    fechaError.textContent = "";
    calificacionError.textContent = "";
    fechaDesdeInput.classList.remove("input-error");
    fechaHastaInput.classList.remove("input-error");
    calificacionMinInput.classList.remove("input-error");
    calificacionMaxInput.classList.remove("input-error");

    tablaContainer.classList.remove("hidden");
    sinResultadosContainer.classList.add("hidden");
    msjSinResultados.textContent = "";

 
    cargarResenias(1);
}

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

function validarCalificaciones() {
    const calificacionMinInput = document.getElementById("calificacionMinFilter");
    const calificacionMaxInput = document.getElementById("calificacionMaxFilter");
    const calificacionError = document.getElementById("calificacionError");


    calificacionMinInput.classList.remove("input-error");
    calificacionMaxInput.classList.remove("input-error");
    calificacionError.classList.add("hidden");
    calificacionError.textContent = "";

    const min = calificacionMinInput.value;
    const max = calificacionMaxInput.value;

    if (min && max) {
        if (min > max) {
            calificacionMinInput.classList.add("input-error");
            calificacionMaxInput.classList.add("input-error");
            
            calificacionError.textContent = "La Calificacion Mín. no puede ser mayor que la Calificacion Máx.";
            calificacionError.classList.remove("hidden");
            return false;
        }
    }
    return true;
}

function renderPagination(pageable) {
  const pagDiv = document.getElementById("pagination");
  pagDiv.innerHTML = `
    <ul class="flex justify-between">
      <li>${pageable.has_prev ? `<a href="#" onclick="cargarResenias(${pageable.page - 1})">Anterior</a>` : `<span class="text-gray-400">Anterior</span>`}</li>
      <li>Página ${pageable.page} de ${pageable.pages} — ${pageable.total} reseñas</li>
      <li>${pageable.has_next ? `<a href="#" onclick="cargarResenias(${pageable.page + 1})">Siguiente</a>` : `<span class="text-gray-400">Siguiente</span>`}</li>
    </ul>
  `;
}

function calificacionATexto(valor) {
  const calificacion_map = {
    1: "Uno",
    2: "Dos",
    3: "Tres",
    4: "Cuatro",
    5: "Cinco"
  };
  return calificacion_map[valor] || "";
}
function getEstiloEstado(estado) {
  const estado_map = {
    1: "bg-yellow-100 text-yellow-800",
    2: "bg-green-100 text-green-800",
    3: "bg-blue-100 text-blue-800",
    4: "bg-red-100 text-red-800"
  };
  return estado_map[estado] || "";
}



const ConfirmActionModal = (function () {

  const modal = document.getElementById("confirmActionModal");
  const titleEl = document.getElementById("confirmModalTitle");
  const msgEl = document.getElementById("confirmModalMessage");
  const reasonContainer = document.getElementById("confirmModalReasonContainer");
  const reasonInput = document.getElementById("confirmReason");
  const reasonError = document.getElementById("confirmReasonError");
  const btnCancel = document.getElementById("confirmModalCancel");
  const btnClose = document.getElementById("confirmModalClose");
  const btnConfirm = document.getElementById("confirmModalConfirm");

  let currentConfig = null; 

  function open(config) {
    
    currentConfig = Object.assign({
      method: "POST",
      requireReason: false,
      actionLabel: "Confirmar",
      message: "¿Está seguro que desea realizar esta acción?",
      bodyFactory: () => ({}),
      onSuccess: () => {}
    }, config);

    titleEl.textContent = currentConfig.actionLabel;
    msgEl.textContent = currentConfig.message;

    if (currentConfig.requireReason) {
      reasonContainer.classList.remove("hidden");
      reasonInput.value = "";
      reasonError.classList.add("hidden");
    } else {
      reasonContainer.classList.add("hidden");
      reasonError.classList.add("hidden");
    }

  
    btnConfirm.textContent = currentConfig.actionLabel;

   
    btnConfirm.disabled = false;
    btnCancel.disabled = false;

    modal.classList.remove("hidden");

    if (currentConfig.requireReason) {
      reasonInput.focus();
    } else {
      btnConfirm.focus();
    }

    document.addEventListener("keydown", onKeyDown);
  }

  function close() {
    modal.classList.add("hidden");
    currentConfig = null;
    reasonInput.value = "";
    reasonError.classList.add("hidden");
    document.removeEventListener("keydown", onKeyDown);
  }

  function onKeyDown(e) {
    if (e.key === "Escape") close();
  }

  function showReasonValidation(message) {
    reasonError.textContent = message;
    reasonError.classList.remove("hidden");
    reasonInput.classList.add("input-error");
  }

async function onConfirmClicked() {
  if (!currentConfig) return;

  let reason = null;
  if (currentConfig.requireReason) {
    reason = reasonInput.value?.trim() || "";
    if (!reason) {
      showReasonValidation("El motivo es obligatorio.");
      return;
    }
    if (reason.length > 200) {
      showReasonValidation("El motivo no puede superar los 200 caracteres.");
      return;
    }
    reasonError.classList.add("hidden");
    reasonInput.classList.remove("input-error");
  }


  btnConfirm.disabled = true;
  btnCancel.disabled = true;

  try {
    const url = currentConfig.url;
    const method = currentConfig.method.toUpperCase();
    const bodyObj = currentConfig.bodyFactory(reason);

    const fetchOptions = {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: 'same-origin' 
    };

    if (method !== "GET" && method !== "HEAD") {
      fetchOptions.body = JSON.stringify(bodyObj);
    }

    const resp = await fetch(url, fetchOptions);


    if (!resp.ok) {
      try { await resp.json(); } catch (e) { /* ignore */ }
    }

  
    location.reload();

  } catch (err) {
    console.error("Error en acción confirmada:", err);
 
    showToast("Ocurrió un error de red. Intente nuevamente.", "error");
    btnConfirm.disabled = false;
    btnCancel.disabled = false;
  }
}


 
  btnCancel.addEventListener("click", close);
  btnClose.addEventListener("click", close);
  btnConfirm.addEventListener("click", onConfirmClicked);

  return { open, close };
})();

function showToast(message, category = "success", timeout = 4000) {
  const container = document.getElementById("flash-messages") || (function create(){ 
    const c = document.createElement("div"); c.id = "flash-messages"; c.className = "mb-4 space-y-2"; 
    document.querySelector("body > div")?.prepend(c); return c; 
  })();

  const div = document.createElement("div");
  div.className = `p-4 rounded ${category === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`;
  div.textContent = message;
  container.appendChild(div);

  setTimeout(() => {
    div.remove();
  }, timeout);
}

function openConfirmAction(options) {
  const defaultBodyFactory = (reason) => {
    if (options.requireReason) return { motivo: reason };
    return {};
  };

  const cfg = Object.assign({
    method: "POST",
    requireReason: false,
    bodyFactory: defaultBodyFactory,
    onSuccess: async () => { await cargarResenias(1); } // refresca la lista por defecto
  }, options);

  ConfirmActionModal.open(cfg);
}



function aprobarResenia(id_resenia) {

  openConfirmAction({
    id: id_resenia,
    actionLabel: "Aprobar",
    message: "¿Está seguro que desea aprobar esta reseña? Esta acción no se podrá deshacer.",
    url: `/resenias/aprobar?id_resenia=${encodeURIComponent(id_resenia)}`,
    method: "PUT",
    requireReason: false,
    bodyFactory: () => ({}),
    onSuccess: async () => { await cargarResenias(1); }
  });
}

function eliminarResenia(id_resenia) {
  openConfirmAction({
    id: id_resenia,
    actionLabel: "Eliminar",
    message: "¿Está seguro que desea eliminar esta reseña? Esta acción no se podrá deshacer.",
    url: `/resenias/eliminar?id_resenia=${encodeURIComponent(id_resenia)}`,
    method: "PUT",
    requireReason: false,
    bodyFactory: () => ({}),
    onSuccess: async () => { await cargarResenias(1); }
  });
}

function rechazarResenia(id_resenia) {
  openConfirmAction({
    id: id_resenia,
    actionLabel: "Rechazar",
    message: "¿Está seguro que desea rechazar esta reseña? Indique el motivo en el recuadro.",
    url: `/resenias/rechazar?id_resenia=${encodeURIComponent(id_resenia)}`,
    method: "PUT",
    requireReason: true,
    bodyFactory: (reason) => ({ motivo: reason }),
    onSuccess: async () => { await cargarResenias(1); }
  });
}


async function verResenia(id_resenia) {
  try {
    const resp = await fetch(`/resenias/get?id_resenia=${encodeURIComponent(id_resenia)}`, {
      method: "GET",
      credentials: "same-origin", 
      headers: { "Accept": "application/json" }
    });

    if (!resp.ok) {
      console.error("Error obteniendo reseña:", resp.status);
      showToast("No se pudo obtener la reseña.", "error");
      return;
    }

    const data = await resp.json();

    document.getElementById("view_site_name").textContent = data.nombre_sitio_historico + " ("+ data.sitio_ciudad + ", " + data.sitio_provincia + ")"  || "-";
    document.getElementById("view_user_email").textContent = data.email_usuario || "-";
    document.getElementById("view_rating").textContent = `${data.calificacion} (${calificacionATexto(data.calificacion)})`;
    document.getElementById("view_content").textContent = data.contenido || "";
    document.getElementById("view_date").textContent = data.fecha_hora_alta || "";
    
    
    const estadoContainer = document.getElementById("view_state_badge");
    estadoContainer.innerHTML = ""; // limpiar
    const span = document.createElement("span");

    span.className = getEstiloEstado(data.id_estado_resenia)
    span.textContent = (data.descripcion_estado || "").toUpperCase();
    estadoContainer.appendChild(span);

   
    const motivoContainer = document.getElementById("view_motivo_container");
    const motivoText = document.getElementById("view_motivo_text");
    if (data.id_estado_resenia && data.id_estado_resenia === 3) {
      motivoContainer.classList.remove("hidden");
      motivoText.textContent = data.motivo_rechazo || "-";
    } else {
      motivoContainer.classList.add("hidden");
      motivoText.textContent = "";
    }

    openViewModal();

  } catch (err) {
    console.error("Error en verResenia:", err);
    showToast("Ocurrió un error al obtener la reseña.", "error");
  }
}

function openViewModal() {
  const modal = document.getElementById("viewReseniaModal");
  modal.classList.remove("hidden");

  document.getElementById("viewModalClose")?.addEventListener("click", closeViewModal);
  document.getElementById("viewModalCloseBtn")?.addEventListener("click", closeViewModal);
  document.addEventListener("keydown", viewOnKeyDown);
}

function closeViewModal() {
  const modal = document.getElementById("viewReseniaModal");
  modal.classList.add("hidden");

  document.getElementById("viewModalClose")?.removeEventListener("click", closeViewModal);
  document.getElementById("viewModalCloseBtn")?.removeEventListener("click", closeViewModal);
  document.removeEventListener("keydown", viewOnKeyDown);
}

function viewOnKeyDown(e) {
  if (e.key === "Escape") closeViewModal();
}