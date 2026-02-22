<template>
  <section class="perfil-page">
    <div class="profile-header">
      <img
        class="avatar"
        :src="userAvatar"
        alt="Foto de perfil"
      />
      <div>
        <h1 class="name">{{ userName }}</h1>
        <p class="email">{{ userEmail }}</p>
      </div>
    </div>
    <div class="tabs">
      <button
        :class="{ active: activeTab === 'reviews' }"
        @click="activeTab = 'reviews'"
      >
        Mis Reseñas
      </button>

      <button
        :class="{ active: activeTab === 'favoritos' }"
        @click="activeTab = 'favoritos'"
      >
        Mis Favoritos
      </button>
    </div>

    <div v-if="activeTab === 'reviews'" class="content">
      <UserReviewList />
    </div>

    <div v-if="activeTab === 'favoritos'" class="content">
      <UserFavoriteList />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import UserFavoriteList from '@/components/UserFavoriteList.vue'
import UserReviewList from '@/components/UserReviewList.vue'


const activeTab = ref<'reviews' | 'favoritos'>('reviews')

const auth = useAuthStore()

onMounted(() => {
  auth.loadFromStorage()
})

const userName = computed(() => auth.profile?.name || 'Nombre del Usuario')
const userEmail = computed(() => auth.profile?.email || 'usuario@mail.com')
const userAvatar = computed(
  () =>
    auth.profile?.picture ||
    'https://cdn-icons-png.flaticon.com/512/847/847969.png'
)
</script>

<style scoped>

.perfil-page {
  padding: 1rem;
  max-width: 820px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #fff;
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
}

.name {
  font-size: 1.4rem;
  font-weight: bold;
}

.email {
  color: #777;
}

.tabs {
  display: flex;
  margin-top: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
}

.tabs button {
  flex: 1;
  padding: 0.8rem;
  background: #dce7ea;
  color: #0b2f3a;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.tabs button.active {
  background: #0b2f3a;
  color: #f5f5f5;
}

.content {
  margin-top: 1.5rem;
}

.empty {
  color: #777;
  font-style: italic;
}

.item {
  background: #fff;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

</style>
