<template>
  <div class="user-indicator">
    <img v-if="avatar" :src="avatar" alt="Avatar" class="avatar" />
    <span class="name">{{ name }}</span>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/authStore.ts'

const auth = useAuthStore()

const avatar = auth.profile?.picture
const name = auth.profile?.name
</script>

<style scoped>
.user-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}
.name {
  font-weight: 600;
  color: #0B2F3A;
}
</style>
