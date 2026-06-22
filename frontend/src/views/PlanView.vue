<template>
  <div class="plan-page max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Error state -->
    <div v-if="store.error && !store.currentPlan" class="text-center py-20">
      <el-icon color="#f5222d" :size="48"><WarningFilled /></el-icon>
      <h3 class="mt-4 text-lg font-bold text-gray-700">生成失败</h3>
      <p class="mt-2 text-gray-500">{{ store.error }}</p>
      <el-button type="primary" class="mt-4" @click="$router.push('/')">
        重新规划
      </el-button>
    </div>

    <!-- Loading -->
    <div v-else-if="store.loading" class="py-12">
      <LoadingOverlay
        :visible="true"
        :title="'正在生成路线'"
        :message="store.loadingMessage"
        :stream-text="streamText"
        :progress="progress"
      />
    </div>

    <!-- Route result -->
    <template v-else-if="store.currentPlan">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            {{ store.currentPlan.title || '自驾路线规划' }}
          </h1>
          <div class="flex items-center gap-2 mt-1 text-sm text-gray-500">
            <span>{{ store.currentPlan.departure || store.formState.departure }}</span>
            <el-icon><ArrowRight /></el-icon>
            <span>{{ store.currentPlan.destination || store.formState.destination }}</span>
            <span class="mx-2 text-gray-300">|</span>
            <span>{{ store.formState.days }}天</span>
            <span class="mx-2 text-gray-300">|</span>
            <span v-if="store.currentPlan.total_distance">{{ store.currentPlan.total_distance }}</span>
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

      <!-- Map + Info Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Map -->
        <div class="lg:col-span-2">
          <RouteMap
            :route="store.currentPlan"
            height="500px"
          />
        </div>

        <!-- Side info -->
        <div class="space-y-4">
          <!-- Quick stats -->
          <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">行程概览</h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-blue-50 rounded-lg p-3 text-center">
                <p class="text-xs text-gray-500">总里程</p>
                <p class="text-lg font-bold text-primary">{{ store.currentPlan.total_distance || '-' }}</p>
              </div>
              <div class="bg-orange-50 rounded-lg p-3 text-center">
                <p class="text-xs text-gray-500">预计用时</p>
                <p class="text-lg font-bold text-warm">{{ store.currentPlan.total_duration || '-' }}</p>
              </div>
              <div class="bg-green-50 rounded-lg p-3 text-center">
                <p class="text-xs text-gray-500">途经景点</p>
                <p class="text-lg font-bold text-success">{{ poiCount }}</p>
              </div>
              <div class="bg-purple-50 rounded-lg p-3 text-center">
                <p class="text-xs text-gray-500">总费用</p>
                <p class="text-lg font-bold text-purple-600">¥{{ store.totalCost.toLocaleString() }}</p>
              </div>
            </div>
          </div>

          <!-- Weather -->
          <WeatherWidget
            v-if="currentWeather"
            :weather="currentWeather"
            :city="store.currentPlan.destination || store.formState.destination"
          />

          <!-- Cost -->
          <CostBreakdown
            :costs="store.currentPlan.costs || {}"
            :total="store.totalCost"
            :budget="store.formState.budget ? Number(store.formState.budget) : null"
          />
        </div>
      </div>

      <!-- Day Timeline -->
      <div class="mt-8">
        <h2 class="section-title text-xl mb-6">
          <el-icon color="#1677ff"><Calendar /></el-icon>
          每日行程
        </h2>
        <DayTimeline
          :days="store.currentPlan.days || []"
          @select-poi="handleSelectPOI"
        />
      </div>

      <!-- Images -->
      <div v-if="store.currentPlan.images && store.currentPlan.images.length > 0" class="mt-8">
        <h2 class="section-title text-xl mb-4">
          <el-icon color="#1677ff"><Picture /></el-icon>
          沿途风景
        </h2>
        <ImageGallery :images="store.currentPlan.images" />
      </div>

      <!-- Articles -->
      <div v-if="store.currentPlan.articles && store.currentPlan.articles.length > 0" class="mt-8">
        <h2 class="section-title text-xl mb-4">
          <el-icon color="#1677ff"><Reading /></el-icon>
          相关攻略
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ArticleCard
            v-for="(article, idx) in store.currentPlan.articles"
            :key="idx"
            :article="article"
          />
        </div>
      </div>
    </template>

    <!-- No data -->
    <div v-else class="text-center py-20">
      <span class="text-6xl">🗺️</span>
      <h3 class="mt-4 text-lg font-bold text-gray-700">还没有规划路线</h3>
      <p class="mt-2 text-gray-500">开始你的第一次自驾之旅吧</p>
      <el-button type="primary" class="mt-4" @click="$router.push('/')">
        开始规划
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouteStore } from '@/stores/route'
import RouteMap from '@/components/RouteMap.vue'
import DayTimeline from '@/components/DayTimeline.vue'
import CostBreakdown from '@/components/CostBreakdown.vue'
import WeatherWidget from '@/components/WeatherWidget.vue'
import ImageGallery from '@/components/ImageGallery.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import ShareButton from '@/components/ShareButton.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const store = useRouteStore()
const streamText = ref('')
const progress = ref(0)
const currentWeather = ref(null)

const poiCount = computed(() => {
  const days = store.currentPlan?.days || []
  return days.reduce((sum, day) => sum + (day.pois?.length || 0), 0)
})

function handleSelectPOI(poi) {
  console.log('Selected POI:', poi)
}

onMounted(async () => {
  // Fetch weather for destination if we have a plan
  if (store.currentPlan?.destination) {
    try {
      const { api } = await import('@/api')
      const res = await api.getWeather(store.currentPlan.destination)
      currentWeather.value = res.data
    } catch {
      // Weather is optional
    }
  }
})
</script>
