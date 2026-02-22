<template>
  <button
    :class="['btn', variantClass]"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' } 
})

const variantClass = computed(() => {
  if (props.variant === 'ghost') return 'btn-ghost'
  if (props.variant === 'neutral') return 'btn-neutral'
  if (props.variant === 'danger') return 'btn-danger' 
  return 'btn-primary'
})
</script>

<style scoped>
.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-size: 1em;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
  background: transparent;
}

/* Primary */
.btn-primary {
  background: #008B8B;
  color: #fff;
  border: 1px solid #008B8B;
}
.btn-primary:hover {
  background: #006666;
  border-color: #006666;
}

/* Ghost */
.btn-ghost {
  background: #fff;
  color: #008B8B;
  border: 1px solid #008B8B;
}
.btn-ghost:hover {
  background: #e6f7ff;
  color: #005580;
  border-color: #91d5ff;
}

.btn-neutral {
  background: #fff;
  color: #666;
  border: 1px solid #ccc;
}
.btn-neutral:hover {
  background: #f5f5f5;
  color: #333;
  border-color: #bbb;
}

.btn-danger {
  background: #dc2626; 
  color: #fff;
  border: 1px solid #dc2626;
}
.btn-danger:hover {
  background: #b91c1c; 
  border-color: #b91c1c;
}
</style>