<template>
  <ErrorContent
    icon="🔍"
    title="Página no encontrada"
    description="La página que estás buscando no existe."
    action-label="Ir al inicio"
    :on-action="goHome"
  />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import ErrorContent from '@/components/ErrorContent.vue'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>
