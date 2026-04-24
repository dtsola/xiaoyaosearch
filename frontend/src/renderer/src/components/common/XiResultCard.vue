<template>
  <div class="result-card" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <!-- 卡片头部 -->
    <div class="result-header">
      <XiIcon :icon="fileIcon" :size="24" class="result-icon" />
      <div class="result-info">
        <h3 class="result-title">{{ result.title }}</h3>
        <div class="result-meta">
          <span class="badge">匹配度 {{ result.score }}%</span>
          <span class="result-size">{{ result.size }}</span>
        </div>
      </div>
    </div>

    <!-- 卡片预览 -->
    <div class="result-preview">
      <p class="preview-text">{{ result.preview }}</p>
      <p class="preview-path">{{ result.path }}</p>
    </div>

    <!-- 操作按钮 -->
    <div class="result-actions">
      <button class="action-link" @click="$emit('preview')">
        <XiIcon icon="lucide:eye" :size="16" />
        预览
      </button>
      <button class="action-link" @click="$emit('open')">
        <XiIcon icon="lucide:external-link" :size="16" />
        打开
      </button>
      <button class="action-link" @click="$emit('favorite')">
        <XiIcon icon="lucide:star" :size="16" />
        收藏
      </button>
      <button class="action-link" @click="$emit('copy')">
        <XiIcon icon="lucide:copy" :size="16" />
        复制
      </button>
      <button class="action-link danger" @click="$emit('delete')">
        <XiIcon icon="lucide:trash-2" :size="16" />
        删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import XiIcon from './XiIcon.vue'

/**
 * 搜索结果接口
 */
interface Result {
  title: string
  score: number
  size: string
  preview: string
  path: string
  type: 'audio' | 'document' | 'video' | 'image' | 'other'
}

const props = defineProps<{
  result: Result
}>()

defineEmits<{
  preview: []
  open: []
  favorite: []
  copy: []
  delete: []
}>()

const isHovered = ref(false)

/**
 * 根据文件类型获取图标
 */
const fileIcon = computed(() => {
  const iconMap: Record<string, string> = {
    audio: 'lucide:music',
    document: 'lucide:file-text',
    video: 'lucide:film',
    image: 'lucide:image',
    other: 'lucide:file'
  }
  return iconMap[props.result.type] || iconMap.other
})
</script>

<style scoped>
.result-card {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  box-shadow: var(--shadow-card);
  transition: all var(--transition-base);
  margin-bottom: var(--space-lg);
}

.result-card:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.result-icon {
  color: var(--brand-blue);
}

.result-info {
  flex: 1;
}

.result-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-xl);
  line-height: 1.27;
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.badge {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 4px var(--space-sm);
}

.result-size {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.result-preview {
  margin-bottom: var(--space-md);
}

.preview-text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-xs) 0;
}

.preview-path {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.result-actions {
  display: flex;
  gap: var(--space-xs);
  padding-top: var(--space-md);
  border-top: var(--border-standard);
}

.action-link {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-link:hover {
  color: var(--brand-blue);
  background: var(--bg-hover);
}

.action-link.danger:hover {
  color: var(--warning-orange);
}
</style>
