<template>
  <label :for="id" class="checkbox-field">
    <span class="checkbox-label">{{label}}</span>

    <div class="checkbox-container">
      <input
        :id="id"
        type="checkbox"
        :checked="modelValue"
        @change="onChange"
        class="checkbox-input"
      />
      <span v-if="description" class="checkbox-description">{{ description }}</span>
    </div>
  </label>
</template>

<script setup lang="ts">
const props = defineProps<{
  label?: string
  description?: string
  modelValue?: boolean
  id?: string
}>()

const emit = defineEmits(['update:modelValue'])

const id = props.id || `cb-${Math.random().toString(36).slice(2,9)}`

function onChange(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  emit('update:modelValue', checked)
}
</script>

<style scoped>
.checkbox-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-input { width: 16px; height: 16px; }
.checkbox-label { font-weight: 600; font-size: 0.95rem; color: #0B2F3A; }
.checkbox-description { font-size: 0.9rem; color: #233; }
</style>