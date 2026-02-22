<template>
  <div v-if="message" class="feedback-message">{{ message }}</div>
</template>

<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<style scoped>
.feedback-message {
  margin: 1rem 0;
  padding: 0.8rem;
  background: #e6f7ff;
  color: #008B8B;
  border: 1px solid #91d5ff;
  border-radius: 6px;
  text-align: center;
}
</style>