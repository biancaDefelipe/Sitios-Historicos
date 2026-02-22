<template>
  <div class="expandable">
   
    <p class="short" v-html="shortHtml"></p>

    <p
      v-if="hasFullText"
      class="complete"
      v-html="expanded ? fullHtml : truncatedHtml"
    ></p>

    <button
      v-if="hasFullText && isTruncated"
      @click="toggle"
      class="toggle-btn"
    >
      {{ expanded ? 'Ver menos' : 'Ver más' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  text?: string
  fullText?: string
}>()

const expanded = ref(false)
function toggle() { expanded.value = !expanded.value }


const shortHtml = computed(() => props.text || '')

const hasFullText = computed(() => Boolean(props.fullText && props.fullText.length > 0))
const fullHtml = computed(() => props.fullText || '')


const MAX_CHARS = 150


const truncatedHtml = computed(() => {
  if (!props.fullText) return ""
  if (props.fullText.length <= MAX_CHARS) return props.fullText
  return props.fullText.substring(0, MAX_CHARS) + "..."
})

const isTruncated = computed(() => {
  return props.fullText && props.fullText.length > MAX_CHARS
})
</script>

<style scoped>
.expandable {
  line-height: 1.6;
  color: #444;
}

.short {
  margin-bottom: 10px;
  font-weight: 500;
}

.complete {
  margin-bottom: 6px;
}

.short,
.complete {
  white-space: pre-line;
  word-break: break-word;
}

.toggle-btn {
  background: none;
  border: none;
  color: #0078ff;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
</style>