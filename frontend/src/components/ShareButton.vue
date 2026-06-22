<template>
  <div class="share-button inline-flex items-center gap-1">
    <!-- Copy link -->
    <el-tooltip content="复制分享链接" placement="top">
      <el-button
        size="small"
        :type="copied ? 'success' : 'default'"
        :icon="copied ? 'Check' : 'Share'"
        circle
        @click="copyLink"
      />
    </el-tooltip>

    <!-- WeChat -->
    <el-tooltip content="分享到微信" placement="top">
      <el-button size="small" circle @click="shareWeChat">
        <span class="text-sm">💬</span>
      </el-button>
    </el-tooltip>

    <!-- Twitter -->
    <el-tooltip content="分享到 Twitter" placement="top">
      <el-button size="small" circle @click="shareTwitter">
        <span class="text-sm">🐦</span>
      </el-button>
    </el-tooltip>

    <!-- Download print -->
    <el-tooltip content="打印/导出PDF" placement="top">
      <el-button size="small" circle @click="printPage">
        <el-icon><Printer /></el-icon>
      </el-button>
    </el-tooltip>

    <!-- Copied toast -->
    <transition name="fade">
      <span v-if="copied" class="text-xs text-success ml-1">已复制!</span>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  shareId: { type: [String, Number], default: null },
  title: { type: String, default: 'SelfDriveTrip 自驾路线' },
})

const copied = ref(false)

const shareUrl = computed(() => {
  if (!props.shareId) return window.location.href
  const base = window.location.origin
  return `${base}/share/${props.shareId}`
})

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback
    const textarea = document.createElement('textarea')
    textarea.value = shareUrl.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function shareWeChat() {
  // WeChat sharing requires WeChat JS-SDK
  // For now copy the link
  copyLink()
  ElMessage.info('已复制链接，请粘贴到微信发送')
}

function shareTwitter() {
  const text = encodeURIComponent(`推荐路线: ${props.title}`)
  const url = encodeURIComponent(shareUrl.value)
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank')
}

function printPage() {
  window.print()
}
</script>
