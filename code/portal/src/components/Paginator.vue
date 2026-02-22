<template>
  <div class="paginator" v-if="totalPages > 0">
    <button class="page-btn" :disabled="page <= 1 || busy" @click="changePage(page - 1)" aria-label="Página anterior" >Anterior</button>

    <div class="pages">
      <button
        v-for="p in pagesToShow"
        :key="p"
        :class="['page-number', { active: p === page }]"
        @click="changePage(p)"
        :disabled="busy"
        :aria-label="`Ir a la página ${p}`"
        :aria-current="p === page ? 'page' : undefined"
      >
        {{ p }}
      </button>
    </div>

    <button class="page-btn" :disabled="page >= totalPages || busy" @click="changePage(page + 1)" aria-label="Página siguiente">Siguiente</button>

    <div class="summary" v-if="showSummary">
      {{ summaryText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  total: { type: Number, required: true },
  limit: { type: Number, required: true },
  busy: { type: Boolean, default: false },
  maxPagesToShow: { type: Number, default: 5 },
  showSummary: { type: Boolean, default: true },
})

const emit = defineEmits(['page-changed'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.limit)))

const pagesToShow = computed(() => {
  const pages: number[] = []
  const max = props.maxPagesToShow
  const half = Math.floor(max / 2)
  let start = Math.max(1, props.page - half)
  let end = Math.min(totalPages.value, start + max - 1)
  if (end - start + 1 < max) start = Math.max(1, end - max + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const startIndex = computed(() => {
  if (props.total === 0) return 0
  return (props.page - 1) * props.limit + 1
})

const endIndex = computed(() => {
  if (props.total === 0) return 0
  return Math.min(props.total, props.page * props.limit)
})

const summaryText = computed(() => {
  if (props.total === 0) return 'No se encontraron resultados'
  return `Mostrando ${startIndex.value}–${endIndex.value} de ${props.total} resultados`
})

function changePage(p: number) {
  if (p < 1) p = 1
  if (p > totalPages.value) p = totalPages.value
  if (p === props.page) return
  emit('page-changed', p)
}
</script>

<style scoped>
.paginator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}
.page-btn {
  padding: 0.5rem 1rem;
  background: #008B8B;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.page-btn.active:hover {
  background: #0B2F3A;;
  color: #fff;
}
.page-btn[disabled] { opacity: 0.6; cursor: not-allowed; }
.pages { display:flex; gap:0.4rem; }
.page-number {
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  background: #fff;
  cursor: pointer;
  transition: background 0.2s;
}
.page-number.active {
  background: #008B8B;
  color: #fff;
  border-color: #008B8B;
}
.page-number.active:hover {
  background: #006666;
  color: #fff;
  border-color: #006666;
  transition: background 0.2s;
}
.page-number[disabled] { opacity: 0.6; cursor: not-allowed; }

.summary {
  margin-left: 1rem;
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}
</style>