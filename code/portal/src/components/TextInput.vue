<template>
  <div class="text-field">
    <label v-if="label" class="text-label">{{ label }}</label>

    <input
      type="text"
      class="text-input"
      :placeholder="placeholder"
      :value="modelValue"
      @input="onInput"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label?: string
  modelValue?: string
  placeholder?: string
}>()

const emit = defineEmits(["update:modelValue"])

function onInput(e: Event) {
  const v = (e.target as HTMLInputElement).value
  emit("update:modelValue", v)
}
</script>

<style scoped>
.text-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.text-label {
  font-weight: 600;
  font-size: 0.95rem;
  color: #0B2F3A;
}

.text-input {
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  background: #fff;
  min-width: 160px;
}
</style>