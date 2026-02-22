<template>
  <input
    :type="type"
    :placeholder="placeholder"
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    class="base-input"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
const props = defineProps({
  modelValue: String,
  type: { type: String, default: 'text' },
  placeholder: String
})
</script>

<style scoped>
.base-input {
  padding: 0.7rem;
  border-radius: 6px;
  border: 1px solid #008B8B;
  font-size: 1em;
  background: #f8fafc;
  color: #0B2F3A;
  width: 100%;
}
</style>