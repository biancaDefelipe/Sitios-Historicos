<template>
  <div class="search-bar">
    <input
      :value="modelValue"
      type="text"
      placeholder="¿Qué desea buscar?"
      @input="$emit('update:modelValue', $event.target.value)"
      @keyup.enter="emitSearch"
    />
    <button @click="emitSearch">Buscar</button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: String
})
const emit = defineEmits(['update:modelValue', 'search'])

function emitSearch() {
  emit('search', props.modelValue || '')
}
</script>

<style scoped>
.search-bar {
  max-width: 600px;
  margin: 0 auto 2rem;
  display: flex;
  gap: 0.5rem;
}

.search-bar input {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.search-bar button {
  padding: 0.75rem 1.5rem;
  background: #008B8B;
  color: #F5F5F5;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.search-bar button:hover {
  background: #006666;
}
</style>