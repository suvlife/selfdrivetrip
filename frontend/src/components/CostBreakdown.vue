<template>
  <div class="cost-breakdown bg-white rounded-xl border border-gray-100 shadow-sm p-6">
    <!-- Total -->
    <div class="text-center mb-6">
      <p class="text-sm text-gray-500 mb-1">总预算</p>
      <div class="text-3xl font-bold text-warm">
        ¥{{ total.toLocaleString() }}
      </div>
      <div v-if="budget" class="mt-2">
        <el-progress
          :percentage="budgetPct"
          :color="budgetColor"
          :stroke-width="8"
          :show-text="false"
        />
        <p class="text-xs text-gray-400 mt-1">
          预算 {{ budgetPct <= 100 ? '未超' : '超出' }} · 预算上限 ¥{{ budget.toLocaleString() }}
        </p>
      </div>
    </div>

    <!-- Bar chart -->
    <div class="space-y-3">
      <div v-for="item in costItems" :key="item.key" class="cost-row">
        <div class="flex items-center justify-between mb-1">
          <div class="flex items-center gap-2">
            <span class="text-lg">{{ item.icon }}</span>
            <span class="text-sm text-gray-700">{{ item.label }}</span>
          </div>
          <span class="text-sm font-semibold text-gray-800">¥{{ item.amount.toLocaleString() }}</span>
        </div>
        <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :style="{
              width: `${maxAmount > 0 ? (item.amount / maxAmount) * 100 : 0}%`,
              backgroundColor: item.color,
            }"
          />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="costItems.length === 0" class="text-center py-6 text-gray-400 text-sm">
      暂无费用数据
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  costs: { type: Object, default: () => ({}) },
  total: { type: Number, default: 0 },
  budget: { type: Number, default: null },
})

const costConfig = {
  highway: { label: '高速费', icon: '🛣️', color: '#1677ff' },
  fuel: { label: '油费', icon: '⛽', color: '#fa8c16' },
  hotel: { label: '住宿费', icon: '🏨', color: '#722ed1' },
  food: { label: '餐饮费', icon: '🍜', color: '#52c41a' },
  tickets: { label: '门票费', icon: '🎫', color: '#eb2f96' },
  shopping: { label: '购物杂费', icon: '🛍️', color: '#13c2c2' },
}

const costItems = computed(() => {
  return Object.entries(costConfig)
    .filter(([key]) => props.costs[key] !== undefined && props.costs[key] !== null)
    .map(([key, config]) => ({
      key,
      ...config,
      amount: props.costs[key] || 0,
    }))
})

const maxAmount = computed(() => {
  return Math.max(...costItems.value.map(i => i.amount), 1)
})

const budgetPct = computed(() => {
  if (!props.budget) return 0
  return Math.round((props.total / props.budget) * 100)
})

const budgetColor = computed(() => {
  if (budgetPct.value <= 80) return '#52c41a'
  if (budgetPct.value <= 100) return '#fa8c16'
  return '#f5222d'
})
</script>
