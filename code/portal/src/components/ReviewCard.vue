<template>
  <div class="review-card">

    <div class="review-header">
      <span class="review-author">{{ authorLabel }}</span>
      <slot name="header-info"></slot>

      <span class="review-rating" aria-hidden="true">
        <span v-html="starsHtml"></span>
        <span class="review-score">{{ rating }}/5</span>
      </span>
    </div>

    <div class="review-text">{{ comment }}</div>

    <div class="review-footer">
      <span class="review-date">{{ formattedDate }}</span>

      <template v-if="isOwn">
        <BaseButton variant="ghost" @click="$emit('edit')">Editar</BaseButton>
        <BaseButton
          variant="ghost"
          @click="$emit('delete')"
          style="color:#a8071a;border-color:#ffa39e;"
        >
          Eliminar
        </BaseButton>
      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
import BaseButton from './BaseButton.vue'
import { computed } from 'vue'

const props = defineProps<{
  id?: number | string
  rating: number
  comment: string
  date?: string
  alias?: string | null
  isOwn?: boolean
}>()

const emits = defineEmits(['edit', 'delete'])

const authorLabel = computed(() => props.alias || 'Usuario')

const formattedDate = computed(() => {
  if (!props.date) return ''
  const d = new Date(props.date)
  if (isNaN(d.getTime())) return props.date
  return d.toLocaleDateString()
})

const starsHtml = computed(() => {
  const n = Math.max(0, Math.min(5, Math.round(Number(props.rating) || 0)))
  return '★'.repeat(n) + '☆'.repeat(5 - n)
})
</script>

<style scoped>
.review-card {
  background-color: var(--card-bg, #f5f5f5);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-bottom: 1rem;
  width: 100%;
  box-sizing: border-box;
}
.review-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}
.review-author {
  font-weight: bold;
  color: #0B2F3A;
}
.review-rating {
  color: #f7b500;
  font-size: 1.1em;
}
.review-score {
  color: #333;
  margin-left: 0.3em;
  font-size: 0.95em;
}
.review-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.review-date {
  color: #888;
  font-size: 0.95em;
}
.review-text {
  color: #222;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-line;
  margin-bottom: 0.8rem;
}
</style>