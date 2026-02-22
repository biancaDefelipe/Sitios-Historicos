<template>
  <div>
    <div v-if="loading" class="loading">Cargando favoritos...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="!loading && items.length === 0" class="empty">
      No tenés sitios favoritos aún.
    </div>

    <div v-else class="list">
      <SiteCard
        v-for="fav in items"
        :key="fav.id"
        :site="fav"
        variant="compact"
      />

      <Paginator
        :page="page"
        :limit="limit"
        :total="total"
        @page-changed="onPageChanged"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue"
import { storeToRefs } from "pinia"
import SiteCard from "@/components/SiteCard.vue"
import Paginator from "@/components/Paginator.vue"
import { useFavoritesStore } from "@/stores/myFavoritesStore"
import { usePaginationStore } from "@/stores/paginationStore"

const pagination = usePaginationStore()
const favorites = useFavoritesStore()
const { items, loading, error } = storeToRefs(favorites)

const page = computed(() => pagination.pagination.page)
const limit = computed(() => pagination.pagination.limit)
const total = computed(() => pagination.pagination.total)

onMounted(async () => {
  pagination.setPage(1)
  await favorites.fetchFavorites()
})

async function onPageChanged(p: number) {
  if (p ===pagination.pagination.page) return
  pagination.setPage(p)
  await favorites.fetchFavorites()
}
</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.loading, .error, .empty {
  margin-top: 1rem;
  color: #555;
}
</style>