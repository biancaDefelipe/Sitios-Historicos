export interface Site {
  id: number | string
  nombre?: string
  name?: string
  short_description: string
  ciudad?: string
  location?: string
  provincia?: string
  calificacion?: number
  imagen?: string
  image?: string
  created_at?: string
  visits?: number
  favorito?: boolean
  type?: string
  tags?: string[]
  lat?: number
  long?: number
}