<template>
  <div class="image-gallery">
    <div v-if="images.length === 0" class="text-center py-8 text-gray-400">
      <el-icon :size="40"><Picture /></el-icon>
      <p class="mt-2 text-sm">暂无图片</p>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
      <div
        v-for="(img, idx) in images"
        :key="idx"
        class="relative aspect-[4/3] overflow-hidden rounded-lg cursor-pointer group"
        @click="openViewer(idx)"
      >
        <img
          :src="img.url || img"
          :alt="img.alt || img.title || '图片'"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          loading="lazy"
        />
        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
        <div class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <p v-if="img.title" class="text-white text-xs truncate">{{ img.title }}</p>
        </div>
      </div>
    </div>

    <!-- Image viewer -->
    <teleport to="body">
      <transition name="fade">
        <div
          v-if="viewerOpen"
          class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center"
          @click.self="closeViewer"
        >
          <button
            class="absolute top-4 right-4 text-white/80 hover:text-white z-10"
            @click="closeViewer"
          >
            <el-icon :size="28"><Close /></el-icon>
          </button>

          <button
            v-if="currentIndex > 0"
            class="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white z-10"
            @click="prevImage"
          >
            <el-icon :size="36"><ArrowLeft /></el-icon>
          </button>

          <img
            :src="currentImage"
            :alt="'图片'"
            class="max-w-[90vw] max-h-[85vh] object-contain rounded-lg"
          />

          <button
            v-if="currentIndex < images.length - 1"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white z-10"
            @click="nextImage"
          >
            <el-icon :size="36"><ArrowRight /></el-icon>
          </button>

          <div class="absolute bottom-4 text-white/60 text-sm">
            {{ currentIndex + 1 }} / {{ images.length }}
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
})

const viewerOpen = ref(false)
const currentIndex = ref(0)

const currentImage = computed(() => {
  const img = props.images[currentIndex.value]
  return img?.url || img
})

function openViewer(idx) {
  currentIndex.value = idx
  viewerOpen.value = true
  document.body.style.overflow = 'hidden'
}

function closeViewer() {
  viewerOpen.value = false
  document.body.style.overflow = ''
}

function prevImage() {
  if (currentIndex.value > 0) currentIndex.value--
}

function nextImage() {
  if (currentIndex.value < props.images.length - 1) currentIndex.value++
}
</script>
