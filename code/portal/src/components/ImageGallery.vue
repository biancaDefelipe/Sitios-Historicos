<template>
  <div class="gallery">
    <img
      v-if="currentImage"
      :src="currentImage.public_url"
      :alt="currentImage.alt_text || 'Imagen del sitio'"
      class="gallery-cover"
    />

    <div v-if="images.length > 1" class="gallery-thumbs">
      <img
        v-for="img in images"
        :key="img.id"
        :src="img.public_url"
        :alt="img.alt_text || 'Miniatura'"
        :class="{ active: img.id === currentImage?.id }"
        @click="currentImage = img"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Image } from '../types/image.ts'

const props = defineProps<{
  cover?: Image | null
  images: Image[]
}>()

const currentImage = ref<Image | null>(props.cover ?? props.images[0] ?? null)

watch(
  () => props.cover,
  (newVal) => {
    currentImage.value = newVal ?? props.images[0] ?? null
  }
)
</script>

<style scoped>
.gallery {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: none;
  outline: none;
}

.gallery-cover {
  width: 100%;
  height: 390px;
  object-fit: contain;
  border-radius: 10px;
  background-color: black;
}

.gallery-thumbs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scroll-behavior: smooth;
}

.gallery-thumbs img {
  width: 110px;
  height: 75px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity .2s, transform .2s;
}

.gallery-thumbs img:hover {
  opacity: 1;
  transform: scale(1.05);
}

.gallery-thumbs img.active {
  opacity: 1;
  border: 2px solid #0078ff;
}
</style>