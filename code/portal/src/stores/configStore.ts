import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfigStore = defineStore('config', () => {
  const maintenanceMode = ref(false)
  const maintenanceMessage = ref('')
  const reviewsEnabled = ref(true)
  const isLoaded = ref(false)

    async function fetchConfig(force = false) {
    
    if (isLoaded.value && !force) {
        return
    }

    try {
      const BASE_URL = import.meta.env.VITE_API_LOCAL
      const res = await fetch(`${BASE_URL}/config/`)
      
      if (res.ok) {
        const data = await res.json()
        maintenanceMode.value = data.maintenance_mode
        maintenanceMessage.value = data.maintenance_message
        reviewsEnabled.value = data.reviews_enabled !== false 
        isLoaded.value = true
      }
    } catch (error) {
      console.error("Error cargando configuración de flags:", error)
    }
  }

  return { maintenanceMode, maintenanceMessage, reviewsEnabled, isLoaded, fetchConfig }
})