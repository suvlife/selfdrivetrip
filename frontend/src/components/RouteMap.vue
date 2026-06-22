<template>
  <div class="route-map relative w-full" :style="{ height: height }">
    <!-- AMap container -->
    <div
      ref="mapContainer"
      class="w-full h-full rounded-xl overflow-hidden"
      :class="{ 'bg-gray-100': !mapLoaded && hasKey }"
    >
      <!-- Loading state -->
      <div v-if="!mapLoaded && hasKey" class="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
        <div class="text-center">
          <el-icon class="is-loading text-primary" :size="40"><Loading /></el-icon>
          <p class="mt-2 text-gray-500 text-sm">地图加载中...</p>
        </div>
      </div>

      <!-- Placeholder when no AMap key -->
      <div v-if="!hasKey" class="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
        <div class="text-center max-w-md px-6">
          <span class="text-6xl">🗺️</span>
          <h3 class="mt-4 text-lg font-bold text-gray-700">地图区域</h3>
          <p class="mt-2 text-gray-500 text-sm">
            {{ routeTitle || '路线地图将在这里展示' }}
          </p>
          <div class="mt-4 bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div class="flex items-center justify-center gap-4 text-sm text-gray-600">
              <span>🚩 {{ departure || '起点' }}</span>
              <span class="text-gray-300">→</span>
              <span>🏁 {{ destination || '终点' }}</span>
            </div>
            <div v-if="totalDistance" class="mt-2 text-center text-sm text-gray-500">
              总里程: {{ totalDistance }} · {{ totalDuration }}
            </div>
          </div>
          <p class="mt-3 text-xs text-gray-400">
            配置 VITE_AMAP_KEY 以启用高德地图
          </p>
        </div>
      </div>
    </div>

    <!-- Day toggle buttons -->
    <div v-if="mapLoaded && hasDays" class="absolute top-4 left-4 z-10 flex flex-wrap gap-2">
      <button
        v-for="(day, idx) in days"
        :key="idx"
        class="px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 shadow-sm"
        :class="activeDay === idx
          ? 'bg-primary text-white shadow-md scale-105'
          : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        @click="toggleDay(idx)"
      >
        第{{ idx + 1 }}天
      </button>
      <button
        v-if="days.length > 1"
        class="px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 shadow-sm"
        :class="activeDay === -1
          ? 'bg-primary text-white shadow-md scale-105'
          : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        @click="toggleDay(-1)"
      >
        全部
      </button>
    </div>

    <!-- Map controls -->
    <div v-if="mapLoaded" class="absolute top-4 right-4 z-10 flex flex-col gap-2">
      <button
        class="w-9 h-9 bg-white rounded-lg shadow-sm flex items-center justify-center hover:bg-gray-50 transition-colors"
        title="放大"
        @click="zoomIn"
      >
        <el-icon><Plus /></el-icon>
      </button>
      <button
        class="w-9 h-9 bg-white rounded-lg shadow-sm flex items-center justify-center hover:bg-gray-50 transition-colors"
        title="缩小"
        @click="zoomOut"
      >
        <el-icon><Minus /></el-icon>
      </button>
      <button
        class="w-9 h-9 bg-white rounded-lg shadow-sm flex items-center justify-center hover:bg-gray-50 transition-colors"
        title="全览"
        @click="fitBounds"
      >
        <el-icon><FullScreen /></el-icon>
      </button>
    </div>

    <!-- POI info window (mobile) -->
    <transition name="slide-up">
      <div
        v-if="selectedPOI && isMobile"
        class="absolute bottom-0 left-0 right-0 z-20 bg-white rounded-t-2xl shadow-2xl max-h-[40vh] overflow-y-auto"
      >
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-bold text-gray-800">{{ selectedPOI.name }}</h3>
            <button class="text-gray-400 hover:text-gray-600" @click="selectedPOI = null">
              <el-icon><Close /></el-icon>
            </button>
          </div>
          <POICard :poi="selectedPOI" :detailed="true" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { hasAMapKey, loadAMap, DAY_COLORS, createMarkerContent,
  createStartMarkerContent, createEndMarkerContent, createInfoWindowContent } from '@/utils/map'
