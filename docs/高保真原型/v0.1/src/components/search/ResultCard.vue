<template>
  <div class="result-card" :class="{ 'loading': loading }" @click="handleCardClick">
    <div class="card-header">
      <div class="file-info">
        <div class="file-icon">
          <SimpleIcon :type="getFileTypeIcon(result.file_type)" />
        </div>
        <div class="file-details">
          <h3 class="file-name" :title="result.file_name">
            {{ result.file_name }}
          </h3>
          <div class="file-meta">
            <span class="file-path">{{ formatFilePath(result.file_path) }}</span>
            <span class="separator">•</span>
            <span class="file-size">{{ formatFileSize(result.file_size) }}</span>
            <span class="separator">•</span>
            <span class="file-time">{{ formatTime(result.modified_at) }}</span>
          </div>
        </div>
      </div>
      <div class="relevance-score">
        <div class="score-circle" :class="getScoreClass(result.relevance_score)">
          <span class="score-text">{{ Math.round(result.relevance_score * 100) }}%</span>
        </div>
        <div class="score-label">匹配度</div>
      </div>
    </div>

    <div class="card-content">
      <div class="preview-text" v-html="result.highlight"></div>
      <div class="file-tags" v-if="result.tags && result.tags.length > 0">
        <a-tag
          v-for="tag in result.tags"
          :key="tag"
          size="small"
          color="cyan"
        >
          {{ tag }}
        </a-tag>
      </div>
    </div>

    <div class="card-footer">
      <div class="match-type">
        <a-tag :color="getMatchTypeColor(result.match_type)" size="small">
          {{ getMatchTypeLabel(result.match_type) }}
        </a-tag>
      </div>
      <div class="action-buttons">
        <a-button
          type="text"
          size="small"
          @click.stop="handlePreview"
          title="预览"
        >
          <SimpleIcon type="preview" />
          预览
        </a-button>
        <a-button
          type="text"
          size="small"
          @click.stop="handleOpen"
          title="打开"
        >
          <SimpleIcon type="open" />
          打开
        </a-button>
        <a-button
          type="text"
          size="small"
          :class="{ 'favorited': result.is_favorite }"
          @click.stop="handleFavorite"
          title="收藏"
        >
          <SimpleIcon type="favorite" />
          {{ result.is_favorite ? '已收藏' : '收藏' }}
        </a-button>
        <a-dropdown placement="bottomRight" :trigger="['click']">
          <a-button
            type="text"
            size="small"
            @click.stop
            title="更多"
          >
            <SimpleIcon type="more" />
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item key="copy" @click="handleCopyPath">
                <SimpleIcon type="copy" />
                复制路径
              </a-menu-item>
              <a-menu-item key="properties" @click="handleProperties">
                <SimpleIcon type="info-circle" />
                属性
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="delete" class="danger-item" @click="handleDelete">
                <SimpleIcon type="delete" />
                删除
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 加载动画 -->
    <div class="loading-overlay" v-if="loading">
      <div class="loading-spinner">
        <SimpleIcon type="loading" />
        <span>处理中...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'
import type { SearchResult, FileType } from '@/types/api'

interface Props {
  result: SearchResult
  index: number
  loading?: boolean
}

interface Emits {
  (e: 'preview', result: SearchResult): void
  (e: 'open', result: SearchResult): void
  (e: 'favorite', result: SearchResult): void
  (e: 'delete', result: SearchResult): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 获取文件图标类型
const getFileTypeIcon = (fileType: FileType): string => {
  const iconMap: Record<FileType, string> = {
    document: 'file',
    pdf: 'file',
    spreadsheet: 'file',
    text: 'file',
    image: 'image',
    video: 'audio',
    audio: 'audio',
    other: 'file'
  }
  return iconMap[fileType] || 'file'
}

// 格式化文件路径
const formatFilePath = (filePath: string): string => {
  const parts = filePath.split(/[\\/]/)
  return parts.slice(0, -1).join(' / ')
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)}${units[unitIndex]}`
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '今天'
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks}周前`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    return `${months}个月前`
  } else {
    const years = Math.floor(diffDays / 365)
    return `${years}年前`
  }
}

// 获取分数样式类
const getScoreClass = (score: number): string => {
  if (score >= 0.9) return 'excellent'
  if (score >= 0.8) return 'good'
  if (score >= 0.7) return 'fair'
  return 'poor'
}

// 获取匹配类型颜色
const getMatchTypeColor = (matchType: string): string => {
  const colorMap: Record<string, string> = {
    semantic: 'purple',
    fulltext: 'blue',
    hybrid: 'cyan'
  }
  return colorMap[matchType] || 'default'
}

// 获取匹配类型标签
const getMatchTypeLabel = (matchType: string): string => {
  const labelMap: Record<string, string> = {
    semantic: '语义',
    fulltext: '全文',
    hybrid: '混合'
  }
  return labelMap[matchType] || matchType
}

