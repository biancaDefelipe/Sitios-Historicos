<template>
  <div class="toast-wrapper">
    <TransitionGroup name="toast-fade" tag="div">
      <div 
        v-for="m in toast.messages" 
        :key="m.id"
        class="toast"
      >
        {{ m.text }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToastStore } from '@/stores/toastStore'
const toast = useToastStore()
</script>

<style scoped>
.toast-wrapper {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;

  width: 100%;
  pointer-events: none; 
}

.toast {
  background: #333;
  color: white;
  padding: 12px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
  font-size: 15px;
  opacity: 0.97;

  pointer-events: auto;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, 10px);
}
.toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 10px);
}

</style>
