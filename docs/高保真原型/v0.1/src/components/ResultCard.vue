<template>
  <div class="result-card" :class="[`type-${result.type}`, { highlighted: isHighlighted }]">
    <div class="card-header">
      <div class="file-icon">
        <span class="icon-emoji">{{ result.icon }}</span>
        <div class="icon-glow"></div>
      </div>
      <div class="file-info">
        <h3 class="file-name" :title="result.name">{{ result.name }}</h3>
        <div class="file-meta">
          <span class="match-score">
            <span class="score-icon">🎯</span>
            <span class="score-text">匹配度: {{ result.matchScore }}%</span>
          </span>
          <span class="file-size">
            <span class="size-icon">📊</span>
            <span class="size-text">{{ result.size }}</span>
          </span>
        </div>
      </div>
      <div class="file-actions">
        <button
          v-for="action in actions"
          :key="action.key"
          :class="['action-btn', action.type]"
          @click="handleAction(action.key)"
          :title="action.title"
          :aria-label="action.title"
        >
          <span class="action-icon">{{ action.icon }}</span>
        </button>
      </div>
    </div>

    <div class="card-content">
      <div class="preview-text">
        <span class="preview-icon">💬</span>
        <p class="preview-content">{{ result.preview }}</p>
      </div>
      <div class="file-path">
        <span class="path-icon">📍</span>
        <span class="path-text">{{ result.path }}</span>
      </div>
    </div>

    <div class="card-footer">
      <div v-if="result.tags && result.tags.length > 0" class="file-tags">
        <span
          v-for="tag in result.tags"
          :key="tag"
          class="tag"
        >
          {{ tag }}
        </span>
      </div>
      <div class="file-date">
        <span class="date-icon">🕒</span>
        <span class="date-text">{{ formatDate(result.lastModified) }}</span>
      </div>
    </div>

    <!-- 匹配度进度条 -->
    <div class="match-progress">
      <div
        class="progress-fill"
        :style="{ width: `${result.matchScore}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SearchResult } from '@/types'

interface Props {
  result: SearchResult
  isHighlighted?: boolean
}

interface Emits {
  (e: 'preview', result: SearchResult): void
  (e: 'open', result: SearchResult): void
  (e: 'favorite', result: SearchResult): void
  (e: 'delete', result: SearchResult): void
}

const props = withDefaults(defineProps<Props>(), {
  isHighlighted: false
})

const emit = defineEmits<Emits>()

const actions = [
  { key: 'preview', icon: '👁️', title: '预览', type: 'primary' },
  { key: 'open', icon: '📂', title: '打开位置', type: 'secondary' },
  { key: 'favorite', icon: '⭐', title: '收藏', type: 'secondary' },
  { key: 'delete', icon: '🗑️', title: '删除', type: 'danger' }
]

const handleAction = (actionKey: string) => {
  switch (actionKey) {
    case 'preview':
      emit('preview', props.result)
      break
    case 'open':
      emit('open', props.result)
      break
    case 'favorite':
      emit('favorite', props.result)
      break
    case 'delete':
      emit('delete', props.result)
      break
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else if (diffDays < 30) {
    return `${Math.floor(diffDays / 7)}周前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}
</script>

<style scoped lang="scss">
.result-card {
  position: relative;
  background: var(--surface-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-4);
  transition: all var(--transition-normal);
  overflow: hidden;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    border-color: var(--accent-cyan);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
  }

  &.highlighted {
    border-color: var(--accent-cyan);
    background: rgba(var(--accent-cyan-rgb), 0.05);
    animation: highlight 1.5s ease-in-out;
  }

  // 不同文件类型的样式
  &.type-audio {
    border-left: 4px solid var(--accent-magenta);
  }

  &.type-document {
    border-left: 4px solid var(--accent-cyan);
  }

  &.type-image {
    border-left: 4px solid var(--accent-yellow);
  }

  &.type-video {
    border-left: 4px solid var(--error);
  }

  &.type-code {
    border-left: 4px solid var(--success);
  }

  &.type-other {
    border-left: 4px solid var(--text-tertiary);
  }
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.file-icon {
  position: relative;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  background: var(--surface-quaternary);
  flex-shrink: 0;
}

.icon-emoji {
  font-size: 24px;
  z-index: 1;
  position: relative;
}

.icon-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(var(--accent-cyan-rgb), 0.2) 0%, transparent 70%);
  border-radius: var(--radius-lg);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.result-card:hover .icon-glow {
  opacity: 1;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.match-score,
.file-size {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.score-icon,
.size-icon {
  font-size: 12px;
}

.file-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-base);
  border: 1px solid var(--border-primary);
  background: var(--surface-quaternary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  &:hover {
    transform: translateY(-1px);

    &.primary {
      background: var(--primary-light);
      border-color: var(--accent-cyan);
    }

    &.secondary {
      background: rgba(var(--accent-cyan-rgb), 0.1);
      border-color: var(--accent-cyan);
    }

    &.danger {
      background: rgba(var(--error-rgb), 0.1);
      border-color: var(--error);
    }
  }

  &:active {
    transform: translateY(0);
  }

  &:focus-visible {
    outline: 2px solid var(--accent-cyan);
    outline-offset: 2px;
  }
}

.card-content {
  margin-bottom: var(--space-4);
}

.preview-text {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.preview-icon {
  font-size: 14px;
  opacity: 0.7;
  flex-shrink: 0;
  margin-top: 2px;
}

.preview-content {
  flex: 1;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.file-path {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-family: var(--font-mono);
  background: var(--surface-quaternary);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-base);
  border: 1px solid var(--border-secondary);
}

.path-icon {
  font-size: 12px;
}

.path-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.file-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.tag {
  background: rgba(var(--accent-cyan-rgb), 0.1);
  color: var(--accent-cyan);
  font-size: var(--text-xs);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(var(--accent-cyan-rgb), 0.2);
  font-weight: 500;
}

.file-date {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.date-icon {
  font-size: 12px;
}

.match-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--surface-quaternary);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta));
  border-radius: var(--radius-sm);
  transition: width var(--transition-slow);
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: progressShine 2s infinite;
  }
}

// 动画定义
@keyframes highlight {
  0%, 100% {
    background-color: rgba(var(--accent-cyan-rgb), 0.05);
    border-color: var(--accent-cyan);
  }
  50% {
    background-color: rgba(var(--accent-cyan-rgb), 0.1);
    border-color: rgba(var(--accent-cyan-rgb), 0.5);
  }
}

@keyframes progressShine {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
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
  }

  .file-info {
    width: 100%;
  }

  .file-actions {
    align-self: flex-end;
  }

  .file-meta {
    gap: var(--space-3);
  }

  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}

// 高对比度模式
@media (prefers-contrast: high) {
  .result-card {
    border-width: 2px;
  }

  .action-btn {
    border-width: 2px;
  }

  .tag {
    border-width: 2px;
  }
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
  .result-card {
    transition: none;

    &:hover {
      transform: none;
    }
  }

  .progress-fill::after {
    animation: none;
  }

  .result-card.highlighted {
    animation: none;
  }
}
</style>