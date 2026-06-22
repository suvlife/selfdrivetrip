<template>
  <div class="route-detail-page max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-20">
      <el-icon class="is-loading text-primary" :size="40"><Loading /></el-icon>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-20">
      <el-icon color="#f5222d" :size="48"><WarningFilled /></el-icon>
      <h3 class="mt-4 text-lg font-bold text-gray-700">加载失败</h3>
      <p class="mt-2 text-gray-500">{{ error }}</p>
      <el-button type="primary" class="mt-4" @click="fetchRoute">
        重试
      </el-button>
    </div>

    <!-- Route detail -->
    <template v-else-if="store.currentPlan">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            {{ store.currentPlan.title || '路线详情' }}
          </h1>
          <div class="flex items-center gap-2 mt-1 text-sm text-gray-500">
            <span>{{ store.currentPlan.departure || store.currentPlan.start_city }}</span>
            <el-icon><ArrowRight /></el-icon>
            <span>{{ store.currentPlan.destination || store.currentPlan.end_city }}</span>
            <span class="mx-2 text-gray-300">|</span>
            <span>{{ store.currentPlan.days || store.currentPlan.days_count }}天</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <ShareButton
            v-if="store.currentPlan.id"
            :share-id="store.currentPlan.id"
            :title="store.currentPlan.title"
          />
        </div>
      </div>

      <!-- Full layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <RouteMap
            :route="store.currentPlan"
            height="500px"
          />
        </div>
        <div class="space-y-4">
          <CostBreakdown
            :costs="store.currentPlan.costs || {}"
            :total="totalCost"
            :budget="null"
          />
          <WeatherWidget
            :weather="currentWeather"
            :city="store.currentPlan.destination || store.currentPlan.end_city"
          />
        </div>
      </div>

      <div class="mt-8">
        <h2 class="section-title text-xl mb-6">每日行程</h2>
        <DayTimeline :days="store.currentPlan.days || []" />
      </div>

      <div v-if="store.currentPlan.images && store.currentPlan.images.length > 0" class="mt-8">
        <h2 class="section-title text-xl mb-4">沿途风景</h2>
        <ImageGallery :images="store.currentPlan.images" />
      </div>
    </template>

    <div v-else class="text-center py-20">
      <span class="text-6xl">🗺️</span>
      <h3 class="mt-4 text-lg font-bold text-gray-700">路线未找到</h3>
      <el-button type="primary" class="mt-4" @click="$router.push('/gallery')">
        浏览公开路线
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRouteStore } from '@/stores/route'
import { api } from '@/api'
import RouteMap from '@/components/RouteMap.vue'
import DayTimeline from '@/components/DayTimeline.vue'
import CostBreakdown from '@/components/CostBreakdown.vue'
import WeatherWidget from '@/components/WeatherWidget.vue'
import ImageGallery from '@/components/ImageGallery.vue'
import ShareButton from '@/components/ShareButton.vue'

const route = useRoute()
const router = useRouter()
const store = useRouteStore()

const loading = ref(false)
const error = ref(null)
const currentWeather = ref(null)

const totalCost = computed(() => {
  if (!store.currentPlan?.costs) return 0
  return Object.values(store.currentPlan.costs).reduce((a, b) => a + b, 0)
})

async function fetchRoute() {
  const id = route.params.id
  if (!id) return

  loading.value = true
  error.value = null
  try {
    await store.getRouteDetail(id)
    // Fetch weather
    const dest = store.currentPlan?.destination || store.currentPlan?.end_city
    if (dest) {
      try {
        const res = await api.getWeather(dest)
        currentWeather.value = res.data
      } catch {}
    }
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchRoute)
</script>
