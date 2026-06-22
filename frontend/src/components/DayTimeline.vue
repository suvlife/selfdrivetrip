<template>
  <div class="day-timeline space-y-4">
    <div
      v-for="(day, dayIdx) in days"
      :key="dayIdx"
      class="relative pl-8"
    >
      <!-- Timeline line -->
      <div
        class="absolute left-[11px] top-6 bottom-0 w-0.5"
        :class="dayIdx === days.length - 1 ? 'bg-gradient-to-b from-gray-200 to-transparent' : 'bg-gray-200'"
      />

      <!-- Timeline dot -->
      <div
        class="absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-sm cursor-pointer transition-transform hover:scale-110"
        :style="{ backgroundColor: dayColor(dayIdx) }"
        @click="expanded[dayIdx] = !expanded[dayIdx]"
      >
        {{ dayIdx + 1 }}
      </div>

      <!-- Day header -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden transition-all duration-300">
        <div
          class="px-4 py-3 flex items-center justify-between cursor-pointer"
          @click="expanded[dayIdx] = !expanded[dayIdx]"
        >
          <div>
            <h3 class="font-bold text-gray-800">
              第{{ dayIdx + 1 }}天
              <span v-if="day.theme" class="ml-2 text-sm font-normal text-primary">· {{ day.theme }}</span>
            </h3>
            <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
              <span v-if="day.distance" class="flex items-center gap-1">
                <el-icon><Aim /></el-icon> {{ day.distance }}
              </span>
              <span v-if="day.total_cost" class="flex items-center gap-1 text-warm">
                <el-icon><Money /></el-icon> ¥{{ day.total_cost }}
              </span>
              <span v-if="day.date" class="flex items-center gap-1">
                <el-icon><Calendar /></el-icon> {{ day.date }}
              </span>
            </div>
          </div>
          <el-icon class="text-gray-400 transition-transform duration-300" :class="{ 'rotate-180': expanded[dayIdx] }">
            <ArrowDown />
          </el-icon>
        </div>

        <!-- Expanded content -->
        <transition name="slide">
          <div v-show="expanded[dayIdx]" class="border-t border-gray-50">
            <!-- Segments -->
            <div v-if="day.segments && day.segments.length > 0" class="px-4 py-3 space-y-3">
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">行程路线</h4>
              <div
                v-for="(seg, segIdx) in day.segments"
                :key="segIdx"
                class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs text-gray-500 flex-shrink-0 mt-0.5">
                  {{ segIdx + 1 }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 text-sm">
                    <span class="font-medium text-gray-700">{{ seg.from }}</span>
                    <span class="text-gray-300">→</span>
                    <span class="font-medium text-gray-700">{{ seg.to }}</span>
                  </div>
                  <div class="flex flex-wrap gap-2 mt-1 text-xs text-gray-500">
                    <span v-if="seg.time">{{ seg.time }}</span>
                    <span v-if="seg.distance" class="text-primary">{{ seg.distance }}</span>
                    <span v-if="seg.duration" class="text-gray-400">{{ seg.duration }}</span>
                    <span v-if="seg.tolls" class="text-warm">过路费 ¥{{ seg.tolls }}</span>
                    <span v-if="seg.fuel" class="text-gray-400">油费 ¥{{ seg.fuel }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- POIs -->
            <div v-if="day.pois && day.pois.length > 0" class="px-4 py-3 border-t border-gray-50">
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">途经景点</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <POICard
                  v-for="(poi, poiIdx) in day.pois"
                  :key="poiIdx"
                  :poi="poi"
                  @click="selectPOI(poi)"
                />
              </div>
            </div>

            <!-- Hotel -->
            <div v-if="day.hotel" class="px-4 py-3 border-t border-gray-50">
              <div
                class="flex items-center justify-between cursor-pointer"
                @click="showHotel[dayIdx] = !showHotel[dayIdx]"
              >
                <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                  <el-icon><HomeFilled /></el-icon> 住宿推荐
                </h4>
                <el-icon class="text-gray-400" :class="{ 'rotate-180': showHotel[dayIdx] }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div v-if="showHotel[dayIdx]" class="mt-2">
                <POICard :poi="day.hotel" :detailed="true" />
              </div>
            </div>

            <!-- Meals -->
            <div v-if="day.meals && day.meals.length > 0" class="px-4 py-3 border-t border-gray-50">
              <div
                class="flex items-center justify-between cursor-pointer"
                @click="showMeals[dayIdx] = !showMeals[dayIdx]"
              >
                <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                  <el-icon><Food /></el-icon> 餐饮推荐
                </h4>
                <el-icon class="text-gray-400" :class="{ 'rotate-180': showMeals[dayIdx] }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div v-if="showMeals[dayIdx]" class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
                <POICard v-for="(meal, mIdx) in day.meals" :key="mIdx" :poi="meal" />
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import POICard from './POICard.vue'
import { DAY_COLORS } from '@/utils/map'

const props = defineProps({
  days: { type: Array, default: () => [] },
})

const emit = defineEmits(['select-poi'])

const expanded = ref({})
const showHotel = ref({})
const showMeals = ref({})

function dayColor(idx) {
  return DAY_COLORS[idx % 5] || '#1677ff'
}

function selectPOI(poi) {
  emit('select-poi', poi)
}
</script>
