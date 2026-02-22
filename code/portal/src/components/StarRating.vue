<template>
<div class="stars" role="img" :aria-label="`Valoración: ${value} de 5`">
  <span
    v-for="n in 5"
    :key="n"
    class="star"
  >
    {{ n <= Math.round(value) ? '★' : '☆' }}
  </span>
</div>
</template>

<script setup lang="ts">
const props = defineProps<{ value: number, readonly?: boolean }>()

</script>


<style scoped>
.stars {
  display: flex;
  gap: 4px;
  font-size: 1.2rem;
  color: #f0b800;
}

.star {
  cursor: default;
}
</style>