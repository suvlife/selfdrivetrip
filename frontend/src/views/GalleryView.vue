<template>
  <div class="gallery-page max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">公开路线</h1>
      <p class="mt-1 text-sm text-gray-500">浏览其他用户分享的自驾路线</p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-6">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Theme filter -->
        <el-select
          v-model="filters.theme"
          placeholder="主题"
          clearable
          class="w-32"
          @change="fetchRoutes"
        >
          <el-option label="全部" value="" />
          <el-option v-for="(label, key) in themeMap" :key="key" :label="label" :value="key" />
        </el-select>

        <!-- Departure -->
        <el-input
          v-model="filters.departure"
          placeholder="起点"
          clearable
          class="w-36"
          @clear="fetchRoutes"
          @keyup.enter="fetchRoutes"
        >
          <template #prefix>
            <el-icon><Location /></el-icon>
          </template>
        </el-input>

        <!-- Destination -->
        <el-input
          v-model="filters.destination"
          placeholder="目的地"
          clearable
          class="w-36"
          @clear="fetchRoutes"
          @keyup.enter="fetchRoutes"
        >
          <template #prefix>
            <el-icon><Aim /></el-icon>
          </template>
        </el-input>

        <!-- Sort -->
        <el-select
          v-model="filters.sort"
          class="w-36"
          @change="fetchRoutes"
        >
          <el-option label="最新发布" value="newest" />
          <el-option label="最多浏览" value="views" />
          <el-option label="最长行程" value="days" />
        </el-select>

        <!-- Search button -->
        <el-button type="primary" @click="fetchRoutes">
          <el-icon><Search /></el-icon> 搜索
        </el-button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="bg-white rounded-xl border border-gray-100 overflow-hidden animate-pulse">
        <div class="h-40 bg-gray-200" />
        <div class="p-4 space-y-3">
          <div class="h-4 bg-gray-200 rounded w-3/4" />
          <div class="h-3 bg-gray-200 rounded w-1/2" />
          <div class="h-3 bg-gray-200 rounded w-1/4" />
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="routes.length === 0" class="text-center py-20">
      <span class="text-6xl">🔍</span>
      <h3 class="mt-4 text-lg font-bold text-gray-700">没有找到路线</h3>
      <p class="mt-2 text-gray-500">试试不同的搜索条件</p>
      <el-button type="primary" class="mt-4" @click="resetFilters">重置筛选</el-button>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <RouteCard v-for="route in routes" :key="route.id" :route="route" />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center mt-8">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api'
import RouteCard from '@/components/RouteCard.vue'

const loading = ref(false)
const routes = ref([])
const page = ref(1)
const pageSize = 12
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / pageSize))

const filters = reactive({
  theme: '',
  departure: '',
  destination: '',
  sort: 'newest',
})

const themeMap = {
  family: '亲子',
  couple: '情侣',
  photography: '摄影',
  food: '美食',
  nature: '山水',
  offroad: '越野',
}

async function fetchRoutes() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      limit: pageSize,
      sort: filters.sort,
    }
    if (filters.theme) params.theme = filters.theme
    if (filters.departure) params.departure = filters.departure
    if (filters.destination) params.destination = filters.destination

    const res = await api.getRoutes(params)
    const data = res.data
    routes.value = data.routes || data.results || data || []
    total.value = data.total || routes.value.length
  } catch (err) {
    console.error('Failed to fetch routes:', err)
    routes.value = []
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.theme = ''
  filters.departure = ''
  filters.destination = ''
  filters.sort = 'newest'
  page.value = 1
  fetchRoutes()
}

function onPageChange(newPage) {
  page.value = newPage
  fetchRoutes()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(fetchRoutes)
</script>
