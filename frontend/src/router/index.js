import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'SelfDriveTrip - AI自驾游规划' },
  },
  {
    path: '/plan',
    name: 'Plan',
    component: () => import('@/views/PlanView.vue'),
    meta: { title: '行程规划结果' },
  },
  {
    path: '/route/:id',
    name: 'RouteDetail',
    component: () => import('@/views/RouteDetailView.vue'),
    meta: { title: '路线详情' },
  },
  {
    path: '/share/:id',
    name: 'Share',
    component: () => import('@/views/ShareView.vue'),
    meta: { title: '分享路线' },
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/GalleryView.vue'),
    meta: { title: '公开路线' },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/AboutView.vue'),
    meta: { title: '关于我们' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
