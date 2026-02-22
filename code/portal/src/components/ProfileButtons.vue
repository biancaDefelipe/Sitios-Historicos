<template>
  <div class="profile-buttons">
    <button class="btn btn-ghost" @click="$emit('logout')">Cerrar Sesión</button>
    <button class="btn btn-primary" @click="$emit('mi-perfil')">Mi Perfil</button>
  </div>
</template>

<script setup>
defineEmits(['logout', 'mi-perfil'])
</script>

<style scoped>
.btn { padding: 0.45rem 0.9rem; border-radius: 6px; border: 1px solid transparent; cursor: pointer; font-weight: 600; background: transparent; }
.btn-ghost { color: #0B2F3A; background: transparent; border-color: rgba(11,47,58,0.06); transition: background 0.2s; }
.btn-primary { background: #008B8B; color: #fff; border-color: #008B8B; transition: background 0.2s; }
.btn-ghost:hover { background: #ebebeb; }
.btn-primary:hover { background: #006666; }
.profile-buttons { display: flex; gap: 0.5rem; align-items: end; }
</style>