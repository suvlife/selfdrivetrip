<template>
  <div
    class="poi-card bg-white rounded-lg border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
    @click="$emit('click', poi)"
  >
    <!-- Image -->
    <div v-if="poi.image && detailed" class="h-32 overflow-hidden">
      <img
        :src="poi.image"
        :alt="poi.name"
        class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        loading="lazy"
      />
    </div>

    <div class="p-3">
      <!-- Type badge -->
      <div class="flex items-center justify-between mb-1">
        <span
          class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium"
          :style="{ backgroundColor: typeColor + '20', color: typeColor }"
        >
          {{ typeIcon }} {{ typeLabel }}
        </span>
        <span v-if="poi.rating" class="text-xs text-warm">
          {{ '★'.repeat(Math.round(poi.rating)) }} {{ poi.rating }}
        </span>
      </div>

      <!-- Name -->
      <h4 class="font-semibold text-gray-800 text-sm leading-tight mb-1 line-clamp-2">
        {{ poi.name }}
      </h4>

      <!-- Description -->
      <p v-if="poi.description && !detailed" class="text-xs text-gray-500 line-clamp-2 mb-2">
        {{ poi.description }}
      </p>
      <p v-if="poi.description && detailed" class="text-xs text-gray-500 mb-2">
        {{ poi.description }}
      </p>

      <!-- Meta -->
      <div class="flex flex-wrap items-center gap-2 text-xs text-gray-400">
        <span v-if="poi.price" class="text-warm font-semibold">
          ¥{{ poi.price }}
        </span>
        <span v-if="poi.duration">
          ⏱ {{ poi.duration }}
        </span>
        <span v-if="poi.distance">
          📍 {{ poi.distance }}
        </span>
        <span v-if="poi.address && detailed" class="truncate max-w-[180px]">
          {{ poi.address }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { POI_ICONS, POI_COLORS } from '@/utils/map'

const props = defineProps({
  poi: { type: Object, default: () => ({}) },
  detailed: { type: Boolean, default: false },
})

defineEmits(['click'])

const typeLabels = {
  scenic: '景点',
  restaurant: '餐厅',
  hotel: '酒店',
  gas_station: '加油站',
  parking: '停车场',
  attraction: '景点',
  default: '地点',
}

const typeIcon = computed(() => POI_ICONS[props.poi.type] || POI_ICONS.default)
const typeColor = computed(() => POI_COLORS[props.poi.type] || POI_COLORS.default)
const typeLabel = computed(() => typeLabels[props.poi.type] || typeLabels.default)
</script>
