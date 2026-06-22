<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-br from-primary/5 via-white to-warm/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <!-- Hero text -->
          <div class="text-center lg:text-left">
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight">
              <span class="text-gradient">AI 自驾游</span>
              <br />
              <span class="text-gray-800">路线规划助手</span>
            </h1>
            <p class="mt-4 text-lg text-gray-500 leading-relaxed">
              输入目的地和偏好，AI 智能生成最优自驾路线<br class="hidden sm:block" />
              包含每日行程、费用估算、景点推荐
            </p>
            <div class="mt-6 flex items-center justify-center lg:justify-start gap-4">
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <el-icon color="#52c41a"><CircleCheckFilled /></el-icon>
                智能规划
              </div>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <el-icon color="#52c41a"><CircleCheckFilled /></el-icon>
                实时路况
              </div>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <el-icon color="#52c41a"><CircleCheckFilled /></el-icon>
                费用预估
              </div>
            </div>
          </div>

          <!-- Hero image -->
          <div class="hidden lg:flex items-center justify-center">
            <div class="relative">
              <div class="w-72 h-72 rounded-full bg-gradient-to-br from-primary/20 to-warm/20 animate-pulse" />
              <span class="absolute inset-0 flex items-center justify-center text-8xl">🚗</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Trip Form Section -->
    <section class="max-w-2xl mx-auto px-4 -mt-8 relative z-10 pb-8">
      <TripForm />
    </section>

    <!-- Features -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 text-center"
        >
          <span class="text-4xl">{{ feature.icon }}</span>
          <h3 class="mt-3 font-bold text-gray-800">{{ feature.title }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{ feature.desc }}</p>
        </div>
      </div>
    </section>

    <!-- Latest Public Routes -->
    <section v-if="store.publicRoutes.length > 0" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
          <el-icon color="#1677ff"><Grid /></el-icon>
          最新公开路线
        </h2>
        <router-link
          to="/gallery"
          class="text-sm text-primary hover:text-primary-light transition-colors flex items-center gap-1"
        >
          查看全部 <el-icon><ArrowRight /></el-icon>
        </router-link>
      </div>

      <!-- Loading skeleton -->
      <div v-if="store.publicRoutesLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-100 overflow-hidden animate-pulse">
          <div class="h-40 bg-gray-200" />
          <div class="p-4 space-y-3">
            <div class="h-4 bg-gray-200 rounded w-3/4" />
            <div class="h-3 bg-gray-200 rounded w-1/2" />
            <div class="h-3 bg-gray-200 rounded w-1/4" />
          </div>
        </div>
      </div>

      <!-- Routes grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <RouteCard
          v-for="route in store.publicRoutes.slice(0, 8)"
          :key="route.id"
          :route="route"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouteStore } from '@/stores/route'
import TripForm from '@/components/TripForm.vue'
import RouteCard from '@/components/RouteCard.vue'

const store = useRouteStore()

const features = [
  { icon: '🧠', title: 'AI 智能规划', desc: '基于深度学习的路线规划算法' },
  { icon: '🗺️', title: '高德地图集成', desc: '实时路况、精准导航' },
  { icon: '💰', title: '费用预估', desc: '油费、过路费、住宿费全面预算' },
  { icon: '📱', title: '一键分享', desc: '生成分享链接，随时随地查看' },
]

onMounted(() => {
  store.fetchPublicRoutes({ limit: 8 })
})
</script>
