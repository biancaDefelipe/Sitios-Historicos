<template>
  <div class="overlay" @click.self="$emit('cancel')">
    <div class="popup">

      <h2 class="title">{{ title }}</h2>
      <p class="message">{{ message }}</p>
      <div v-if="note" class="popup-note">{{ note }}</div>

      <div class="actions">
        <BaseButton 
          variant="neutral" 
          @click="$emit('cancel')"
        >
          {{ cancelText }}
        </BaseButton>

        <BaseButton 
          :variant="confirmVariant" 
          @click="$emit('confirm')"
        >
          {{ confirmText }}
        </BaseButton>
      </div>

    </div>
  </div>
</template>

<script setup>
import BaseButton from './BaseButton.vue' 

defineProps({
  title: String,
  message: String,
  note: {
    type: String,
    default: ""
  },
  confirmText: {
    type: String,
    default: "Confirmar"
  },
  cancelText: {
    type: String,
    default: "Cancelar"
  },
  confirmVariant: {
    type: String,
    default: 'primary'
  }
})

defineEmits(["confirm", "cancel"])
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999999;
}

.popup {
  background: #fff;
  padding: 1.5rem;
  width: 90%;
  max-width: 380px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
  animation: fadeIn .15s ease-out;
}

.title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.message {
  margin: 1rem 0 0.5rem 0;
  font-size: 1rem;
  color: #444;
}

.popup-note {
  font-size: 0.95em;
  color: #ad8b00;
  font-weight: bold;
  margin-bottom: 0.7em;
  margin-top: 0.2em;
  text-align: left;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.2rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>