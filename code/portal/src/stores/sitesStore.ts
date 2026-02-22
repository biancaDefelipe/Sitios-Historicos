import { defineStore } from "pinia"
import type { Site } from "../types/site"
import { useAuthStore } from './authStore'
import { usePaginationStore } from "./paginationStore"

import api from "@/services/httpInterceptor"
import { ref } from "vue"



export const useSitesStore = defineStore("sites", {
  state: () => ({

    topRanked: [] as Site[],
    latest: [] as Site[],

    provinces: [] as string[],
    tagsList: [] as string[],

    sites: [] as Site[],
    loading: false,
    error: null as string | null,

    lastSearch: {} as Record<string, any>,

    filters: {
      q: "",
      city: "",
      province: "",
      tags: [] as string[],
      favorites: false,
      order_by: "latest",
      map: {
        lat: null as number | null,
        long: null as number | null,
        radius: null as number | null,
      }
    },


  }),

  getters: {
    isDirty(state) {
      const f = state.filters
      const mapDirty =
        f.map.lat !== null ||
        f.map.long !== null ||
        f.map.radius !== null

      return (
        !!f.q ||
        !!f.city ||
        !!f.province ||
        f.tags.length > 0 ||
        f.favorites ||
        f.order_by !== "latest" ||
        mapDirty
      )
    }
  },

  actions: {
    async fetchAllSites() {
      this.loading = true
      this.error = null
      const auth = useAuthStore()
      const pagination = usePaginationStore()

      const authToken = auth.token || null

      try {
        const params: any={}

        if (this.filters.q){
          params.name =this.filters.q
          params.description=this.filters.q
        }
        
        if (this.filters.city) params.city = this.filters.city
        if (this.filters.province) params.province = this.filters.province

        if (this.filters.tags.length)
            params.tags= this.filters.tags.join(",")
        
        params.order_by = this.filters.order_by

        if (this.filters.favorites)
          params.favorites= this.filters.favorites

        const { lat, long, radius } = this.filters.map
        if (lat &&long && radius){
          params.lat = lat
          params.long = long
          params.radius = radius / 1000
        }


        params.page = pagination.pagination.page
        params.per_page = pagination.pagination.limit

        
        const response = await api.get("/sites/", {
          params, 
          headers: authToken
            ? {Authorization: `Bearer ${authToken}` }
            : {}
        })
        const json = response.data


        this.sites = (json.data || []).map((raw: any) => ({
          ...raw,
          nombre: raw.name,
          ciudad: raw.city,
          provincia: raw.province,
          calificacion: raw.rank,
          imagen: raw.images?.find((img: any) => img.is_cover)?.public_url || null,
        }))

        const meta = json.meta ?? {}
        pagination.setTotal(meta.total ?? 0)
      } catch (err: any) {
        this.error = err.message ?? "Error desconocido"

      } finally {
        this.loading = false
      }
    },

    async fetchFiltersData() {
      try {

        const [provincesRes, tagsRes] = await Promise.all ([
            api.get("/sites/provinces"), 
            api.get("/sites/tags"),
        ])
        this.provinces = provincesRes.data.provinces || []
        this.tagsList = tagsRes.data.tags || []

      } catch (err) {
        console.error ("error cargando filtros: ", err)
      }
    },
    setMapFilter(value: { lat: number; long: number; radius: number }) {
      const pagination = usePaginationStore()

      this.filters.map.lat = value.lat
      this.filters.map.long = value.long
      this.filters.map.radius = value.radius

      
      pagination.setPage(1)

      this.fetchAllSites().catch(() => {})
    },

    setLastSearch(q: Record<string, any>) {
      this.lastSearch = q
    },

    clearMapFilter() {
      this.filters.map.lat = null
      this.filters.map.long = null
      this.filters.map.radius = null
    },

    resetFilters() {
      const pagination = usePaginationStore()
      this.filters = {
        q: "",
        city: "",
        province: "",
        tags: [],
        favorites: false,
        order_by: "latest",
        map: {
          lat: null,
          long: null,
          radius: null
        }
      }
      pagination.resetPagination()
    },
    async fetchTopRankedSites() {
      this.loading = true
      const pagination = usePaginationStore()
      try {
      
        const response = await api.get("/sites/", {
          params: {
            order_by: "rating-5-1",
            page: pagination.pagination.page,
            per_page: pagination.pagination.limit,
          }
        })

        const json = response.data
        this.topRanked = (json.data || []).map((raw: any) => ({
          ...raw,
          nombre: raw.name,
          ciudad: raw.city,
          provincia: raw.province,
          calificacion: raw.rank,
          imagen:
            raw.images?.find((img: any) => img.is_cover)?.public_url || null,
        }))

        
        pagination.setTotal (json.meta?.total ?? 0)
      } finally {
        this.loading = false
      }
    },
     async fetchLatestSites() {
      this.loading = true
      const pagination = usePaginationStore()

      try {
        const response = await api.get("/sites/", {
          params: {
            order_by: "latest",
            page: pagination.pagination.page,
            per_page: pagination.pagination.limit,
          }
        })

        const json = response.data
        this.latest = (json.data || []).map((raw: any) => ({
          ...raw,
          nombre: raw.name,
          ciudad: raw.city,
          provincia: raw.province,
          calificacion: raw.rank,
          imagen:
            raw.images?.find((img: any) => img.is_cover)?.public_url || null,
        }))

        pagination.setTotal(json.meta?.total ?? 0)
        
      } finally {
        this.loading = false
      }
    }
  }
})