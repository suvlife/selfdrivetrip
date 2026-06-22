<template>
  <div class="route-card bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md hover:-translate-y-1">
    <router-link :to="`/route/${route.id}`" class="block">
      <!-- Thumbnail -->
      <div class="h-40 bg-gradient-to-br from-primary/10 to-primary/5 relative overflow-hidden">
        <img
          v-if="route.thumbnail"
          :src="route.thumbnail"
          :alt="route.title"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <span class="text-5xl">🗺️</span>
        </div>
        <!-- Theme badge -->
        <span
          v-if="route.theme"
          class="absolute top-2 right-2 px-2 py-0.5 bg-white/90 rounded-full text-xs font-medium text-primary shadow-sm"
        >
          {{ themeLabel(route.theme) }}
        </span>
        <!-- Day count badge -->
        <span class="absolute top-2 left-2 px-2 py-0.5 bg-white/90 rounded-full text-xs font-medium text-gray-600 shadow-sm">
          {{ route.days }}天
        </span>
      </div>

      <!-- Content -->
      <div class="p-4">
        <h3 class="font-bold text-gray-800 line-clamp-1 mb-2">{{ route.title || '未命名路线' }}</h3>

        <!-- Route -->
        <div class="flex items-center gap-2 text-sm text-gray-600 mb-2">
          <span class="truncate">{{ route.departure || route.start_city }}</span>
          <el-icon class="text-gray-300 flex-shrink-0"><ArrowRight /></el-icon>
          <span class="truncate">{{ route.destination || route.end_city }}</span>
        </div>

        <!-- Meta -->
        <div class="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-50">
          <div class="flex items-center gap-2">
            <span v-if="route.author" class="flex items-center gap-1">
              <el-icon><User /></el-icon> {{ route.author }}
            </span>
            <span v-if="route.views">
              <el-icon><View /></el-icon> {{ route.views }}
            </span>
          </div>
          <span v-if="route.total_cost" class="text-warm font-semibold">
            ¥{{ route.total_cost.toLocaleString() }}
          </span>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script setup>
const props = defineProps({
  route: { type: Object, default: () => ({}) },
})

const themeMap = {
  family: '亲子',
  couple: '情侣',
  photography: '摄影',
  food: '美食',
  nature: '山水',
  offroad: '越野',
}

function themeLabel(theme) {
  if (!theme) return ''
  if (Array.isArray(theme)) {
    return theme.map(t => themeMap[t] || t).join('·')
  }
  return themeMap[theme] || theme
}
</script>
