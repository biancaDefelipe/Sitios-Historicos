<template>
  <div :class="['site-card', variantClass]" @click="goToDetail">
    <template v-if="variant === 'card'">
      <div class="site-image">
        <img :src="site.imagen || site.image || 'https://via.placeholder.com/300x180?text=Sin+Imagen'" :alt="site.nombre || site.name" />
      </div>
      <div class="site-info">
        <h3>{{ site.nombre || site.name }}</h3>
        <p class="location">{{ site.ciudad || site.location }}, {{ site.provincia || '' }}</p>
        <div v-if="site.calificacion" class="rating">⭐ {{ (site.calificacion || 0).toFixed(1) }}</div>
      </div>
    </template>

    <template v-else-if="variant === 'compact'">
      <div class="compact-row">

        <img
          v-if="coverImage"
          class="compact-cover"
          :src="coverImage.public_url"
          :alt="coverImage.alt_text || 'Portada'"
        />

        <div class="compact-info">
          <h3 class="compact-title">{{ site.nombre || site.name }}</h3>
          <p v-if="site.rank" class="rating">⭐ {{ (site.rank || 0).toFixed(1) }}</p>
          <p class="location">{{ location }}</p>

          <p v-if="site.estado_conservacion || site.state_of_conservation" class="estado-compact">
            Estado: <strong>{{ site.estado_conservacion || site.state_of_conservation }}</strong>
          </p>

          <div class="tags-section">
            <span class="tags-label">Tags:</span>
            <TagList :tags="limitedTags" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import TagList from './TagList.vue'
import type { Image } from '../types/image'

const props = defineProps<{
  site: any,
  variant?: 'card' | 'compact'
}>()

const router = useRouter()
const variant = props.variant || 'card'

const limitedTags = computed(() => {
  if (!props.site.tags) return []
  return props.site.tags.slice(0, 5)
})

const coverImage = computed(() => {
  if (Array.isArray(props.site.images)) {
    return props.site.images.find((img: Image) => img.is_cover) || props.site.images[0];
  }
  return null;
});

const location = computed(() => {
  const c = props.site.ciudad || props.site.city || ""
  const p = props.site.provincia || props.site.province || ""
  return `${c}${c && p ? ', ' : ''}${p}`
})

function goToDetail() {
  const id = props.site?.id ?? props.site?.ID
  if (id) router.push(`/sites/${id}`)
}

const variantClass = computed(() => variant === 'compact' ? 'compact' : 'detailed')
</script>

<style scoped>
.site-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
  background: #fff;
}
.site-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.site-card.detailed .site-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
}
.site-card.detailed .site-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.site-info {
  padding: 1rem;
  color: #0B2F3A;
}
.site-info h3 {
  color: #0B2F3A;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.location {
  color: #0B2F3A;
  font-size: 0.9rem;
}
.rating {
  margin-top: 0.5rem;
  color: #0B2F3A;
}

.compact-wrapper {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}
.compact-cover {
  width: 160px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}
.compact-info {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  flex: 1;
  overflow: hidden;
}
.compact-row {
  display: flex;
  flex-direction: row;
  gap: 12px;
  padding: 8px;
  align-items: flex-start;
}
.compact-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: #000;
}
.site-card.compact {
  display: flex;
  flex-direction: row;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  background: #fff;
}
.site-compact-info {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.site-compact-info h3 {
  margin: 0;
  font-size: 1rem;
  color: #383838;
  font-weight: bold;
}
.site-compact-info .location {
  color: #383838;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
.compact-left {
  display: flex;
  flex-direction: column;
}
.compact-right .type {
  font-size: 0.85rem;
  color: #008B8B;
}

.compact-container {
  padding: 0.8rem 0.4rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.compact-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.location {
  color: #000;
  font-size: 0.85rem;
}

.estado-compact {
  margin-top: 4px;
  font-size: 0.85rem;
  color: #000;
}

.tags-label{
  font-size: 0.85rem;
  color: #0B2F3A;
  margin-right: 6px;
}


</style>