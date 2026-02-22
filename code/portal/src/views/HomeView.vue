<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SiteCard from '../components/SiteCard.vue'
import SitePanel from '../components/SitePanel.vue'
import SearchBar from '../components/SearchBar.vue'
import { useSitesStore } from '../stores/sitesStore'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from "@/stores/myFavoritesStore"

const favStore = useFavoritesStore()
const router = useRouter()
const store = useSitesStore()
const search = ref('')

function buscar(q = '') {
  const query = q || search.value || ''
  router.push({ name: 'buscar', query: { q: query } })
}

function verTodos(tipo: string) {
  let orderBy = "latest"

   if (tipo === "favoritos") {
    return router.push({
      name: "buscar",
      query: { favorites: true } as any
    })
  }

  if (tipo === "mejor-puntuados") {
    orderBy = "rating-5-1"
  }

  if (tipo === "recientes") {
    orderBy = "latest"
  }

  router.push({
    name: "buscar",
    query: { order_by: orderBy }
  })
}

onMounted(async () => {
  store.filters.q = ""
  store.filters.city = ""
  store.filters.province = ""
  store.filters.tags = []
  store.filters.favorites = false
  store.filters.order_by = "latest"
  store.filters.map = {
    lat: null,
    long: null,
    radius: null,
  }


    await Promise.all([
      store.fetchTopRankedSites(),
      store.fetchLatestSites(),
      auth.token ? favStore.fetchFavorites() : Promise.resolve(),
    ]).catch(() => {})
  })

const loading = computed(() => store.loading)

const mejorPuntuados = computed(() => store.topRanked)
const recientementeAgregados = computed(() => store.latest)
const favoritos = computed(() => favStore.items)

const auth = useAuthStore()
const isAuthenticated = computed(() => !!auth.token)

</script>

<template>
  <div class="home">
    <section class="hero">
      <h1 class="title-text">Portal de Sitios Históricos</h1>
      <SearchBar v-model="search" @search="buscar"></SearchBar>
    </section>

    <SitePanel title="Mejor puntuados" :items="mejorPuntuados" :loading="loading" @view-all="verTodos('mejor-puntuados')">
      <template #item="{ item }">
        <SiteCard :site="item" />
      </template>
    </SitePanel>

    <SitePanel title="Recientemente agregados" :items="recientementeAgregados" :loading="loading" @view-all="verTodos('recientes')">
      <template #item="{ item }">
        <SiteCard :site="item" />
      </template>
    </SitePanel>

    <SitePanel v-if="isAuthenticated" title="Mis favoritos" :items="favoritos" :loading="loading" @view-all="verTodos('favoritos')">
      <template #item="{ item }">
        <SiteCard :site="item" />
      </template>
    </SitePanel>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: transparent;
}
.hero {
  margin-top: -80px;
  background: #0B2F3A;
  color: #F5F5F5;
  padding: 3rem 1rem;
  padding-bottom: 6rem;
  padding-top: 8rem;    
  text-align: center;
}
.hero h1 {
  font-size: 2.2rem;
  margin-bottom: 1.5rem;
  color: #F5F5F5;
}
</style>