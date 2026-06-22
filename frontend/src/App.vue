<template>
  <div id="app-root" class="min-h-screen flex flex-col">
    <HeaderNav />
    <main class="flex-1">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    <footer class="bg-white border-t border-gray-100 py-6 text-center text-sm text-gray-400">
      <div class="max-w-7xl mx-auto px-4">
        <p>SelfDriveTrip © {{ new Date().getFullYear() }} - AI 自驾游路线规划</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import HeaderNav from '@/components/HeaderNav.vue'
import { onMounted } from 'vue'
import { useRouteStore } from '@/stores/route'

const routeStore = useRouteStore()

onMounted(() => {
  routeStore.loadFromLocalStorage()
})
</script>