// 事件处理
const handleCardClick = () => {
  emit('open', props.result)
}

const handlePreview = () => {
  emit('preview', props.result)
}

const handleOpen = () => {
  emit('open', props.result)
}

const handleFavorite = () => {
  emit('favorite', props.result)
}

const handleCopyPath = async () => {
  try {
    await navigator.clipboard.writeText(props.result.file_path)
    message.success('路径已复制到剪贴板')
  } catch (error) {
    message.error('复制失败')
  }
}

const handleProperties = () => {
  // 显示文件属性对话框
  console.log('显示文件属性:', props.result)
}

const handleDelete = () => {
  emit('delete', props.result)
}
</script>

<style lang="scss" scoped>
.result-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: all 0.3s var(--ease-out-cubic);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s var(--ease-out-cubic) backwards;
  animation-delay: calc(var(--index, 0) * 0.1s);

  @include glass-morphism;

  &:hover {
    transform: translateY(-4px);
    border-color: rgba(0, 229, 255, 0.3);
    box-shadow: 0 12px 40px rgba(0, 229, 255, 0.2);
  }

  &.loading {
    pointer-events: none;
    opacity: 0.7;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 卡片头部
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
}

.file-info {
  display: flex;
  gap: var(--space-3);
  flex: 1;
  min-width: 0;
}

.file-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 229, 255, 0.1);
  color: var(--accent-cyan);
  border-radius: var(--radius-lg);
  font-size: 18px;
  border: 1px solid rgba(0, 229, 255, 0.2);
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  flex-wrap: wrap;

  .separator {
    color: var(--border-medium);
  }

  .file-path {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.relevance-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

.score-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--text-sm);
  position: relative;
  transition: all 0.3s var(--ease-out-cubic);

  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, currentColor, transparent);
    opacity: 0.3;
    z-index: -1;
  }

  &.excellent {
    background: var(--success);
    color: white;
  }

  &.good {
    background: var(--accent-cyan);
    color: white;
  }

  &.fair {
    background: var(--warning);
    color: white;
  }

  &.poor {
    background: var(--error);
    color: white;
  }
}

.score-text {
  position: relative;
  z-index: 1;
}

.score-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: 500;
}

// 卡片内容
.card-content {
  margin-bottom: var(--space-4);
}

.preview-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;

  :deep(em) {
    background: rgba(0, 229, 255, 0.2);
    color: var(--accent-cyan);
    padding: 0 2px;
    border-radius: 2px;
    font-style: normal;
  }
}

.file-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

// 卡片底部
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
}

.match-type :deep(.ant-tag) {
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: opacity 0.3s var(--ease-out-cubic);

  .result-card:hover & {
    opacity: 1;
  }
}

.action-buttons :deep(.ant-btn) {
  border: none;
  color: var(--text-tertiary);
  transition: all 0.3s var(--ease-out-cubic);

  &:hover {
    color: var(--accent-cyan);
    background: rgba(0, 229, 255, 0.1);
  }

  &.favorited {
    color: var(--warning);
  }
}

// 加载覆盖层
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  backdrop-filter: blur(4px);
  z-index: 10;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

// 下拉菜单
:deep(.ant-dropdown-menu) {
  background: var(--surface-tertiary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);

  .ant-dropdown-menu-item {
    color: var(--text-secondary);
    transition: all 0.2s var(--ease-out-cubic);

    &:hover {
      background: rgba(0, 229, 255, 0.1);
      color: var(--accent-cyan);
    }

    &.danger-item:hover {
      background: rgba(239, 68, 68, 0.1);
      color: var(--error);
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .result-card {
    padding: var(--space-4);
  }

  .card-header {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }

  .file-info {
    gap: var(--space-2);
  }

  .file-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .file-name {
    font-size: var(--text-base);
  }

  .file-meta {
    font-size: 10px;
  }

  .relevance-score {
    align-self: center;
  }

  .score-circle {
    width: 40px;
    height: 40px;
    font-size: 11px;
  }

  .card-footer {
    flex-direction: column;
    gap: var(--space-2);
    align-items: stretch;
  }

  .action-buttons {
    justify-content: center;
    opacity: 1;
  }

  .action-buttons :deep(.ant-btn) {
    span {
      display: none;
    }
  }
}

@media (max-width: 480px) {
  .result-card {
    padding: var(--space-3);
  }

  .file-meta .file-path {
    max-width: 120px;
  }

  .action-buttons :deep(.ant-btn) {
    padding: 4px 8px;
  }
}

// 无障碍
@media (prefers-reduced-motion: reduce) {
  .result-card {
    animation: none;

    &:hover {
      transform: none;
    }
  }

  .score-circle,
  .action-buttons :deep(.ant-btn),
  .loading-overlay {
    transition: none;
  }
}
</style>