<template>
    <button class="favorite-btn"
            @click="toggle"
            :aria-pressed="favorited"
            :title="favorited ? 'Quitar favorito' : 'Marcar como favorito'"
    >
    {{ favorited ? '♥' : '♡' }}
    </button>
</template>


<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSiteDetailStore } from '@/stores/siteDetailStore'
import { useAuthStore } from '@/stores/authStore'
import { useToastStore} from '@/stores/toastStore'

const props = defineProps<{ siteId: string }>()

const favorited = computed(() => siteStore.isFavorite)
const router = useRouter()
const siteStore = useSiteDetailStore()
const authStore = useAuthStore()
const toast = useToastStore()


async function toggle() {
   const token = sessionStorage.getItem("auth.token")
    if (!token) {
        authStore.loginWithGoogle()
        return
    }
   
   const ok = await siteStore.toggleFavorite(props.siteId, token)
    if (ok) {
      if (siteStore.isFavorite){
            toast.show("Sitio agregado a 'favoritos'")
        }else{
          toast.show("Sitio eliminado de 'favoritos'")
        }
    }else{
      toast.show("Error al actualizar favoritos")
    }
   
}
</script>


<style scoped>
.favorite-btn {
  cursor: pointer;
  font-size: 24px;
  color: #e03a3a;
  background: none;
  border: none;
  padding: 0;
  transition: transform .15s;
}

.favorite-btn:hover {
  transform: scale(1.15);
}
</style>