<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center">
        <!-- Icon -->
        <div class="mb-4">
          <span class="text-6xl animate-bounce">🚗</span>
        </div>

        <!-- Title -->
        <h3 class="text-xl font-bold text-gray-800 mb-2">
          {{ title }}
        </h3>

        <!-- Progress message -->
        <div class="space-y-2">
          <p class="text-gray-500 text-sm flex items-center justify-center gap-1">
            <span>{{ message }}</span>
            <span class="inline-flex gap-0.5">
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-dot-pulse" style="animation-delay: 0s" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-dot-pulse" style="animation-delay: 0.2s" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-dot-pulse" style="animation-delay: 0.4s" />
            </span>
          </p>

          <!-- Streaming text -->
          <div
            v-if="streamText"
            class="bg-gray-50 rounded-lg p-4 text-left max-h-32 overflow-y-auto text-sm text-gray-600 leading-relaxed"
          >
            <p>{{ streamText }}</p>
          </div>

          <!-- Progress bar -->
          <el-progress
            :percentage="progress"
            :stroke-width="6"
            :show-text="false"
            class="!mt-4"
            color="#1677ff"
          />
        </div>

        <!-- Cancel button -->
        <el-button
          class="mt-4"
          text
          size="small"
          @click="$emit('cancel')"
        >
          取消
        </el-button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '正在规划路线' },
  message: { type: String, default: 'AI 正在为你生成最优路线' },
  streamText: { type: String, default: '' },
  progress: { type: Number, default: 0 },
})

defineEmits(['cancel'])
</script>
