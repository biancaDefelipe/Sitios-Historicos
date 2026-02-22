import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const messages = ref<Array<{ id: number; text: string }>>([])

  function show(text: string, duration = 2500) {
    if (messages.value.some(m => m.text === text)) {
      return
    }
    
    const id = Date.now()
    messages.value.push({ id, text })

    setTimeout(() => {
      messages.value = messages.value.filter(m => m.id !== id)
    }, duration)
  }

  return { messages, show }
})
