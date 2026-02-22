<template>
  <div class="select-field">
    <label v-if="label" class="select-label">{{ label }}</label>
    <select :value="modelValue" @change="onChange" class="select-input">
      <option v-if="placeholder" class="select-placeholder" value="">
        {{ placeholder }}
      </option>
      <option
        v-for="opt in options"
        class="select-item"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
type Option = {
  label: string
  value: string
}

const props = defineProps<{
  label?: string
  modelValue?: string
  options: Option[]
  placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])

function onChange(e: Event) {
  const v = (e.target as HTMLSelectElement).value
  emit('update:modelValue', v)
}
</script>

<style scoped>
.select-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.select-label {
  font-weight: 600;
  font-size: 0.95rem;
  color: #0B2F3A;
}
.select-input {
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  background: #fff;
  min-width: 160px;
  cursor: pointer;
}
.select-item:hover {
  background: #f3f8f8;
  cursor: pointer;
}
.select-placeholder {
  color: #000;
}
</style>