<template>
  <textarea
    :placeholder="placeholder"
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    class="base-textarea"
    v-bind="$attrs">
  </textarea>
</template>

<script setup lang="ts">
const props = defineProps({
  modelValue: String,
  placeholder: String
})
</script>

<style scoped>
.base-textarea {
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid #008B8B;
  font-size: 1em;
  background: #f8fafc;
  color: #0B2F3A;
  width: 100%;
  min-height: 120px;
  resize: None;
}
</style>