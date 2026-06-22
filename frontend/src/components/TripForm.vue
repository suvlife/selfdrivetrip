<template>
  <div class="trip-form bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
    <div class="bg-gradient-to-r from-primary to-primary-light px-6 py-4">
      <h2 class="text-white text-lg font-bold flex items-center gap-2">
        <el-icon :size="20"><EditPen /></el-icon>
        规划你的自驾之旅
      </h2>
      <p class="text-white/80 text-sm mt-1">AI 智能生成专属路线</p>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="p-6 space-y-4"
      @submit.prevent="handleSubmit"
    >
      <!-- Departure & Destination -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <el-form-item label="起点城市" prop="departure">
          <el-autocomplete
            v-model="form.departure"
            :fetch-suggestions="searchCities"
            :trigger-on-focus="false"
            placeholder="例如：北京"
            clearable
            class="w-full"
            @select="onSelectDeparture"
          >
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
          </el-autocomplete>
        </el-form-item>

        <el-form-item label="目标城市/区域" prop="destination">
          <el-autocomplete
            v-model="form.destination"
            :fetch-suggestions="searchCities"
            :trigger-on-focus="false"
            placeholder="例如：成都"
            clearable
            class="w-full"
            @select="onSelectDestination"
          >
            <template #prefix>
              <el-icon><Aim /></el-icon>
            </template>
          </el-autocomplete>
        </el-form-item>
      </div>

      <!-- Month & Days -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <el-form-item label="出行月份" prop="month">
          <el-select v-model="form.month" placeholder="选择月份" class="w-full">
            <el-option v-for="m in 12" :key="m" :label="m + '月'" :value="m" />
          </el-select>
        </el-form-item>

        <el-form-item label="出行天数" prop="days">
          <el-input-number
            v-model="form.days"
            :min="1"
            :max="30"
            class="w-full"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="行程类型" prop="tripType">
          <el-select v-model="form.tripType" class="w-full">
            <el-option label="往返" value="round" />
            <el-option label="单程" value="oneway" />
          </el-select>
        </el-form-item>
      </div>

      <!-- People -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <el-form-item label="成人" prop="adults">
          <el-input-number
            v-model="form.adults"
            :min="1"
            :max="10"
            class="w-full"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="儿童">
          <div class="flex items-center gap-2 w-full">
            <el-input-number
              v-model="childCount"
              :min="0"
              :max="5"
              class="flex-1"
              controls-position="right"
            />
          </div>
        </el-form-item>
      </div>

      <!-- Children ages -->
      <div v-if="childCount > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        <div v-for="i in childCountArray" :key="i" class="flex items-center gap-1">
          <span class="text-xs text-gray-500 whitespace-nowrap">儿童{{ i }}:</span>
          <el-input-number
            :model-value="form.children[i - 1]"
            :min="0"
            :max="17"
            size="small"
            class="flex-1"
            controls-position="right"
            @update:model-value="onChildAgeChange(i - 1, $event)"
          />
        </div>
      </div>

      <!-- Car Type -->
      <el-form-item label="车型" prop="carType">
        <el-radio-group v-model="form.carType" class="flex flex-wrap gap-2">
          <el-radio-button value="sedan">轿车</el-radio-button>
          <el-radio-button value="suv">SUV</el-radio-button>
          <el-radio-button value="offroad">越野车</el-radio-button>
          <el-radio-button value="mpv">MPV</el-radio-button>
          <el-radio-button value="ev">电动车</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- Themes -->
      <el-form-item label="主题偏好" prop="themes">
        <el-checkbox-group v-model="form.themes" class="flex flex-wrap gap-2">
          <el-checkbox value="family" border>&#x1F468;&#x200D;&#x1F469;&#x200D;&#x1F467;&#x200D;&#x1F466; 亲子</el-checkbox>
          <el-checkbox value="couple" border>&#x1F491; 情侣</el-checkbox>
          <el-checkbox value="photography" border>&#x1F4F8; 摄影</el-checkbox>
          <el-checkbox value="food" border>&#x1F35C; 美食</el-checkbox>
          <el-checkbox value="nature" border>&#x26F0;&#xFE0F; 山水</el-checkbox>
          <el-checkbox value="offroad" border>&#x1F699; 越野</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <!-- Budget -->
      <el-form-item label="预算上限（可选）" prop="budget">
        <el-input
          v-model="form.budget"
          placeholder="例如：5000"
          class="w-full sm:w-64"
          clearable
        >
          <template #prefix>&#165;</template>
        </el-input>
      </el-form-item>

      <!-- Submit -->
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          class="w-full h-12 text-base font-bold"
          :loading="store.loading"
          @click="handleSubmit"
        >
          <template v-if="!store.loading">
            <el-icon class="mr-1"><MagicStick /></el-icon>
            开始规划
          </template>
          <template v-else>
            <span>{{ store.loadingMessage || '正在规划' }}<span class="dots"><span>.</span><span>.</span><span>.</span></span></span>
          </template>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useRouteStore } from '@/stores/route'
import { api } from '@/api'

const router = useRouter()
const store = useRouteStore()
const formRef = ref(null)

const form = reactive({
  departure: store.formState.departure,
  destination: store.formState.destination,
  month: store.formState.month,
  days: store.formState.days,
  tripType: store.formState.tripType,
  adults: store.formState.adults,
  children: store.formState.children.length > 0 ? [...store.formState.children] : [],
  carType: store.formState.carType,
  budget: store.formState.budget,
  themes: [...store.formState.themes],
})

const childCount = ref(form.children.length)

const childCountArray = computed(() => {
  const len = childCount.value
  return Array.from({ length: len }, (_, i) => i + 1)
})

watch(childCount, (newVal, oldVal) => {
  if (newVal > oldVal) {
    for (let i = oldVal; i < newVal; i++) {
      form.children.push(6)
    }
  } else {
    form.children.splice(newVal)
  }
})

function onChildAgeChange(index, value) {
  form.children[index] = value
}

// Validation rules
const rules = {
  departure: [{ required: true, message: '请输入起点城市', trigger: 'blur' }],
  destination: [{ required: true, message: '请输入目标城市', trigger: 'blur' }],
  month: [{ required: true, message: '请选择月份', trigger: 'change' }],
  days: [{ required: true, message: '请输入天数', trigger: 'blur' }],
  carType: [{ required: true, message: '请选择车型', trigger: 'change' }],
}

// Search cities with debounce
let searchTimer = null
async function searchCities(query, cb) {
  if (!query || query.length < 1) {
    cb([])
    return
  }
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    try {
      const res = await api.searchCities(query)
      const cities = (res.data || []).map(c => ({ value: c.name || c }))
      cb(cities)
    } catch {
      cb([])
    }
  }, 300)
}

function onSelectDeparture(item) {
  form.departure = item.value
  store.saveToLocalStorage()
}

function onSelectDestination(item) {
  form.destination = item.value
  store.saveToLocalStorage()
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // Sync to store
  Object.keys(form).forEach(key => {
    store.updateFormField(key, form[key])
  })

  try {
    await store.generatePlan()
    router.push('/plan')
  } catch (err) {
    ElMessage.error(err.message || '规划生成失败，请重试')
  }
}
</script>

<style scoped>
.dots span {
  animation: dotPulse 1.4s infinite;
}
.dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.dots span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}
</style>
