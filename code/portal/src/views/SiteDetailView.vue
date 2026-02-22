<template>
  <main class="max-w-3xl mx-auto p-4">
    <BackButton />

    <header class="mb-3">
      <h1 class="text-2xl font-semibold">{{ siteStore.site?.name }} <FavoriteButton :siteId="id" /></h1>
      <div class="flex items-center gap-2 mt-1">
        <span class="text-sm text-muted">
          {{ siteStore.site?.city }}, {{ siteStore.site?.province }}
        </span>
        <br>
        <Chip :label="siteStore.site?.state_of_conservation" :clickable="false" />
      </div>

      <div class="mt-2 flex items-center gap-2">
        <p v-if="siteStore.reviews && siteStore.site?.rank" class="rating">{{ (siteStore.site?.rank || 0).toFixed(1) }}⭐</p>
        <p v-else>Aún no hay reseñas</p>
        <small>({{ siteStore.totalReviews }} reseñas)</small>
      </div>
    </header>

        <section class="mt-3">
            <h2 class="font-medium">Imágenes</h2> 
            <ImageGallery
              :cover="siteStore.coverImage"
              :images="siteStore.galleryImages"
            />
        </section>

    <section class="mt-3">
      <h2 class="font-medium">Descripción</h2>
      <ExpandableText :text="siteStore.site?.short_description" :fullText="siteStore.site?.description" />
    </section>

    <section class="mt-3">
      <h2 class="font-medium">Etiquetas</h2>
      <p v-if="!siteStore.site?.tags || siteStore.site.tags.length === 0" class="text-gray-500 mt-2">
        El sitio no posee etiquetas.
      </p>
      <div v-else class="flex flex-wrap gap-2 mt-2">
        <Chip v-for="tag in siteStore.site.tags" :key="tag" :label="tag" clickable toTagSearch />
      </div>
    </section>

    <section class="mt-3">
      <h2 class="font-medium">Ubicación</h2>
      <MapSection :lat="siteStore.site?.lat" :long="siteStore.site?.long" :tooltipText="siteStore.site?.name"
        :tooltipDesc="siteStore.site?.short_description" />
    </section>

    <section class="mt-4">
  <div class="flex justify-between items-center mb-4">
    <h2 class="font-medium">Reseñas</h2>

    <!-- 1. CASO: RESEÑAS DESHABILITADAS -->
    <div v-if="!configStore.reviewsEnabled">
      <span class="text-sm font-bold text-orange-600 bg-orange-50 px-3 py-1 rounded border border-orange-200">
        Las reseñas están deshabilitadas temporalmente.
      </span>
    </div>

    <!-- 2. CASO: HABILITADAS + NO TENGO RESEÑA -->
    <button 
      v-else-if="!siteStore.userReview && !siteStore.userReviewDeleted" 
      class="btn" 
      @click="onWriteReview"
    >
      Escribir reseña
    </button>
    
  </div>

    <div v-if="configStore.reviewsEnabled && siteStore.userReview && !siteStore.userReviewDeleted" 
        class="user-review-container mb-6 rounded-lg border border-gray-300 overflow-hidden">
      <ReviewCard 
        :rating="siteStore.userReview.rating" 
        :comment="siteStore.userReview.comment"
        :date="siteStore.userReview.inserted_at" 
        :alias="siteStore.userReview.alias" 
        :isOwn="true"
        class="!mb-0 shadow-none" 
        @edit="openEditModal"  
        @delete="askConfirmDelete"
      >
              <template #header-info>
                <span v-if="siteStore.userReview.state_id === 1" 
                      class="text-sm text-gray-600 ml-2 font-normal">
                      Pendiente de aprobación
                </span>
                <span v-else-if="siteStore.userReview.state_id === 3" 
                      class="text-sm text-gray-600 ml-2 font-normal">
                      Rechazada
                </span>
                <span v-else-if="siteStore.userReview.state_id === 2" 
                      class="text-sm text-gray-600 ml-2 font-normal">
                      Aprobada
                </span>
              </template>
      </ReviewCard>
    </div>

  <div v-else-if="configStore.reviewsEnabled && siteStore.userReviewDeleted" class="mb-4 text-gray-500">
    Su reseña ha sido eliminada. Solo está permitido una reseña por usuario para cada sitio.
  </div>

      <ReviewList 
  v-if="configStore.reviewsEnabled"
  :reviews="siteStore.reviews.filter(r => r.id !== siteStore.userReview?.id)"
  :loading="siteStore.loading" 
  :totalReviews="siteStore.totalReviews" 
  :page="pagination.pagination.page"
  :limit="pagination.pagination.limit" 

  :emptyMessage="siteStore.userReview 
    ? 'No hay reseñas de otros usuarios aún.' 
    : 'No hay reseñas para este sitio aún.'"
  @page-changed="onPageChanged" 