import POICard from './POICard.vue'

const props = defineProps({
  route: { type: Object, default: null },
  height: { type: String, default: '500px' },
  interactive: { type: Boolean, default: true },
})

// Placeholder display
const routeTitle = computed(() => props.route?.title || '')
const departure = computed(() => props.route?.departure || props.route?.start_city || '')
const destination = computed(() => props.route?.destination || props.route?.end_city || '')
const totalDistance = computed(() => props.route?.total_distance || props.route?.distance || '')
const totalDuration = computed(() => props.route?.total_duration || props.route?.duration || '')

const hasKey = hasAMapKey()
const mapContainer = ref(null)
const mapLoaded = ref(false)
let map = null
let polylines = []
let markers = []
let infoWindow = null

const activeDay = ref(-1)
const selectedPOI = ref(null)
const isMobile = ref(false)

const days = computed(() => {
  if (!props.route?.days) return []
  if (Array.isArray(props.route.days)) return props.route.days
  return []
})

const hasDays = computed(() => days.value.length > 0)

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  if (hasKey) {
    initMap()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (map) {
    map.destroy()
    map = null
  }
})

watch(() => props.route, (newRoute) => {
  if (newRoute && mapLoaded.value) {
    nextTick(() => renderRoute(newRoute))
  }
}, { deep: true })

async function initMap() {
  try {
    const AMap = await loadAMap()
    if (!mapContainer.value) return

    map = new AMap.Map(mapContainer.value, {
      zoom: 5,
      center: [104.0, 35.0],
      mapStyle: 'amap://styles/light',
      layers: [new AMap.TileLayer.Satellite()],
      resizeEnable: true,
    })

    mapLoaded.value = true

    if (props.route) {
      nextTick(() => renderRoute(props.route))
    }
  } catch (err) {
    console.error('Map init failed:', err)
  }
}

