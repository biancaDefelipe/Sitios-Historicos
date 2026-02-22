<template>
  <div class="relative">
    <l-map
      ref="map"
      :zoom="zoom"
      :center="center"
      @click="onMapClick"
      @update:zoom="zoomUpdated"
      style="height: 500px; border-radius: 6px;"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <l-control>
        <button
          class="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded shadow"
          :disabled="!selectedPoint"
          @click="confirmSelection"
        >
          Confirmar selección
        </button>
      </l-control>

      <l-circle
        v-if="selectedPoint && radius !== null"
        :lat-lng="selectedPoint"
        :radius="radius"
        color="blue"
      />

      <l-marker
        v-if="selectedPoint"
        :lat-lng="selectedPoint"
      />
    </l-map>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import { LControl, LMap, LTileLayer, LMarker, LCircle, LPopup } from "@vue-leaflet/vue-leaflet"
import L from "leaflet"
import type { PointTuple } from "leaflet"
import type { Site } from "../types/site"
import { nextTick } from 'vue'

const MAX_RADIUS = 500_000

const emit = defineEmits<{
  (e: "confirm", v: { lat: number; long: number; radius: number }): void
}>()

const zoom = ref(13)
const center = ref<PointTuple>([-34.6037, -58.3816])

const selectedPoint = ref<[number, number] | null>(null)
const radius = ref(300) 


const props = defineProps<{
  modelValue?: { lat: number | null; long: number | null; radius: number | null } | null
  sites?: {
    id: number,
    latitud: number,
    longitud: number,
    name: string,
    short_description: string
  }[]
}>()


watch(
  () => props.modelValue,
  (val) => {
    if (val && val.lat !== null && val.long !== null && val.radius !== null) {
      selectedPoint.value = [val.lat, val.long]
      radius.value = val.radius

      center.value = [val.lat, val.long]
      zoom.value = 13

      nextTick(() => {
        map.value?.leafletObject?.invalidateSize()
        map.value?.leafletObject?.fitBounds([
          [val.lat, val.long],
          [val.lat, val.long]
        ])
      })
    } else {
      selectedPoint.value = null
    }
  },
  { immediate: true }
)


function zoomUpdated(z: number) {
  zoom.value = z
}

function calculateZoomRadius(z: number) {
  const referenceZoom = 16
  const referenceRadius = 300
  const scale = Math.pow(2, referenceZoom - z)
  const rawRadius = referenceRadius * scale

  return Math.min(rawRadius, MAX_RADIUS)
}

function onMapClick(e: any) {
  const { lat, lng } = e.latlng
  selectedPoint.value = [lat, lng]

  radius.value = calculateZoomRadius(zoom.value)
}

function isInsideRadius(lat: number, lon: number) {
  if (!selectedPoint.value || radius.value === null) return false

  const R = 6371000
  const dLat = (lat - selectedPoint.value[0]) * Math.PI / 180
  const dLon = (lon - selectedPoint.value[1]) * Math.PI / 180

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(selectedPoint.value[0] * Math.PI / 180) *
      Math.cos(lat * Math.PI / 180) *
      Math.sin(dLon / 2) ** 2

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  const dist = R * c

  return dist <= radius.value
}

function confirmSelection() {
  if (!selectedPoint.value || radius.value === null) return
  
  emit("confirm", {
    lat: selectedPoint.value[0],
    long: selectedPoint.value[1],
    radius: radius.value
  })
}

const map = ref<any>(null)
function invalidateMap() {
  map.value?.leafletObject?.invalidateSize()
}
defineExpose({ invalidateMap })
</script>