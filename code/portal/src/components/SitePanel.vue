<template>
  <section class="sites-section">
    <div class="section-header">
      <h2 class="subtitle-text">{{ title }}</h2>
      <button v-if="showViewAll" @click="$emit('view-all')">Ver todos</button>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else-if="items.length === 0" class="empty-message">No hay sitios.</div>

    <div v-else :class="['sites-container', layoutClass]">
      <template v-for="item in items" :key="item.id">
        <slot name="item" :item="item">
          <SiteCard :site="item" />
        </slot>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SiteCard from './SiteCard.vue'

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array as () => any[], required: true },
  loading: { type: Boolean, default: false },
  showViewAll: { type: Boolean, default: true },
  layout: { type: String as () => 'grid' | 'list', default: 'grid' }
})

const layoutClass = computed(() =>
  props.layout === 'list' ? 'list-layout' : 'grid-layout'
)
</script>

<style scoped>
.sites-section {
  max-width: 1200px;
  margin: 3rem auto;
  padding: 0 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.8rem;
  color: #001F3F;
}

.section-header button {
  padding: 0.5rem 1rem;
  background: transparent;
  color: #0B2F3A;
  border: 2px solid #0B2F3A;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.section-header button:hover {
  background: #ebebeb;
}

.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.list-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading,
.empty-message {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>