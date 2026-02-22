<template>
  <form class="review-form" @submit.prevent="() => { emitAction('submit') }">
    <Selector
      label="Puntuación"
      :options="scoreOptions"
      v-model="form.puntuacion"
      placeholder="Selecciona una puntuación"
    />
    <label>
      Texto de la reseña:
      <BaseTextarea
        v-model="form.texto"
        required
        minlength="20"
        maxlength="1000"
        placeholder="Escribe aquí tu reseña (20 a 1000 caracteres)..."
      />
    </label>

    <div class="form-actions">
      <BaseButton
        type="submit"
        variant="primary"
      >
        {{ userReview ? 'Actualizar' : 'Publicar' }}
      </BaseButton>

      <BaseButton
        type="button"
        variant="ghost"
        style="color: #666; border-color: #ccc;" 
        @click="$emit('cancel')"
      >
        Cancelar
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Selector from './Selector.vue'
import BaseButton from './BaseButton.vue'
import BaseTextarea from './BaseTextarea.vue'

const props = defineProps<{
  userReview?: any
}>()

const emit = defineEmits(['action', 'update:form', 'cancel'])

const scoreOptions = [
  { label: '1 ★', value: '1' },
  { label: '2 ★', value: '2' },
  { label: '3 ★', value: '3' },
  { label: '4 ★', value: '4' },
  { label: '5 ★', value: '5' }
]

const form = ref({
  puntuacion: '5',
  texto: ''
})

watch(() => props.userReview, (val) => {
  if (val) {
    form.value.puntuacion = String(val.rating || val.puntuacion || '5')
    form.value.texto = val.comment || val.texto || ''
  } else {
    form.value.puntuacion = '5'
    form.value.texto = ''
  }
}, { immediate: true })

function emitAction(action: 'submit' | 'delete') {
  emit('update:form', { ...form.value })
  emit('action', action)
}
</script>

<style scoped>
.review-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
 
}
.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  flex-wrap: wrap; 
}
</style>