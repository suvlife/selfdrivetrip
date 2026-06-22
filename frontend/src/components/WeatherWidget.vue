<template>
  <div class="weather-widget bg-white rounded-xl border border-gray-100 shadow-sm p-4">
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-1">
        <el-icon><Sunny /></el-icon> 天气
      </h4>
      <span v-if="city" class="text-xs text-gray-400">{{ city }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-4">
      <el-icon class="is-loading text-gray-400" :size="24"><Loading /></el-icon>
    </div>

    <!-- Weather data -->
    <div v-else-if="weather" class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-3xl">{{ weatherIcon }}</span>
          <div>
            <span class="text-2xl font-bold text-gray-800">{{ weather.temp }}°C</span>
            <span class="text-sm text-gray-500 ml-2">{{ weather.condition }}</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 text-center text-xs">
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-gray-400">风速</p>
          <p class="font-medium text-gray-700">{{ weather.wind || '-' }}</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-gray-400">湿度</p>
          <p class="font-medium text-gray-700">{{ weather.humidity || '-' }}</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-gray-400">降水</p>
          <p class="font-medium text-gray-700">{{ weather.precipitation || '-' }}</p>
        </div>
      </div>

      <!-- Forecast -->
      <div v-if="weather.forecast && weather.forecast.length > 0">
        <p class="text-xs text-gray-500 mb-2">未来预报</p>
        <div class="flex gap-2 overflow-x-auto scrollbar-hide">
          <div
            v-for="(f, idx) in weather.forecast"
            :key="idx"
            class="flex-shrink-0 text-center p-2 bg-gray-50 rounded-lg min-w-[60px]"
          >
            <p class="text-xs text-gray-500">{{ f.date || f.day }}</p>
            <span class="text-lg">{{ forecastIcon(f.condition) }}</span>
            <p class="text-xs font-medium">{{ f.temp }}°</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-4 text-gray-400 text-sm">
      <el-icon :size="32"><Cloudy /></el-icon>
      <p class="mt-1">暂无天气数据</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  weather: { type: Object, default: null },
  city: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const weatherIcon = computed(() => {
  if (!props.weather) return '🌤️'
  const cond = (props.weather.condition || '').toLowerCase()
  if (cond.includes('晴') || cond.includes('sun')) return '☀️'
  if (cond.includes('多云') || cond.includes('cloud')) return '⛅'
  if (cond.includes('阴') || cond.includes('overcast')) return '☁️'
  if (cond.includes('雨') || cond.includes('rain')) return '🌧️'
  if (cond.includes('雪') || cond.includes('snow')) return '❄️'
  if (cond.includes('雾') || cond.includes('fog')) return '🌫️'
  return '🌤️'
})

function forecastIcon(condition) {
  if (!condition) return '🌤️'
  const c = condition.toLowerCase()
  if (c.includes('晴') || c.includes('sun')) return '☀️'
  if (c.includes('云') || c.includes('cloud')) return '⛅'
  if (c.includes('雨') || c.includes('rain')) return '🌧️'
  if (c.includes('雪') || c.includes('snow')) return '❄️'
  return '🌤️'
}
</script>
