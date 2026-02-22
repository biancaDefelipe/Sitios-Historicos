<template>
  <span
    :class="['chip', { 'chip-clickable': clickable }]"
    @click="clickable ? onClick() : null"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  label: string
  clickable?: boolean
  toTagSearch?: boolean 
}>()

const router = useRouter()

function onClick() {
  if (props.toTagSearch) {
    router.push({ name: 'buscar', query: { tags: props.label } })
  }
}
</script>

<style scoped>
.chip {
  padding: 4px 10px;
  background: #f3f3f3;
  border-radius: 12px;
  font-size: 0.85rem;
  color: #444;
  border: 1px solid #e0e0e0;
}

.chip-clickable {
  cursor: pointer;
}

.chip-clickable:hover {
  background: #e7e7e7;
}
</style>