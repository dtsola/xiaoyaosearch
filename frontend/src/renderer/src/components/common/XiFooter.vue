<template>
  <footer class="xi-footer">
    <div class="footer-content">
      <div class="status-info">
        <span class="status-item">
          <XiIcon icon="lucide:database" :size="14" />
          索引: {{ indexCount.toLocaleString() }} 文件
        </span>
        <span class="status-item">
          <XiIcon icon="lucide:search" :size="14" />
          今日: {{ searchCount }} 次搜索
        </span>
        <span class="status-item">
          <XiIcon icon="lucide:hard-drive" :size="14" />
          数据: {{ formattedDataSize }}
        </span>
      </div>
      <div class="system-status">
        <span class="last-update">最后更新: {{ formattedTime }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import XiIcon from './XiIcon.vue'

/**
 * XiFooter 组件 Props
 */
interface Props {
  /** 索引文件数量 */
  indexCount?: number
  /** 今日搜索次数 */
  searchCount?: number
  /** 数据大小（字节） */
  dataSize?: number
  /** 最后更新时间 */
  lastUpdate?: Date
}

const props = withDefaults(defineProps<Props>(), {
  indexCount: 0,
  searchCount: 0,
  dataSize: 0,
  lastUpdate: () => new Date()
})

/**
 * 格式化数据大小
 */
const formattedDataSize = computed(() => {
  const bytes = props.dataSize
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
})

/**
 * 格式化时间
 */
const formattedTime = computed(() => {
  return props.lastUpdate.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<style scoped>
.xi-footer {
  height: 40px;
  background: var(--bg-primary);
  border-top: var(--border-standard);
  padding: var(--space-sm) 0;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
}

.status-info {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 500;
}

.system-status {
  display: flex;
  align-items: center;
}

.last-update {
  color: var(--text-tertiary);
  font-size: 12px;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: var(--space-xs);
    padding: var(--space-sm) var(--space-lg);
  }

  .status-info {
    gap: var(--space-md);
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
