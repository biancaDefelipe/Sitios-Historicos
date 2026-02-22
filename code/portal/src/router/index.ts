import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SiteSearchView from '../views/SiteSearchView.vue'
import { useConfigStore } from '@/stores/configStore'
import MaintenanceView from '@/views/MaintenanceView.vue'
import AuthCallback from '@/views/AuthCallback.vue'
import  { useAuthStore } from '@/stores/authStore'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/buscar',
      name: 'buscar',
      component: SiteSearchView,
    },
    {
      path: '/perfil',
      name: 'perfil',
      component: () => import('../views/PerfilUsuario.vue'),
    },
    {
      path: '/auth/callback',
      name: 'authCallback',
      component: () => import('../views/AuthCallback.vue')
    }, 
    {
      path: '/sites/:id',
      name: 'SiteDetail',
      component: () => import('@/views/SiteDetailView.vue'),
    },
    {
      path: '/maintenance',
      name: 'Maintenance',
      component: MaintenanceView
    },
    {
      path: '/denied',
      name: 'denied',
      component: () => import('@/views/DeniedView.vue')
    },
    {
      path: '/not-found', 
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue')
    }
  ],
})


router.beforeEach(async (to, from, next) => {
  const configStore = useConfigStore()
  const auth = useAuthStore()
  await configStore.fetchConfig(true)

  if (configStore.maintenanceMode) {
    if (to.path !== '/maintenance' && !to.path.startsWith('/login')) {
      return next({ name: 'Maintenance' })
    }
  }

  if (!configStore.maintenanceMode && to.path === '/maintenance') {
    return next('/')
  }
  
  if (to.path === '/perfil' && auth.isTokenExpired()) {
    return next('/denied')
  }

  if (to.path === '/denied' && !auth.isTokenExpired()) {
    return next('/')
  }
  next()
})
export default router
