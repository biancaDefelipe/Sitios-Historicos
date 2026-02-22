<template>
  <div>
    <div v-if="loading" class="text-gray-500 mt-2 text-center">Cargando reseñas...</div>

    <div v-else-if="!reviews || reviews.length === 0" class="empty-container">
      {{ emptyMessage || 'No hay reseñas para este sitio todavía.' }}
    </div>

    <div v-else class="flex flex-col gap-4 mt-2">
      <ReviewCard
        v-for="review in reviews"
        :key="review.id"
        :rating="review.rating"
        :comment="review.comment"
        :date="review.inserted_at"
        :alias="review.alias"
      />
    </div>

    <Paginator
      v-if="totalReviews > (limit || 0)"
      :page="page"
      :total="totalReviews"
      :limit="limit"
      :busy="loading"
      @page-changed="$emit('page-changed', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import ReviewCard from './ReviewCard.vue'
import Paginator from './Paginator.vue'
import type { Review } from '../types/review'

defineProps<{
  reviews: Review[]
  loading: boolean
  totalReviews: number
  page: number
  limit: number
  emptyMessage?: string
}>()

defineEmits(['page-changed'])
</script>

<style scoped>

.empty-container {
  display: flex;         
  justify-content: center; 
  align-items: center;     
  width: 100%;             
  padding: 2rem 0;         
  text-align: center;      

  color: #6b7280;     
  font-style: italic;
}
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.loading {
  color: #888;
  text-align: center;
  margin: 2rem 0;
}
</style>