function renderRoute(route) {
  if (!map || !route) return
  clearMap()

  const AMap = window.AMap
  if (!AMap) return

  const allPoints = []
  const daysData = route.days || []

  daysData.forEach((day, dayIdx) => {
    const segments = day.segments || []
    const color = DAY_COLORS[dayIdx % 5]
    const path = []

    segments.forEach((seg, segIdx) => {
      if (seg.coordinates && seg.coordinates.length >= 2) {
        path.push([seg.coordinates[0], seg.coordinates[1]])
        allPoints.push([seg.coordinates[0], seg.coordinates[1]])
      }
    })

    if (path.length >= 2) {
      const polyline = new AMap.Polyline({
        path,
        strokeColor: color,
        strokeWeight: activeDay.value === -1 || activeDay.value === dayIdx ? 6 : 2,
        strokeOpacity: activeDay.value === -1 || activeDay.value === dayIdx ? 0.9 : 0.2,
        strokeStyle: 'solid',
        lineJoin: 'round',
        lineCap: 'round',
        zIndex: activeDay.value === dayIdx ? 100 : 50,
        extData: { dayIdx },
      })
      polyline.on('click', () => {
        activeDay.value = dayIdx
      })
      polyline.setMap(map)
      polylines.push(polyline)

      // Distance label on middle segment
      if (segments.length > 0) {
        const midSeg = segments[Math.floor(segments.length / 2)]
        if (midSeg.coordinates && midSeg.coordinates.length >= 2) {
          const label = new AMap.Text({
            text: `${midSeg.distance || ''}${midSeg.duration ? ` · ${midSeg.duration}` : ''}`,
            position: [midSeg.coordinates[0], midSeg.coordinates[1]],
            offset: new AMap.Pixel(0, -10),
            style: {
              'background-color': 'rgba(255,255,255,0.9)',
              'border': '1px solid #e8e8e8',
              'border-radius': '4px',
              'padding': '2px 6px',
              'font-size': '11px',
              'color': '#666',
              'white-space': 'nowrap',
            },
          })
          label.setMap(map)
          markers.push(label)
        }
      }
    }

    // Start marker
    if (dayIdx === 0 && segments.length > 0 && segments[0].coordinates) {
      const startMarker = new AMap.Marker({
        position: [segments[0].coordinates[0], segments[0].coordinates[1]],
        content: createStartMarkerContent(),
        offset: new AMap.Pixel(-20, -20),
        zIndex: 200,
      })
      startMarker.setMap(map)
      markers.push(startMarker)
    }

    // End marker
    if (dayIdx === daysData.length - 1 && segments.length > 0) {
      const lastSeg = segments[segments.length - 1]
      if (lastSeg.coordinates) {
        const endMarker = new AMap.Marker({
          position: [lastSeg.coordinates[0], lastSeg.coordinates[1]],
          content: createEndMarkerContent(),
          offset: new AMap.Pixel(-15, -20),
          zIndex: 200,
        })
        endMarker.setMap(map)
        markers.push(endMarker)
      }
    }

    // POI markers
    const pois = day.pois || day.poi || []
    pois.forEach(poi => {
      if (!poi.coordinates && !poi.lng && !poi.lat) return
      const lng = poi.coordinates?.[0] || poi.lng
      const lat = poi.coordinates?.[1] || poi.lat
      if (!lng || !lat) return

      const marker = new AMap.Marker({
        position: [lng, lat],
        content: createMarkerContent(poi),
        offset: new AMap.Pixel(-16, -16),
        zIndex: 150,
        extData: { poi, dayIdx },
      })

      marker.on('click', () => {
        selectedPOI.value = poi
        if (!isMobile.value && infoWindow) {
          infoWindow.setContent(createInfoWindowContent(poi))
          infoWindow.open(map, [lng, lat])
        }
      })

      marker.setMap(map)
      markers.push(marker)
    })
  })

  if (allPoints.length >= 2) {
    map.setFitView(null, false, [40, 40, 40, 40])
  }
}

function clearMap() {
  polylines.forEach(p => p.setMap(null))
  markers.forEach(m => m.setMap(null))
  polylines = []
  markers = []
  if (infoWindow) {
    infoWindow.close()
  }
}

function toggleDay(idx) {
  activeDay.value = activeDay.value === idx ? -1 : idx

  polylines.forEach(poly => {
    const dayIdx = poly.getExtData()?.dayIdx
    if (activeDay.value === -1) {
      poly.setOptions({ strokeWeight: 6, strokeOpacity: 0.9 })
    } else if (dayIdx === activeDay.value) {
      poly.setOptions({ strokeWeight: 8, strokeOpacity: 1, zIndex: 100 })
    } else {
      poly.setOptions({ strokeWeight: 2, strokeOpacity: 0.2, zIndex: 50 })
    }
  })

  if (activeDay.value !== -1 && days.value[activeDay.value]) {
    const day = days.value[activeDay.value]
    const points = []
    ;(day.segments || []).forEach(seg => {
      if (seg.coordinates) points.push([seg.coordinates[0], seg.coordinates[1]])
    })
    const bounds = new window.AMap.Bounds()
    points.forEach(p => bounds.extend(p))
    if (points.length > 0) {
      map.setBounds(bounds, false, [60, 60, 60, 60])
    }
  } else {
    fitBounds()
  }
}

function fitBounds() {
  if (map && polylines.length > 0) {
    map.setFitView(null, false, [40, 40, 40, 40])
  }
}

function zoomIn() {
  if (map) map.zoomIn()
}

function zoomOut() {
  if (map) map.zoomOut()
}
</script>
