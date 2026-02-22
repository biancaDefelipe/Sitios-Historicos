<template>
  <header class="app-header">
    <nav class="nav">

      <div class="logo" @click="goHome">
        <span class="logo-text">Portal de Sitios Históricos</span>
      </div>

      <template v-if="isLogged && !useConfigStore().maintenanceMode">
        <UserIndicator />

        <ProfileButtons 
          @logout="openLogoutPopup"
          @mi-perfil="goToProfile"
        />
      </template>


      <template v-else-if="!useConfigStore().maintenanceMode">
        <button class="btn-login" @click="auth.loginWithGoogle">
          Iniciar sesión
        </button>
      </template>
    </nav>


  <ConfirmPopUp
    v-if="showLogoutPopup"
    title="Cerrar sesión"
    message="¿Estás segura/o de que querés cerrar sesión?"
    confirmText="Cerrar sesión"
    cancelText="Cancelar"
    @confirm="confirmLogout"
    @cancel="showLogoutPopup = false"
  />
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import UserIndicator from '@/components/UserIndicator.vue'
import ProfileButtons from '@/components/ProfileButtons.vue'
import ConfirmPopUp from '@/components/ConfirmPopUp.vue'
import { useConfigStore } from '@/stores/configStore'
import { useToastStore } from "@/stores/toastStore"
const auth = useAuthStore()
const router = useRouter()
const toast = useToastStore()
const isLogged = computed(() => !!auth.token)
const showLogoutPopup = ref(false)

onMounted(() => auth.loadFromStorage())

function confirmLogout() {
  auth.clearSession()
  showLogoutPopup.value = false
  router.push({ name: 'home' })
}
function goHome() {
  router.push({ name: 'home' })
}

function openLogoutPopup() {
  showLogoutPopup.value = true
}

function goToProfile() {

  if (!auth.token){
    return router.push('/denied')
  } else if (auth.isTokenExpired?.()) {
    auth.clearSession()
    toast.show("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.") 
    return router.push('/denied')
  }else{
      router.push({ name: 'perfil' })
  }
}

</script>

<style scoped>
.app-header {
  background: #fff;
  border-bottom: 1px solid #e3e3e3;
  padding: 0.7rem 1.2rem;
}

.nav {
  display: flex;
  justify-content: space-between;
   align-items: center;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 0.5rem; 
}

.logo-text {
  font-weight: 700;
  font-size: 1.2rem;
  color: #0B2F3A;
  cursor: pointer;
}

.btn-login {
  padding: 0.45rem 1rem;
  background: #008B8B;
  border-radius: 6px;
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.btn-login:hover {
  background: #006666;
}
</style>
