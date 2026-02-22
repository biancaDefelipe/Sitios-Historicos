<template>
  <div class="multi-select" ref="dropdown">
    <label v-if="label" class="multi-label">{{ label }}</label>

    <div class="multi-display" @click="toggleOpen">
      <span v-if="!selectedLabels.length" class="placeholder">
        {{ placeholder || 'Seleccionar...' }}
      </span>
      <span v-else class="selected-summary">
        {{ selectedLabels.length === 1
          ? selectedLabels[0]
          : selectedLabels.length + ' seleccionados'
        }}
      </span>
      <span class="caret">{{ open ? '▴' : '▾' }}</span>
    </div>

    <div v-if="open" class="dropdown" role="listbox" aria-multiselectable="true">
      <div
        v-for="opt in options"
        :key="opt.value"
        class="option-item"
        @click.stop="toggleOption(opt.value)"
      >
        <input
          type="checkbox"
          :checked="modelValue.includes(opt.value)"
          class="checkbox"
        />
        <label>{{ opt.label }}</label>
      </div>
      <div v-if="modelValue.length" class="clear" @click.stop="clearAll">
        Limpiar selección
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onClickOutside } from '@vueuse/core'

const dropdown = ref<HTMLElement | null>(null)
const open = ref(false)

type Option = {
  label: string
  value: string
}

const props = defineProps<{
  label?: string
  options: Option[]
  modelValue: string[]
  placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])

const selectedLabels = computed(() =>
  props.options
    .filter(o => props.modelValue.includes(o.value))
    .map(o => o.label)
)

function dispatchNativeInput() {
  try {
    dropdown.value?.dispatchEvent(new Event('input', { bubbles: true }))
  } catch (e) {
    return 
  }
}

function toggleOption(value: string) {
  const current = [...props.modelValue]
  const index = current.indexOf(value)
  if (index >= 0) current.splice(index, 1)
  else current.push(value)
  emit('update:modelValue', current)
  
  dispatchNativeInput()
}

function clearAll() {
  emit('update:modelValue', [])

  dispatchNativeInput()
}

function toggleOpen() {
  if (props.options.length !== 0) {
    open.value = !open.value
  }
}

onClickOutside(dropdown, () => (open.value = false))
</script>

<style scoped>
.multi-select {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.multi-label {
  font-weight: 600;
  font-size: 0.95rem;
  color: #0B2F3A;
}

.multi-display {
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 160px;
  color: #000000;
}

.multi-display:hover {
  border-color: #ccc;
}

.placeholder {
  color: #000000;
  font-size: 0.9rem;
}

.dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 10;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.4rem 0;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  cursor: pointer;
  color: #000000;
  font-size: 0.9rem;
}

.option-item:hover {
  background: #f3f8f8;
}

.checkbox {
  pointer-events: none;
  width: 16px;
  height: 16px;
}

.clear {
  text-align: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: red;
  padding: 0.3rem 0;
  cursor: pointer;
  border-top: 1px solid #d2d2d2;
}

.clear:hover {
  background: #f0fafa;
}
</style>