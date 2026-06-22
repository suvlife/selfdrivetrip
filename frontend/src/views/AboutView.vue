<template>
  <div class="about-page max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero -->
    <div class="text-center mb-12">
      <span class="text-6xl">🚗</span>
      <h1 class="text-3xl font-bold text-gray-800 mt-4">关于 SelfDriveTrip</h1>
      <p class="mt-2 text-gray-500 text-lg">AI 驱动的智能自驾游路线规划工具</p>
    </div>

    <!-- Content -->
    <div class="space-y-8">
      <!-- What -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-3">这是什么？</h2>
        <p class="text-gray-600 leading-relaxed">
          SelfDriveTrip 是一款基于人工智能的自驾游路线规划工具。只需要输入出发地、目的地、出行天数和偏好，
          AI 会自动为你生成完整的行程规划，包括每日路线、景点推荐、住宿建议、费用估算等。
        </p>
      </div>

      <!-- Features -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">主要功能</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-for="feature in features" :key="feature.title" class="flex items-start gap-3">
            <span class="text-2xl flex-shrink-0">{{ feature.icon }}</span>
            <div>
              <h3 class="font-semibold text-gray-800">{{ feature.title }}</h3>
              <p class="text-sm text-gray-500">{{ feature.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- How to use -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">如何使用</h2>
        <div class="space-y-4">
          <div v-for="(step, idx) in steps" :key="idx" class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
              {{ idx + 1 }}
            </div>
            <div>
              <h3 class="font-semibold text-gray-800">{{ step.title }}</h3>
              <p class="text-sm text-gray-500">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tech -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">技术栈</h2>
        <div class="flex flex-wrap gap-2">
          <span v-for="tech in techStack" :key="tech"
            class="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600">
            {{ tech }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const features = [
  { icon: '🧠', title: 'AI 路线规划', desc: '基于深度学习的智能路线生成算法' },
  { icon: '🗺️', title: '高德地图集成', desc: '实时路况、精准导航、POI 查询' },
  { icon: '💰', title: '费用估算', desc: '油费、过路费、住宿费全面预算' },
  { icon: '🌤️', title: '天气信息', desc: '沿途城市天气预报和提醒' },
  { icon: '📸', title: '图片展示', desc: '景点图片画廊和浏览' },
  { icon: '🔗', title: '一键分享', desc: '生成分享链接，方便朋友查看' },
]

const steps = [
  { title: '输入基本信息', desc: '填写出发地、目的地、出行天数、人数等' },
  { title: '选择偏好', desc: '选择车型、主题偏好、预算上限等' },
  { title: 'AI 智能生成', desc: '系统自动生成完整的行程规划' },
  { title: '查看和调整', desc: '在地图上查看路线，浏览每日行程详情' },
  { title: '分享行程', desc: '生成分享链接，与朋友家人共享' },
]

const techStack = [
  'Vue 3', 'Vite', 'Element Plus', 'Tailwind CSS', 'Pinia', 'Axios',
  '高德地图 JSAPI 2.0', 'Node.js', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker',
]
</script>
