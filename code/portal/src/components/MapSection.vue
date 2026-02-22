<template>
  <div class="map-wrapper">
    <div class="map-container" ref="mapEl"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const props = defineProps<{ 
  lat: number | null; 
  long: number | null; 
  tooltipText?: string; 
  tooltipDesc?: string 
}>()

const mapEl = ref<HTMLElement | null>(null)

let map: L.Map | null = null
let marker: L.Marker | null = null

function initializeMap() {
  if (!mapEl.value) return
  
  const defaultLat = -34.6037
  const defaultLong = -58.3816
  const zoom = 13
  
  const initialLat = props.lat && typeof props.lat === 'number' ? props.lat : defaultLat
  const initialLong = props.long && typeof props.long === 'number' ? props.long : defaultLong
  map = L.map(mapEl.value, { 
    scrollWheelZoom: true
  }).setView([initialLat, initialLong], zoom)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, 
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)
  
  if (props.lat && props.long && typeof props.lat === 'number' && typeof props.long === 'number') {
    createMarker(props.lat, props.long)
  }
}

function createMarker(lat: number, long: number) {
  if (!map) return
  
  if (marker) {
    map.removeLayer(marker)
    marker = null
  }
  
  marker = L.marker([lat, long]).addTo(map)
  
  if (props.tooltipText || props.tooltipDesc) {
    const popupContent = `<strong>${props.tooltipText || ''}</strong>${props.tooltipDesc ? `<br/>${props.tooltipDesc}` : ''}`
    marker.bindPopup(popupContent)
  }
}

function updateMap(lat: number | null | undefined, long: number | null | undefined) {
  if (!map) return

  const hasValidCoords =
    lat !== null &&
    long !== null &&
    lat !== undefined &&
    long !== undefined &&
    typeof lat === "number" &&
    typeof long === "number"

  if (hasValidCoords) {
    map.setView([lat, long], 13)
    createMarker(lat, long)
  } else {
    if (marker) {
      map.removeLayer(marker)
      marker = null
    }
  }
}


onMounted(() => {
  initializeMap()
})

watch(
  () => [props.lat, props.long],
  async ([lat, lon]) => {
    await nextTick()
    updateMap(lat, lon)
  }
)
</script>

<style scoped>
.map-wrapper {
  margin-top: 16px;
}

.map-container {
  width: 100%;
  height: 280px;
  border-radius: 10px;
  border: 1px solid #ddd;
  overflow: hidden;
}
</style>