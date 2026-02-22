<template>
  <button @click="goBack" class="inline-flex items-center gap-2">
    ← Volver
  </button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSitesStore } from '@/stores/sitesStore'

const router = useRouter()
const store = useSitesStore()

function goBack() {
  if (Object.keys(store.lastSearch).length > 0) {
    router.push({
      name: 'buscar',
      query: store.lastSearch
    })
  } else {
    router.push({ name: 'buscar' })
  }
}
</script>

<style scoped>
button {
  cursor: pointer;
  font-size: 1rem;
  color: #000;
  background: none;
  border: none;
  border-radius: 6px;
  padding: 0;
  transition: background .2s;
}

button:hover {
  background: #e6e6e6;
}
</style>