<template>
  <div class="denied-container">
    <div class="card">
      <div class="icon">{{ icon }}</div>

      <h1>{{ title }}</h1>

      <p>{{ description }}</p>

      <button
        v-if="actionLabel"
        class="btn"
        @click="onAction"
      >
        {{ actionLabel }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}>()
</script>

<style scoped>
.denied-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  max-width: 450px;
  width: 90%;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
  border: 1px solid #e5e7eb;
}

.icon {
  font-size: 60px;
  margin-bottom: 20px;
}

h1 {
  font-size: 28px;
  margin-bottom: 15px;
  font-weight: bold;
  color: #111827;
}

p {
  font-size: 18px;
  color: #6b7280;
  line-height: 1.5;
}

.btn {
  margin-top: 20px;
  background: #2563eb;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}

.btn:hover {
  background: #1e40af;
}
</style>
