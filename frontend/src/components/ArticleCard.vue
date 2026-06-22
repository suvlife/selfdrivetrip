<template>
  <a
    :href="article.url"
    target="_blank"
    rel="noopener noreferrer"
    class="article-card block bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md hover:-translate-y-1"
  >
    <!-- Image -->
    <div v-if="article.image" class="h-36 overflow-hidden">
      <img
        :src="article.image"
        :alt="article.title"
        class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        loading="lazy"
      />
    </div>

    <div class="p-4">
      <!-- Source badge -->
      <span class="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full font-medium">
        {{ article.source || '推荐' }}
      </span>

      <!-- Title -->
      <h3 class="font-bold text-gray-800 line-clamp-2 mt-2 mb-1 leading-snug">
        {{ article.title }}
      </h3>

      <!-- Summary -->
      <p v-if="article.summary" class="text-xs text-gray-500 line-clamp-2 mb-3">
        {{ article.summary }}
      </p>

      <!-- Meta -->
      <div class="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-50">
        <span>{{ article.author || '未知作者' }}</span>
        <span class="flex items-center gap-1">
          <el-icon><Clock /></el-icon>
          {{ article.date || article.created_at || '' }}
        </span>
      </div>
    </div>
  </a>
</template>

<script setup>
const props = defineProps({
  article: { type: Object, default: () => ({}) },
})
</script>
