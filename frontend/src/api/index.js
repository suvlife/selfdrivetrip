import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for AI generation
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 429) {
        console.warn('Rate limited')
      }
      const message = data?.detail || data?.message || `请求失败 (${status})`
      return Promise.reject(new Error(message))
    }
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('请求超时，请重试'))
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const api = {
  // Generate route plan
  generatePlan(payload) {
    return apiClient.post('/api/generate', payload)
  },

  // List public routes
  getRoutes(params) {
    return apiClient.get('/api/routes', { params })
  },

  // Get route detail
  getRoute(id) {
    return apiClient.get(`/api/routes/${id}`)
  },

  // Share a route
  shareRoute(id) {
    return apiClient.post(`/api/routes/${id}/share`)
  },

  // Get share data
  getShareData(shareId) {
    return apiClient.get(`/api/share/${shareId}`)
  },

  // Get cities for autocomplete
  searchCities(query) {
    return apiClient.get('/api/cities', { params: { q: query } })
  },

  // Get weather for a city
  getWeather(city, date) {
    return apiClient.get('/api/weather', { params: { city, date } })
  },

  // Get articles
  getArticles(params) {
    return apiClient.get('/api/articles', { params })
  },
}

export default api
