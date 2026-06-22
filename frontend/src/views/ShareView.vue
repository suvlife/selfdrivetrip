<template>
  <div class="share-page max-w-5xl mx-auto px-4 sm:px-6 py-6">
    <!-- Loading -->
    <div v-if="store.loading" class="text-center py-20">
      <el-icon class="is-loading text-primary" :size="40"><Loading /></el-icon>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="text-center py-20">
      <el-icon color="#f5222d" :size="48"><WarningFilled /></el-icon>
      <h3 class="mt-4 text-lg font-bold text-gray-700">获取分享数据失败</h3>
      <p class="mt-2 text-gray-500">{{ store.error }}</p>
    </div>

    <!-- Share content -->
    <template v-else-if="store.currentPlan">
      <!-- Header -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 text-xs text-gray-400 mb-2">
              <el-icon><Share /></el-icon>
              分享路线
            </div>
            <h1 class="text-2xl font-bold text-gray-800">
              {{ store.currentPlan.title || '自驾路线' }}
            </h1>
            <div class="flex items-center gap-2 mt-2 text-sm text-gray-500">
              <span>{{ store.currentPlan.departure || store.currentPlan.start_city }}</span>
              <el-icon><ArrowRight /></el-icon>
              <span>{{ store.currentPlan.destination || store.currentPlan.end_city }}</span>
              <span class="mx-2 text-gray-300">|</span>
              <span>{{ store.currentPlan.days || store.currentPlan.days_count }}天</span>
            </div>
          </div>
          <ShareButton
            :share-id="route.params.id"
            :title="store.currentPlan.title"
          />
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">总里程</p>
            <p class="text-lg font-bold text-gray-800">{{ store.currentPlan.total_distance || '-' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">预计用时</p>
            <p class="text-lg font-bold text-gray-800">{{ store.currentPlan.total_duration || '-' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">途经景点</p>
            <p class="text-lg font-bold text-gray-800">{{ poiCount }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">总费用</p>
            <p class="text-lg font-bold text-warm">¥{{ totalCost.toLocaleString() }}</p>
          </div>
        </div>
      </div>

      <!-- Map -->
      <div class="mb-6">
        <RouteMap
          :route="store.currentPlan"
          height="400px"
          :interactive="false"
        />
      </div>

      <!-- Timeline -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
        <h2 class="text-lg font-bold text-gray-800 mb-6">行程安排</h2>
        <DayTimeline :days="store.currentPlan.days || []" />
      </div>

      <!-- Cost -->
      <div class="mb-6">
        <CostBreakdown
          :costs="store.currentPlan.costs || {}"
          :total="totalCost"
        />
      </div>

      <!-- Weather -->
      <div v-if="currentWeather" class="mb-6">
        <WeatherWidget
          :weather="currentWeather"
          :city="store.currentPlan.destination || store.currentPlan.end_city"
        />
      </div>

      <!-- Images -->
      <div v-if="store.currentPlan.images && store.currentPlan.images.length > 0" class="mb-6">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 class="text-lg font-bold text-gray-800 mb-4">沿途风景</h2>
          <ImageGallery :images="store.currentPlan.images" />
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center py-8 text-sm text-gray-400">
        <p>路线由 SelfDriveTrip AI 自动生成</p>
        <p class="mt-1">https://selfdrivetrip.com</p>
      </div>
    </template>

    <!-- Not found -->
    <div v-else class="text-center py-20">
      <span class="text-6xl">🔗</span>
      <h3 class="mt-4 text-lg font-bold text-gray-700">分享链接无效</h3>
      <p class="mt-2 text-gray-500">该分享已过期或不存在</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRouteStore } from '@/stores/route'
import { api } from '@/api'
import RouteMap from '@/components/RouteMap.vue'
import DayTimeline from '@/components/DayTimeline.vue'
import CostBreakdown from '@/components/CostBreakdown.vue'
import WeatherWidget from '@/components/WeatherWidget.vue'
import ImageGallery from '@/components/ImageGallery.vue'
import ShareButton from '@/components/ShareButton.vue'

const route = useRoute()
const store = useRouteStore()
const currentWeather = ref(null)

const totalCost = computed(() => {
  if (!store.currentPlan?.costs) return 0
  return Object.values(store.currentPlan.costs).reduce((a, b) => a + b, 0)
})

const poiCount = computed(() => {
  const days = store.currentPlan?.days || []
  return days.reduce((sum, day) => sum + (day.pois?.length || 0), 0)
})

onMounted(async () => {
  const shareId = route.params.id
  if (shareId) {
    try {
      await store.getShareData(shareId)
      const dest = store.currentPlan?.destination || store.currentPlan?.end_city
      if (dest) {
        try {
          const res = await api.getWeather(dest)
          currentWeather.value = res.data
        } catch {}
      }
    } catch {}
  }
})
</script>

<style>
@media print {
  .share-page {
    padding: 0;
  }
  .share-page .el-button,
  .share-page button {
    display: none !important;
  }
}
</style>
