import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSitesStore } from './sitesStore'
import api from '@/services/httpInterceptor'
import { usePaginationStore } from './paginationStore'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null) 
  const profile = ref<any | null>(null)
  const loading = ref(false)
  const processingAuth = ref(false)
  const sitesStore = useSitesStore()
  const pagination = usePaginationStore()

  function setSession(payload: { token: string; profile: any }) {
    
    token.value = payload.token
    profile.value = payload.profile
   
    sessionStorage.setItem('auth.token', payload.token)
    sessionStorage.setItem('auth.profile', JSON.stringify(profile.value))
  }

  function loadFromStorage() {
    const t = sessionStorage.getItem('auth.token')
    const p = sessionStorage.getItem('auth.profile')

    token.value = t
    profile.value = p ? JSON.parse(p) : null
  }

  function clearSession() {
    token.value = null
    profile.value = null
    sitesStore.filters.favorites = false
    
    pagination.resetPagination()
    sessionStorage.clear()

  }


  function loginWithGoogle() {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    const redirect = import.meta.env.VITE_GOOGLE_REDIRECT_URI

    const returnTo = window.location.pathname + window.location.search

    sessionStorage.setItem("auth.returnTo", returnTo)

    const url = `https://accounts.google.com/o/oauth2/v2/auth?` +
      new URLSearchParams({
        client_id: clientId,
        redirect_uri: redirect,
        response_type: 'code',
        scope: 'openid email profile',
        access_type: 'offline',
        prompt: 'select_account',
        state: returnTo 
      })

    window.location.href = url
  }

  async function handleGoogleCallback(code: string) {
    loading.value = true
    processingAuth.value = true

    try {
      const response = await api.post("/auth/", {
        provider: "google",
        code
      })

      const data = response.data

      const payload = JSON.parse(atob(data.token.split('.')[1]))
      

     

      setSession({
        token: data.token,
        profile: {
          name: payload.nombre,
          email: payload.email,
          picture: payload.avatar
        }
      })

    } finally {
      loading.value = false
      processingAuth.value = false
    }
  }
  function isTokenExpired() {
    const rawToken = token.value
    if (!rawToken) return true   

    try {
      const parts = rawToken.split('.')
      if (parts.length < 2) return true

      const payloadBase64 = parts[1]
      if (!payloadBase64) return true 

      const payload = JSON.parse(atob(payloadBase64))

      if (!payload.exp) return true

      const now = Date.now()
      const exp = payload.exp * 1000

      return exp < now
    } catch {
      return true
    }
  }



  return {
    token,
    profile,
    loading,
    processingAuth,
    setSession,
    loadFromStorage,
    clearSession,
    loginWithGoogle,
    handleGoogleCallback, 
    isTokenExpired
  }
})
