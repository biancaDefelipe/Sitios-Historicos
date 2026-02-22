<script setup lang="ts">
defineProps<{
  tags: string[]
}>()
</script>

<template>
  <div class="tag-list">
    <!-- Si no hay tags -->
    <span v-if="!tags || tags.length === 0" class="no-tags">-</span>

    <!-- Si hay tags -->
    <span
      v-for="(tag, index) in tags"
      :key="index"
      class="tag-chip"
    >
      {{ tag }}
    </span>
  </div>
</template>

<style scoped>
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.tag-chip {
  background: #e3e8ef;
  padding: 2px 7px;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
}

.no-tags {
  color: #6b7280;
  font-style: italic;
  font-size: 12px;
}
</style>