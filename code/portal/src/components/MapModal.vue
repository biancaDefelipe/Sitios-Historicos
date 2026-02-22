<template>
  <div
    v-show="visible"
    class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg shadow-lg p-4 w-[700px] max-w-[90vw]">
      <h2 class="text-xl font-semibold mb-2">Seleccionar ubicación en el mapa</h2>
      <MapPicker
        ref="picker"
        :sites="mapSites"
        @confirm="onConfirm"
        :modelValue="modelValue"
        @close="close"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import MapPicker from './MapPicker.vue'
import { useSitesStore } from "../stores/sitesStore"

const sitesStore = useSitesStore()

const mapSites = computed(() =>
  sitesStore.sites.map(s => ({
    id: Number(s.id),
    latitud: s.lat ?? 0,
    longitud: s.long ?? 0,
    name: s.nombre ?? s.name ?? "",
    short_description: s.short_description ?? ""
  }))
)

const props = defineProps<{
  visible: boolean
  modelValue?: { lat: number | null; long: number | null; radius: number | null } | null
}>()

const emit = defineEmits(['close', 'confirm', 'update:modelValue'])

const picker = ref<InstanceType<typeof MapPicker> | null>(null)

function close() {
  emit('close')
}

function onConfirm(value: { lat: number; long: number; radius: number }) {
  emit('confirm', value)
  emit('update:modelValue', value)
}

watch(
  () => props.visible,
  async (val) => {
    if (val) {
      await nextTick()
      picker.value?.invalidateMap()
    }
  }
)
</script>