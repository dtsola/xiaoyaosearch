<template>
  <div class="result-card" :class="{ 'is-favorite': isFavorite }">
    <!-- 文件头部信息 -->
    <div class="card-header">
      <div class="file-info">
        <!-- 文件图标 -->
        <div class="file-icon" :class="`file-type-${result.file_type}`">
          <FileTextOutlined v-if="result.file_type === 'document'" />
          <AudioOutlined v-else-if="result.file_type === 'audio'" />
          <VideoCameraOutlined v-else-if="result.file_type === 'video'" />
          <PictureOutlined v-else-if="result.file_type === 'image'" />
          <FileOutlined v-else />
        </div>

        <!-- 文件名称和路径 -->
        <div class="file-details">
          <h4 class="file-name" @click="$emit('open', result)">
            {{ result.file_name }}
          </h4>
          <div class="file-path" :title="result.file_path">
            <FolderOutlined />
            {{ result.file_path }}
          </div>
        </div>
      </div>

      <!-- 相关性评分 -->
      <div class="relevance-score">
        <a-progress
          type="circle"
          :percent="Math.round(result.relevance_score * 100)"
          :size="60"
          :stroke-color="getScoreColor(result.relevance_score)"
          :width="60"
          class="score-circle"
        >
          <template #format="percent">
            <span class="score-text">{{ percent }}%</span>
          </template>
        </a-progress>
        <div class="score-label">匹配度</div>
      </div>
    </div>

    <!-- 文件内容预览 -->
    <div class="card-content">
      <div class="preview-text" v-html="result.highlight"></div>

      <!-- 文件元信息 -->
      <div class="file-metadata">
        <div class="metadata-row">
          <span class="metadata-item">
            <CalendarOutlined />
            {{ formatDate(result.modified_at) }}
          </span>
          <span class="metadata-item">
            <HddOutlined />
            {{ formatFileSize(result.file_size) }}
          </span>
          <span class="metadata-item">
            <TagOutlined />
            {{ getMatchTypeLabel(result.match_type) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions">
      <a-button type="text" size="small" @click="$emit('preview', result)">
        <EyeOutlined />
        预览
      </a-button>
      <a-button type="text" size="small" @click="$emit('open', result)">
        <FolderOpenOutlined />
        打开
      </a-button>
      <a-button
        type="text"
        size="small"
        :class="{ 'is-favorite': isFavorite }"
        @click="toggleFavorite"
      >
        <StarFilled v-if="isFavorite" />
        <StarOutlined v-else />
        {{ isFavorite ? '已收藏' : '收藏' }}
      </a-button>
      <a-dropdown>
        <a-button type="text" size="small">
          <MoreOutlined />
          更多
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item @click="copyFilePath">
              <CopyOutlined />
              复制路径
            </a-menu-item>
            <a-menu-item @click="showFileProperties">
              <InfoCircleOutlined />
              文件属性
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item @click="$emit('delete', result)" class="danger-item">
              <DeleteOutlined />
              删除
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import type { SearchResult } from '@/types/api'
import {
  FileTextOutlined,
  AudioOutlined,
  VideoCameraOutlined,
  PictureOutlined,
  FileOutlined,
  FolderOutlined,
  EyeOutlined,
  FolderOpenOutlined,
  StarOutlined,
  StarFilled,
  MoreOutlined,
  CopyOutlined,
  InfoCircleOutlined,
  DeleteOutlined,
  CalendarOutlined,
  HddOutlined,
  TagOutlined
} from '@ant-design/icons-vue'

// Props
interface Props {
  result: SearchResult
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  preview: [result: SearchResult]
  open: [result: SearchResult]
  favorite: [result: SearchResult, isFavorite: boolean]
  delete: [result: SearchResult]
}>()

// 响应式数据
const isFavorite = ref(false)

// 计算属性
const getScoreColor = (score: number) => {
  if (score >= 0.9) return '#52c41a'
  if (score >= 0.7) return '#1890ff'
  if (score >= 0.5) return '#faad14'
  return '#ff4d4f'
}

const getMatchTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    semantic: '语义匹配',
    fulltext: '全文匹配',
    hybrid: '混合匹配'
  }
  return typeMap[type] || type
}

// 方法
const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value
  emit('favorite', props.result, isFavorite.value)
  message.success(isFavorite.value ? '已添加到收藏' : '已取消收藏')
}

const copyFilePath = async () => {
  try {
    await navigator.clipboard.writeText(props.result.file_path)
    message.success('文件路径已复制到剪贴板')
  } catch (error) {
    message.error('复制失败，请手动复制')
  }
}

const showFileProperties = () => {
  message.info('文件属性功能开发中...')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}
</script>

<style scoped>
.result-card {
  background: var(--surface-01);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-base);
  transition: all var(--transition-base);
  margin-bottom: var(--space-4);
  position: relative;
  overflow: hidden;
}

.result-card:hover {
  border-color: var(--primary-200);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.result-card.is-favorite {
  border-color: var(--warning);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0.02));
}

.result-card.is-favorite::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--warning), var(--warning-light));
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.file-info {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  flex: 1;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.file-type-document {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
}

.file-type-audio {
  background: linear-gradient(135deg, #faad14, #ffc53d);
}

.file-type-video {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
}

.file-type-image {
  background: linear-gradient(135deg, #52c41a, #73d13d);
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
  cursor: pointer;
  transition: color var(--transition-base);
  word-break: break-word;
}

.file-name:hover {
  color: var(--primary-600);
}

.file-path {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.relevance-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  margin-left: var(--space-4);
}

.score-circle {
  font-weight: 600;
}

.score-text {
  font-size: 0.875rem;
  font-weight: 600;
}

.score-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.card-content {
  margin-bottom: var(--space-4);
}

.preview-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-3);
  word-break: break-word;
}

.preview-text :deep(em) {
  background: rgba(245, 158, 11, 0.2);
  color: #d97706;
  padding: 2px 4px;
  border-radius: 4px;
  font-style: normal;
  font-weight: 500;
}

.file-metadata {
  border-top: 1px solid var(--border-light);
  padding-top: var(--space-3);
}

.metadata-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.75rem;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-wrap: wrap;
}

.card-actions .ant-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.card-actions .ant-btn:hover {
  background: var(--surface-02);
  transform: translateY(-1px);
}

.card-actions .ant-btn.is-favorite {
  color: var(--warning);
  background: rgba(245, 158, 11, 0.1);
}

.card-actions .ant-btn.is-favorite:hover {
  background: rgba(245, 158, 11, 0.2);
}

.danger-item {
  color: var(--error);
}

.danger-item:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-card {
    padding: var(--space-4);
  }

  .card-header {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }

  .relevance-score {
    align-self: flex-end;
    margin-left: 0;
  }

  .file-info {
    gap: var(--space-3);
  }

  .card-actions {
    justify-content: center;
  }

  .metadata-row {
    justify-content: center;
    gap: var(--space-2);
  }
}
</style>