<template>
  <AppHeader />
  <main id="app-main">
    <RouterView />
    <ToastContainer />
  </main>
</template>
<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import ToastContainer from './components/ToastContainer.vue'

</script>
<style scoped>
#app-main {
  margin-top: 64px; 
  min-height: calc(100vh - 64px);
  background: var(--color-background-soft);
  padding: 1rem 0;
}
</style>