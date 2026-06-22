<template>
  <header class="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 group">
          <span class="text-2xl">🚗</span>
          <span class="text-xl font-bold text-gradient">SelfDriveTrip</span>
        </router-link>

        <!-- Desktop Nav -->
        <nav class="hidden md:flex items-center gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            :class="isActive(item.path)
              ? 'bg-primary/10 text-primary'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
          >
            <el-icon class="mr-1">{{ item.icon }}</el-icon>
            {{ item.label }}
          </router-link>
          <el-button type="primary" size="small" class="ml-2" @click="$router.push('/')">
            <el-icon class="mr-1"><MagicStick /></el-icon>
            开始规划
          </el-button>
        </nav>

        <!-- Mobile menu button -->
        <button
          class="md:hidden p-2 rounded-lg hover:bg-gray-100"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <el-icon :size="22">
            <Menu v-if="!mobileMenuOpen" />
            <Close v-else />
          </el-icon>
        </button>
      </div>
    </div>

    <!-- Mobile Nav -->
    <transition name="slide">
      <div v-if="mobileMenuOpen" class="md:hidden bg-white border-t border-gray-100">
        <div class="px-4 py-3 space-y-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium"
            :class="isActive(item.path)
              ? 'bg-primary/10 text-primary'
              : 'text-gray-600 hover:bg-gray-50'"
            @click="mobileMenuOpen = false"
          >
            <el-icon>{{ item.icon }}</el-icon>
            {{ item.label }}
          </router-link>
          <el-button
            type="primary"
            class="w-full mt-2"
            @click="mobileMenuOpen = false; $router.push('/')"
          >
            <el-icon class="mr-1"><MagicStick /></el-icon>
            开始规划
          </el-button>
        </div>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/', label: '首页', icon: 'HomeFilled' },
  { path: '/gallery', label: '公开路线', icon: 'Grid' },
  { path: '/about', label: '关于', icon: 'InfoFilled' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
