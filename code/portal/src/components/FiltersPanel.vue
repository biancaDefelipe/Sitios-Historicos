<template>
  <div class="filters-panel-wrapper" @update:modelValue="handleChange" @input="handleChange">
    <button class="filters-toggle" @click="open = !open">
      Filtros <span class="caret">{{ open ? '▴' : '▾' }}</span>
    </button>

    <div :class="['filters-panel', { open }]">
      <div class="filters-inner">
        <slot name="controls"></slot>
      </div>

      <div class="filters-actions">
        <button class="clear-btn" :disabled="!dirty" @click="resetAll">Limpiar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { debounce } from 'lodash-es'

type DynCtrl = { component: any; props?: Record<string, any> }
const props = defineProps<{ components?: DynCtrl[]; externalDirty?: boolean }>()

const emit = defineEmits(['update-filters', 'reset-filters'])

const open = ref(false)
const dirty = ref(false)

const debouncedEmitFiltersUpdate = debounce(() => {
  emit('update-filters')
}, 300)

const handleChange = async () => {
  await nextTick()
  dirty.value = true
  debouncedEmitFiltersUpdate()
}

watch(
  () => props.externalDirty,
  (val) => {
    dirty.value = !!val
  },
  { immediate: true }
)

const resetAll = () => {
  emit('reset-filters')
  nextTick(() => {
    dirty.value = false
  })
}
</script>

<style scoped>
.filters-toggle {
  display: block;
  width: 100%;
  padding: 0.6rem 0.8rem;
  color: #fff;
  border-color: #008B8B;
  background: #008B8B;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 0.75rem;
  text-align: left;
  transition: background 0.2s;
}
.filters-toggle:hover { background: #006666; }

.filters-panel {
  display: none;
  gap: 0.75rem;
  padding: 0.5rem 0;
}
.filters-panel.open {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filters-inner {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
@media (max-width: 768px) {
  .filters-inner { grid-template-columns: 1fr; }
}

.filters-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.clear-btn {
  background: #e70000;
  border: 1px solid;
  color: #fff;
  border-radius: 6px;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.clear-btn:hover { background: #c00000; }
.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #999;
  border-color: #999;
}
</style>