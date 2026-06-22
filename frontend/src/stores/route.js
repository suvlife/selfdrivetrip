import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'

export const useRouteStore = defineStore('route', () => {
  // Form state
  const formState = ref({
    departure: '',
    destination: '',
    month: new Date().getMonth() + 1,
    days: 3,
    tripType: 'round',
    adults: 2,
    children: [],
    carType: 'suv',
    budget: null,
    themes: [],
  })

  // Current route plan
  const currentPlan = ref(null)
  const loading = ref(false)
  const loadingMessage = ref('')
  const error = ref(null)

  // Public routes list
  const publicRoutes = ref([])
  const publicRoutesLoading = ref(false)

  // Computed
  const totalCost = computed(() => {
    if (!currentPlan.value?.costs) return 0
    return Object.values(currentPlan.value.costs).reduce((a, b) => a + b, 0)
  })

  const budgetPercentage = computed(() => {
    if (!formState.value.budget) return null
    return Math.min(100, Math.round((totalCost.value / formState.value.budget) * 100))
  })

  // Form persistence
  function saveToLocalStorage() {
    try {
      localStorage.setItem('selfdrivetrip_form', JSON.stringify(formState.value))
    } catch (e) {
      console.warn('Failed to save form to localStorage:', e)
    }
  }

  function loadFromLocalStorage() {
    try {
      const saved = localStorage.getItem('selfdrivetrip_form')
      if (saved) {
        const parsed = JSON.parse(saved)
        formState.value = { ...formState.value, ...parsed }
      }
    } catch (e) {
      console.warn('Failed to load form from localStorage:', e)
    }
  }

  // Auto-save on change
  function updateFormField(field, value) {
    formState.value[field] = value
    saveToLocalStorage()
  }

  // Generate route plan
  async function generatePlan() {
    loading.value = true
    loadingMessage.value = '正在分析路线'
    error.value = null
    try {
      const payload = {
        departure: formState.value.departure,
        destination: formState.value.destination,
        month: formState.value.month,
        days: formState.value.days,
        trip_type: formState.value.tripType,
        adults: formState.value.adults,
        children: formState.value.children,
        car_type: formState.value.carType,
        budget: formState.value.budget || null,
        themes: formState.value.themes,
      }
      loadingMessage.value = '正在生成行程安排'
      const response = await apiClient.post('/api/generate', payload)
      currentPlan.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '生成失败，请重试'
      throw err
    } finally {
      loading.value = false
      loadingMessage.value = ''
    }
  }

  // Fetch public routes
  async function fetchPublicRoutes(params = {}) {
    publicRoutesLoading.value = true
    try {
      const response = await apiClient.get('/api/routes', { params })
      publicRoutes.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch public routes:', err)
      return []
    } finally {
      publicRoutesLoading.value = false
    }
  }

  // Get route detail
  async function getRouteDetail(id) {
    loading.value = true
    try {
      const response = await apiClient.get(`/api/routes/${id}`)
      currentPlan.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取路线详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create share link
  async function createShare(id) {
    try {
      const response = await apiClient.post(`/api/routes/${id}/share`)
      return response.data
    } catch (err) {
      throw err.response?.data?.detail || '分享失败'
    }
  }

  // Get share page data
  async function getShareData(id) {
    loading.value = true
    try {
      const response = await apiClient.get(`/api/share/${id}`)
      currentPlan.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取分享数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    formState,
    currentPlan,
    loading,
    loadingMessage,
    error,
    publicRoutes,
    publicRoutesLoading,
    totalCost,
    budgetPercentage,
    saveToLocalStorage,
    loadFromLocalStorage,
    updateFormField,
    generatePlan,
    fetchPublicRoutes,
    getRouteDetail,
    createShare,
    getShareData,
  }
})
