/**
 * Muestra un mensaje de error para un campo específico.
 * @param {string} fieldName - El nombre base del campo (ej: "nombre").
 * @param {string} message - El mensaje de error a mostrar.
 */
export function showError(fieldName, message) {
    const errorElement = document.getElementById(`${fieldName}Error`);
    const inputElement = document.getElementById(fieldName);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }
    if (inputElement) inputElement.classList.add('border-red-500');
}

/**
 * Oculta el mensaje de error para un campo específico.
 * @param {string} fieldName - El nombre base del campo (ej: "nombre").
 */
export function hideError(fieldName) {
    const errorElement = document.getElementById(`${fieldName}Error`);
    const inputElement = document.getElementById(fieldName);
    if (errorElement) errorElement.classList.add('hidden');
    if (inputElement) inputElement.classList.remove('border-red-500');
}

export const validationRules = {
    'nombre': [
      { validate: (value) => value.trim() !== '', message: 'El nombre es obligatorio.' },
      { validate: (value) => value.length <= 100, message: 'El nombre no puede exceder los 100 caracteres.' },
      { validate: (value) => /^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚüÜ\s'.,-]+$/.test(value), message: 'El nombre contiene caracteres no válidos.' }
    ],
    'descripcion_breve': [
      { validate: (value) => value.trim() !== '', message: 'La descripción breve es obligatoria.' },
      { validate: (value) => value.length <= 100, message: 'La descripción breve no puede exceder los 100 caracteres.' }
    ],
    'descripcion_detallada': [
        { validate: (value) => value.trim() !== '', message: 'La descripción detallada es obligatoria.' }
    ],
    'ciudad': [
        { validate: (value) => value.trim() !== '', message: 'La ciudad es obligatoria.' },
        { validate: (value) => /^[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ\s'-]+$/.test(value), message: 'La ciudad contiene caracteres no válidos.' }
    ],
    'provincia': [
        { validate: (value) => value !== '', message: 'Debe seleccionar una provincia.' }
    ],
    'estado': [
        { validate: (value) => value !== '', message: 'Debe seleccionar un estado.' }
    ],
    'categoria-select': [
        { validate: (value) => value !== '', message: 'Debe seleccionar una categoría.' }
    ],
    'anio_inauguracion': [
        { validate: (value) => value.trim() !== '', message: 'El año es obligatorio.' },
        { 
            validate: (value) => {
                const year = parseInt(value, 10);
                const currentYear = new Date().getFullYear();
                return !isNaN(year) && year >= 1000 && year <= currentYear;
            },
            message: `El año debe estar entre 1000 y ${new Date().getFullYear()}.`
        }
    ],
    'lat': [
      { validate: (value) => value.trim() !== '', message: 'La latitud es obligatoria.' },
      { validate: (value) => !isNaN(parseFloat(value)) && parseFloat(value) >= -90 && parseFloat(value) <= 90, message: 'Latitud inválida (debe ser entre -90 y 90).' }
    ],
    'lng': [
      { validate: (value) => value.trim() !== '', message: 'La longitud es obligatoria.' },
      { validate: (value) => !isNaN(parseFloat(value)) && parseFloat(value) >= -180 && parseFloat(value) <= 180, message: 'Longitud inválida (debe ser entre -180 y 180).' }
    ]
};

/**
 * Valida un campo individual según las reglas definidas.
 * @param {string} fieldId - El ID del campo a validar.
 * @returns {boolean} - True si es válido, False si no.
 */
export function validateField(fieldId) {
    const field = document.getElementById(fieldId);
    const rules = validationRules[fieldId];
    if (!field || !rules) return true;

    const errorFieldId = (fieldId === 'categoria-select') ? 'categoria' : fieldId;

    for (const rule of rules) {
        if (!rule.validate(field.value)) {
            showError(errorFieldId, rule.message);
            return false;
        }
    }
    hideError(errorFieldId);
    return true;
}

/**
 * Valida todos los campos del formulario.
 * @returns {boolean} - True si todo el formulario es válido, False si no.
 */
export function validateForm() {
    let isFormValid = true;
    for (const fieldId in validationRules) {
        if (!validateField(fieldId)) {
            isFormValid = false;
        }
    }
    return isFormValid;
}