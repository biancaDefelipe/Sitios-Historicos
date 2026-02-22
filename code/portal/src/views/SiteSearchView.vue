<template>
  <div class="sites-view">
    <div class="layout">
      <main class="content">

        <section class="search-section">
          <h1 class="title-text">Búsqueda de Sitios</h1>
          <SearchBar v-model="q" @search="onSearch" />
        </section>

        <section class="search-section">
          <FiltersPanel
            :externalDirty="filtersDirty"
            @update-filters="() => store.fetchAllSites()"
            @reset-filters="onResetFilters"
          >
            <template #controls>

              <Selector
                v-model="province"
                label="Provincia"
                placeholder="Todas las Provincias"
                :options="store.provinces.map(p => ({ label: p, value: p }))"
              />

              <TextInput
                v-model="city"
                label="Ciudad"
                placeholder="Ingrese una ciudad..."
              />

              <MultiSelector
                v-model="tags"
                label="Tags"
                placeholder="Todos"
                :options="store.tagsList.map(t => ({ label: t, value: t }))"
              />

              <Selector
                v-model="order_by"
                label="Ordenar por"
                :options="[
                  { label: 'Fecha (más recientes)', value: 'latest' },
                  { label: 'Fecha (más antiguos)', value: 'oldest' },
                  { label: 'Nombre (A-Z)', value: 'name-asc' },
                  { label: 'Nombre (Z-A)', value: 'name-desc' },
                  { label: 'Puntaje (mejor valorados)', value: 'rating-5-1' },
                  { label: 'Peores (peor valorados)', value: 'rating-1-5' }
                ]"
              />

              <Checkbox
                v-if="authStore.token"
                v-model="favorites"
                label="Sitios Favoritos"
                description="Ver solo sitios favoritos"
              />
            </template>
          </FiltersPanel>

          <div class="flex justify-between items-center mb-2">
            <button
              class="border px-3 py-1 rounded"
              :class="{ 'bg-gray-200': mapVisible }"
              @click="toggleMap"
            >
              {{ mapVisible ? 'Ocultar mapa' : 'Ver mapa' }}
            </button>
          </div>

          <MapModal
            :visible="mapVisible"
            :modelValue="store.filters.map"
            @close="mapVisible = false"
            @confirm="setMapFilter"
          />

          <SitesPanel
            title="Resultados"
            :items="sitesList"
            :loading="loading"
            :showViewAll="false"
            layout="list"
          >
            <template #item="{ item }">
              <SiteCard :site="item" variant="compact" />
            </template>
          </SitesPanel>

          <Paginator
            v-if="pagination.total > 0 && !loading"
            :page="pagination.page"
            :total="pagination.total"
            :limit="pagination.limit"
            :busy="loading"
            @page-changed="onPageChanged"
          />

        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSitesStore } from '../stores/sitesStore'
import { useAuthStore } from '@/stores/authStore'
import { usePaginationStore } from '@/stores/paginationStore'

import SearchBar from '../components/SearchBar.vue'
import FiltersPanel from '../components/FiltersPanel.vue'
import TextInput from '@/components/TextInput.vue'
import Selector from '@/components/Selector.vue'
import MultiSelector from '@/components/MultiSelector.vue'
import Checkbox from '@/components/Checkbox.vue'
import MapModal from '../components/MapModal.vue'
import SiteCard from '../components/SiteCard.vue'
import SitesPanel from '../components/SitePanel.vue'
import Paginator from '../components/Paginator.vue'

function getQueryString(v: unknown, fb = '') { return typeof v === 'string' ? v : fb }
function getQueryArray(v: unknown) { return typeof v === 'string' ? v.split(',') : [] }

const route = useRoute()
const router = useRouter()
const store = useSitesStore()
const authStore = useAuthStore()
const paginationStore = usePaginationStore()

const q = ref(getQueryString(route.query.q))
const province = ref(getQueryString(route.query.province))
const city = ref(getQueryString(route.query.city))
const tags = ref(getQueryArray(route.query.tags))
const favorites = ref(route.query.favorites === 'true')
const order_by = ref(getQueryString(route.query.order_by, 'latest'))

const mapVisible = ref(false)

const loading = computed(() => store.loading)
const sitesList = computed(() => store.sites)
const filtersDirty = computed(() => store.isDirty)
const pagination = computed(() => paginationStore.pagination)

watch([q, province, city, tags, favorites, order_by], () => {
  store.filters.q = q.value
  store.filters.city = city.value
  store.filters.province = province.value
  store.filters.tags = tags.value
  store.filters.favorites = favorites.value
  store.filters.order_by = order_by.value

  syncQuery()
}, { deep: true, immediate: false })

function syncQuery() {
  const query = {
      q: q.value || undefined,
      province: province.value || undefined,
      city: city.value || undefined,
      tags: tags.value.length ? tags.value.join(',') : undefined,
      favorites: authStore.token && favorites.value ? 'true' : undefined,
      order_by: order_by.value,
      lat: store.filters.map.lat !== null ? store.filters.map.lat : undefined,
      long: store.filters.map.long !== null ? store.filters.map.long : undefined,
      radius: store.filters.map.radius !== null ? store.filters.map.radius : undefined,
      page: pagination.value.page
  }

  router.replace({ query })
  store.setLastSearch(query)

}

function onSearch(value: string) {
  const trimmed = value.trim()
  q.value = trimmed
  paginationStore.setPage(1)
  store.fetchAllSites()
}

function setMapFilter(v: { lat: number; long: number; radius: number }) {
  store.setMapFilter(v)
  syncQuery()
}

function toggleMap() {
  mapVisible.value = !mapVisible.value
}

function onResetFilters() {
  store.resetFilters()

  q.value = ""
  province.value = ""
  city.value = ""
  tags.value = []
  favorites.value = false
  order_by.value = "latest"

  store.clearMapFilter()

 
  paginationStore.resetPagination() 

  store.fetchAllSites().then(() => {
    syncQuery()
  })


}

function onPageChanged(page: number) {
  
  paginationStore.setPage(page)
  store.fetchAllSites()
}

onMounted(async () => {
  if (route.query.order_by) {
    store.filters.order_by = String(route.query.order_by)
  }

  if (!authStore.token) {
    favorites.value = false
    store.filters.favorites = false
    router.replace({
      query: {
        ...route.query,
        favorites: undefined
      }
    })
  }
  
  await store.fetchFiltersData()

  store.filters.q = q.value
  store.filters.city = city.value
  store.filters.province = province.value
  store.filters.tags = tags.value
  store.filters.favorites = favorites.value
  store.filters.order_by = order_by.value

  if (route.query.lat && route.query.long && route.query.radius) {
    store.filters.map.lat = Number(route.query.lat)
    store.filters.map.long = Number(route.query.long)
    store.filters.map.radius = Number(route.query.radius)
  }

  store.fetchAllSites()
  syncQuery()
})
</script>

<style scoped>
.sites-view {
  min-height: 100vh;
  background: transparent;
}
.search-section {
  max-width: 1200px;
  margin: 3rem auto;
  padding: 0 1rem;
}
.no-results {
  text-align: center;
  margin-top: 2rem;
  color: #999;
  font-style: italic;
}
</style>