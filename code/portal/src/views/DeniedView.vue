<template>
  <ErrorContent
    icon="🚫"
    title="Acceso denegado"
    description="Lo sentimos, debes iniciar sesión para acceder a esta página."
    action-label="Iniciar sesión"
    :on-action="goToLogin"
  />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import ErrorContent from '@/components/ErrorContent.vue'

const router = useRouter()

function goToLogin() {
  router.push('/login')
}
</script>
