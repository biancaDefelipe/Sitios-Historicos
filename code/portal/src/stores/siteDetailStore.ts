import { defineStore } from 'pinia'
import type { Image } from '../types/image'
import { useAuthStore } from './authStore'
import api from '@/services/httpInterceptor'
import { usePaginationStore } from './paginationStore'

export const useSiteDetailStore = defineStore('siteDetailStore', {
  state: () => ({
    site: null as any,
    reviews: [] as any[],
    images: [] as Image[],
    userReview: null as any,
    userReviewDeleted: false,
    totalReviews: 0,
    loading: false,

  isFavorite: false
  }),

  getters: {
    averageRating(state) {
      if (!state.site || !state.site.ratings) return 0
      return state.site.ratings.average || 0
    },

    coverImage(state) {
      const images = state.site?.images || []
      return images.find((img: Image) => img.is_cover) || null
    },

    galleryImages(state) {
      return state.site?.images || []
    }
  },

  actions: {
   async fetchSite(site_id: string) {
    this.loading = true
    try {
      const BASE_URL = import.meta.env.VITE_API_LOCAL

     const { data }= await api.get (`${BASE_URL}/sites/${site_id}`)
     this.site = data

     const rawToken = sessionStorage.getItem("auth.token")
     const token = rawToken ?? undefined
     await this.loadFavoriteStatus(site_id, token)

    } catch (err) {
      console.error('Error al obtener sitio', err)
      this.site = null
    } finally {
      this.loading = false
    }
    },

async fetchUserReview(site_id: string) {
  this.loading = true
  const auth = useAuthStore()
  const authToken = auth.token || null

  if (authToken){  
    try {
      const BASE_URL = import.meta.env.VITE_API_LOCAL

     const { data } = await api.get (
        `${BASE_URL}/sites/${site_id}/reviews/user`, 
        {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        }
     ) 

      if(data){
        if (data.review && !data.deleted) this.userReview = data.review
        else this.userReview = null
        this.userReviewDeleted = data.deleted
      }

    } catch (err) {
      console.error(err)
    } finally {
      this.loading = false
    }
  }
},

async fetchReviews(site_id: string, page = 1) {
  this.loading = true
  const auth = useAuthStore()
  const pagination = usePaginationStore()

  try {
    const BASE_URL = import.meta.env.VITE_API_LOCAL

   const { data } = await api.get (
      `${BASE_URL}/sites/${site_id}/reviews`, 
      {
        params:{
          page: pagination.pagination.page,
          per_page: pagination.pagination.limit
        }
      }
   )
    this.reviews = Array.isArray(data.data) ? data.data : []
    this.totalReviews = data.meta?.total ?? 0

    pagination.setTotal (this.totalReviews)

    
  } catch (err) {
    console.error(err)
  } finally {
    this.loading = false
  }
  },
  changePage(page: number) {
    const pagination = usePaginationStore()
    if (page === pagination.pagination.page) return
    pagination.setPage(page)
    if (this.site) this.fetchReviews(this.site.id)
  },

  async submitReview(site_id: string, payload: { rating: number; text: string }) {
  const auth = useAuthStore()
  const BASE_URL = import.meta.env.VITE_API_LOCAL

  try{
    await api.post (
      `${BASE_URL}/sites/${site_id}/reviews`, 
      {
        rating: payload.rating, 
        comment: payload.text, 
        site_id: Number(site_id)
      }, 
      {
        headers: {
          Authorization: `Bearer ${auth.token}`
        }
      }
    )
        return true
      }catch{
        return false
      }
    },
    
    async toggleFavorite(site_id: string, token?: string) {
      const BASE_URL = import.meta.env.VITE_API_LOCAL
      const isFav = this.isFavorite

      const url = `${BASE_URL}/sites/${site_id}/favorite`

      try{
        await api.request({
          url, 
          method: isFav ? "DELETE" : "PUT", 
          headers: {
            ...(token ? {Authorization:`Bearer ${token}` } : {})
          }
        })
        this.isFavorite = !this.isFavorite
        return true
      }catch{
        return false
      }
    },

    
    async editReview(site_id: string, review_id: number, payload: { rating: number; text: string }) {
  const auth = useAuthStore()
  const BASE_URL = import.meta.env.VITE_API_LOCAL


  try{
    await api.put(
      `${BASE_URL}/sites/${site_id}/reviews/${review_id}`,
      {
        rating: payload.rating, 
        comment: payload.text
      },
      {
        headers: {
          Authorization: `Bearer ${auth.token}`
        }
      }
    )
    return true
  }catch{ 
      return false
  }
},

    async deleteReview(site_id: string, review_id: number) {
      const auth = useAuthStore()
      const BASE_URL = import.meta.env.VITE_API_LOCAL


      try{
        await api.delete(
          `${BASE_URL}/sites/${site_id}/reviews/${review_id}`, 
          {
            headers: {
              Authorization: `Bearer ${auth.token}`
            }
          }
        )
        this.userReview = null
        this.userReviewDeleted= true
        return true
      }catch{
        return false
      }
    },

    async loadFavoriteStatus(site_id: string, token?: string) {
      if (!token) {
        this.isFavorite = false
        return
      }

      const BASE_URL = import.meta.env.VITE_API_LOCAL


     try{
      const { data }= await api.get (`${BASE_URL}/me/site_is_favorite/${site_id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      this.isFavorite = data.site_is_favorite
     }catch{
      this.isFavorite = false
     }
      
    }

  }
})
