<template>
  <div class="maintenance-container">
    <div class="card">
      <div class="icon">🛠️</div>

      <h1>Sitio en Mantenimiento</h1>

      <p>
        {{ configStore.maintenanceMessage || 'Estamos realizando mejoras para brindarte una mejor experiencia. Vuelve pronto.' }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConfigStore } from '@/stores/configStore'
import { useRouter } from 'vue-router'

const configStore = useConfigStore()
const router = useRouter()

async function checkAgain() {
  await configStore.fetchConfig()
  if (!configStore.maintenanceMode) router.push('/')
}
</script>

<style scoped>

.maintenance-container {

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
</style>
