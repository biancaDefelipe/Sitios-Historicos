<template>
  <div class="content">

    <div class="filtros">
      <label for="orden">Ordenar por fecha:</label>
      <select id="orden" v-model="order" @change="onOrderChange">
        <option value="desc">Más recientes primero</option>
        <option value="asc">Más antiguas primero</option>
      </select>
    </div>

    <p v-if="loading">Cargando reseñas...</p>

    <p v-else-if="error" class="empty">
      {{ error }}
    </p>

    <p v-else-if="reviews.length === 0" class="empty">
      Aún no escribiste reseñas.
    </p>

    <ul v-else>
      <li v-for="r in reviews" :key="r.id" class="item" @click="goToSite(r.siteId)">
        <h3>{{ r.site }}</h3>

        <div>
          <p>Calificación: {{ r.rate }}/5</p>
          <span v-html="renderStars(r.rate)"></span>
        </div>

        <p>Fecha: {{ formatDate(r.fecha) }}</p>
        <p class="extracto">{{ r.extracto }}</p>
      </li>
    </ul>

    <Paginator
      v-if="total > 0"
      :page="page"
      :total="total"
      :limit="limit"
      :busy="loading"
      @page-changed="changePage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import Paginator from "@/components/Paginator.vue"
import api from '@/services/httpInterceptor'
import { usePaginationStore } from "@/stores/paginationStore"


interface Review {
  id: number
  siteId: number
  site: string
  rate: number
  fecha: string
  extracto: string
  estado: number
}

const reviews = ref<Review[]>([])

const order = ref("desc") 

const loading = ref(false)
const error = ref("")
const router = useRouter()

const pagination = usePaginationStore()
const page = computed(() => pagination.pagination.page)
const limit = computed(() => pagination.pagination.limit)
const total = computed(() => pagination.pagination.total)

onMounted(() => cargar())

function changePage(p: number) {
  if (p === pagination.pagination.page) return
  pagination.setPage(p)
  cargar()
}

function onOrderChange() {
  pagination.setPage(1)
  cargar()
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("es-AR")
}

function renderStars(n: number) {
  const val = Math.max(0, Math.min(5, Math.round(n)))
  return "★".repeat(val) + "☆".repeat(5 - val)
}

function goToSite(siteId: number) {
  if (siteId) {
    router.push(`/sites/${siteId}`)
  }
}

async function cargar() {
  loading.value = true
  error.value = ""

  try {
    const token = sessionStorage.getItem("auth.token")
    if (!token) {
      error.value = "Debes iniciar sesión."
      return
    }

    const BASE_URL = import.meta.env.VITE_API_LOCAL

   const response= await api.get(`${BASE_URL}/me/reviews`, {
      params: {
        page: page.value,
        per_page: limit.value,
        order: order.value
      },
      headers: { Authorization: `Bearer ${token}` },
    })
    if (response.status !== 200) {
      throw new Error("No se pudieron cargar las reseñas")
    }
    const data = response.data
    reviews.value = data.data
      .filter((r: any) => [1, 2, 3].includes(r.state_id))
      .map((r: any) => ({
        id: r.id,
        siteId: r.site_id,
        site: r.site_name,
        rate: r.rating,
        fecha: r.inserted_at,
        extracto: r.comment,
        estado: r.state_id
      }))


    pagination.setTotal(data.meta.total)

  } catch (err) {
    console.error(err)
    error.value = "Error al cargar las reseñas."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.filtros {
  margin-bottom: 1rem;
  display: flex;
  gap: 0.6rem;
  align-items: center;
}
.empty {
  color: #777;
  font-style: italic;
}
.extracto {
  color: #555;
  margin-top: 0.4rem;
}
.item {
  background: #fff;
  padding: 1rem;
  margin-bottom: 0.6rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
.extracto {
  color: #555;
  margin-top: 0.5rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  white-space: normal;
}
</style>