/>

    </section>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Nueva Reseña</h3>
          
        </div>
        
        <ReviewForm 
          @action="handleCreateAction" 
          @update:form="formData = $event" 
          @cancel="closeCreateModal" 
        />
        </div>
    </div>

    <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
      <div class="modal-content">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Editar mi reseña</h3>
          
        </div>

        <ReviewForm 
          :userReview="siteStore.userReview" 
          @action="handleEditAction" 
          @update:form="formData = $event" 
          @cancel="closeUserModal"
        />
        </div>
    </div>

    <ConfirmPopUp 
      v-if="showConfirm" 
      :title="confirmTitle" 
      :message="confirmMessage" 
      :confirmText="confirmButtonText"
      cancelText="Cancelar" 
      
      :confirmVariant="confirmType === 'delete' ? 'danger' : 'primary'" 
      
      @confirm="onConfirmAction" 
      @cancel="showConfirm = false" 
    />
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSiteDetailStore } from '@/stores/siteDetailStore'
import { useAuthStore } from '@/stores/authStore'
import { useToastStore } from '@/stores/toastStore'
import { usePaginationStore } from '@/stores/paginationStore'
import ImageGallery from '@/components/ImageGallery.vue'
import MapSection from '@/components/MapSection.vue'
import ReviewList from '@/components/ReviewList.vue'
import ReviewForm from '@/components/ReviewForm.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'
import Chip from '@/components/Chip.vue'
import BackButton from '@/components/BackButton.vue'
import ExpandableText from '@/components/ExpandableText.vue'
import ReviewCard from '@/components/ReviewCard.vue'
import ConfirmPopUp from '@/components/ConfirmPopUp.vue'
import { useConfigStore } from '@/stores/configStore'


const route = useRoute()
const router = useRouter()
const siteStore = useSiteDetailStore()
const id = String(route.params.id)
const configStore = useConfigStore()
const pagination = usePaginationStore()
const toast = useToastStore()
const showCreateModal = ref(false)
const showUserModal = ref(false)
const isEditing = ref(false) 
const showConfirm = ref(false)
const confirmType = ref<'delete' | 'edit'>('delete') 
const pendingEditData = ref<any>(null) 
const formData = ref({ puntuacion: '5', texto: '' })

const confirmTitle = computed(() => confirmType.value === 'delete' ? 'Eliminar reseña' : 'Confirmar edición')
const confirmMessage = computed(() => confirmType.value === 'delete' 
  ? '¿Estás seguro de que querés eliminar tu reseña? Solo está permitido una reseña por usuario para cada sitio. Una vez eliminada no podrás escribir una nueva.' 
  : '¿Estás seguro de que querés guardar los cambios en tu reseña? Pasará a estar pendiente de aprobación.')
const confirmButtonText = computed(() => confirmType.value === 'delete' ? 'Eliminar' : 'Guardar')

onMounted(async () => {

  pagination.resetPagination() 
  await siteStore.fetchSite(id)
  await siteStore.fetchUserReview(id)  
  await siteStore.fetchReviews(id, 1)
})

function onWriteReview() {
  const auth = useAuthStore()
  if (!auth.token) {
    auth.loginWithGoogle()
    return
  }
  formData.value = { puntuacion: '5', texto: '' }
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function handleCreateAction(action: string) {
  closeCreateModal()
  if (action === 'submit') {
    const ok = await siteStore.submitReview(id, {
      rating: Number(formData.value.puntuacion),
      text: formData.value.texto
    })
    
    if (ok) {
      
      await siteStore.fetchReviews(id, 1)
      toast.show('Tu reseña ha sido publicada. Quedará pendiente de aprobación.')
    }
  }
}

function closeUserModal() {
  showUserModal.value = false
}

function openEditModal() {
  if (!siteStore.userReview) return

 
  formData.value = {
    puntuacion: String(siteStore.userReview.rating),
    texto: siteStore.userReview.comment
  }
  
  
  showUserModal.value = true
}


function askConfirmDelete() {
  confirmType.value = 'delete'
  showConfirm.value = true
}


function handleEditAction(action: string) {
 
  if (action === 'submit') {
    
    pendingEditData.value = {
      rating: Number(formData.value.puntuacion),
      text: formData.value.texto
    }
    confirmType.value = 'edit'
    showConfirm.value = true
  }
 
}


async function onConfirmAction() {
  closeUserModal()
  showConfirm.value = false
  if (confirmType.value === 'delete') {
    if (!siteStore.userReview) return
    const ok = await siteStore.deleteReview(id, siteStore.userReview.id)
    if (ok) {
 
      await siteStore.fetchReviews(id, 1)
      toast.show('Tu reseña ha sido eliminada.')
    }
  } 
  else if (confirmType.value === 'edit') {
    if (!siteStore.userReview || !pendingEditData.value) return
    const ok = await siteStore.editReview(id, siteStore.userReview.id, pendingEditData.value)
    if (ok) {

      
      await siteStore.fetchReviews(id, 1)
      await siteStore.fetchUserReview(id)
      toast.show('Reseña actualizada con éxito. Quedará pendiente de aprobación.')
    }
  }
}

function onPageChanged(p: number) {
 
 pagination.setPage(p)
 siteStore.fetchReviews(id)
}
</script>

<style scoped>
main {
  max-width: 780px;
  margin: 0 auto;
  padding: 16px;
  margin-top: 70px;
}
header { margin-bottom: 16px; }
header h1 { font-size: 2rem; font-weight: 600; }
.text-muted { color: #727272; }
.btn {
  background: #0078ff;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}
.btn:hover { background: #0064d4; }


.modal-overlay {
  position: fixed;
  inset: 0; 
  background: rgba(0, 0, 0, 0.6); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
  backdrop-filter: blur(3px); 
}

.user-review-container {
  --card-bg: #e2e8f0; 
}

.modal-content {
  background-color: #ffffff; 
  padding: 24px;
  border-radius: 12px; 
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow-y: auto;
}
</style>