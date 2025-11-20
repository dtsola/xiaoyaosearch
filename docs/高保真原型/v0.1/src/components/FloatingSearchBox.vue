<template>
  <div class="floating-search-box">
    <div class="search-container">
      <!-- 搜索框主体 -->
      <div class="search-input-wrapper">
        <div class="search-input-container">
          <!-- 左侧工具栏 -->
          <div class="search-tools">
            <div class="tool-button" @click="$emit('voiceToggle')" title="语音输入">
              <span class="tool-icon">🔊</span>
            </div>
            <div class="tool-button" @click="$emit('textMode')" title="文本输入">
              <span class="tool-icon">📝</span>
            </div>
            <div class="tool-button" @click="$emit('imageMode')" title="图片输入">
              <span class="tool-icon">🖼️</span>
            </div>
          </div>

          <!-- 主要搜索输入区域 -->
          <div class="search-main">
            <div class="search-input-field">
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                class="search-input"
                :placeholder="placeholderText"
                @keydown.enter="handleSearch"
                @input="handleInput"
                :disabled="isRecording"
                aria-label="搜索文件"
                role="searchbox"
                aria-expanded="false"
                aria-autocomplete="list"
              />

              <!-- 语音波形可视化 -->
              <div v-if="isRecording" class="voice-visualization">
                <div class="voice-bars">
                  <div
                    v-for="i in 12"
                    :key="i"
                    class="voice-bar"
                    :style="{ animationDelay: `${i * 0.05}s` }"
                  ></div>
                </div>
                <div class="voice-timer">
                  <span>{{ formatTime(recordingTime) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧操作按钮 -->
          <div class="search-actions">
            <button
              class="action-button primary"
              @click="handleSearch"
              :disabled="!canSearch"
              title="智能搜索"
            >
              <span class="action-icon">🔍</span>
              <span class="action-text">智能搜索</span>
            </button>
            <button
              class="action-button secondary"
              @click="$emit('aiEnhance')"
              title="AI增强分析"
            >
              <span class="action-icon">⚡</span>
              <span class="action-text">AI分析</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 搜索建议下拉框 -->
      <transition name="dropdown">
        <div v-if="showSuggestions" class="search-suggestions">
          <div class="suggestions-header">
            <span class="suggestions-title">搜索建议</span>
          </div>
          <div class="suggestions-list">
            <div
              v-for="(suggestion, index) in suggestions"
              :key="index"
              class="suggestion-item"
              @click="selectSuggestion(suggestion)"
              @keydown.enter="selectSuggestion(suggestion)"
              tabindex="0"
            >
              <span class="suggestion-icon">💡</span>
              <span class="suggestion-text">{{ suggestion }}</span>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 隐藏的文件上传输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      @change="handleImageUpload"
      style="display: none"
      aria-hidden="true"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/useAppStore'

interface Emits {
  (e: 'search'): void
  (e: 'voiceToggle'): void
  (e: 'textMode'): void
  (e: 'imageMode'): void
  (e: 'aiEnhance'): void
}

const emit = defineEmits<Emits>()

const appStore = useAppStore()
const { currentMode, isRecording } = storeToRefs(appStore)

const searchInputRef = ref<HTMLInputElement>()
const fileInputRef = ref<HTMLInputElement>()
const recordingTime = ref(0)
const recordingTimer = ref<NodeJS.Timeout>()
const showSuggestions = ref(false)

const searchQuery = computed({
  get: () => appStore.search.query,
  set: (value: string) => appStore.setQuery(value)
})

const placeholderText = computed(() => {
  switch (currentMode.value) {
    case 'voice':
      return '🎤 点击麦克风开始录音...'
    case 'image':
      return '🖼️ 选择或拖拽图片到此处...'
    default:
      return '✨ 说出你的想法，或开始输入...'
  }
})

const canSearch = computed(() => {
  return searchQuery.value.trim().length > 0 && !isRecording.value
})

const suggestions = computed(() => {
  if (!searchQuery.value.trim()) return []

  const allSuggestions = [
    'AI技术发展趋势',
    '机器学习算法优化',
    '前端开发最佳实践',
    'API接口设计规范',
    '产品原型设计',
    '用户体验研究',
    '数据结构分析',
    '系统架构设计'
  ]

  return allSuggestions.filter(suggestion =>
    suggestion.toLowerCase().includes(searchQuery.value.toLowerCase())
  ).slice(0, 5)
})

// 监听录音状态
watch(isRecording, (newValue) => {
  if (newValue) {
    startRecordingTimer()
  } else {
    stopRecordingTimer()
  }
})

// 监听输入模式变化
watch(currentMode, (newMode) => {
  if (newMode === 'image') {
    nextTick(() => {
      fileInputRef.value?.click()
    })
  }

  // 聚焦到输入框
  if (newMode === 'text') {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
})

const startRecordingTimer = () => {
  recordingTime.value = 0
  recordingTimer.value = setInterval(() => {
    recordingTime.value++
    if (recordingTime.value >= 30) {
      appStore.stopVoiceRecording()
    }
  }, 1000)
}

const stopRecordingTimer = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = undefined
  }
  recordingTime.value = 0
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleSearch = () => {
  if (canSearch.value) {
    showSuggestions.value = false
    appStore.startSearch()
    emit('search')
  }
}

const handleInput = () => {
  showSuggestions.value = searchQuery.value.trim().length > 0
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  handleSearch()
}

const handleImageUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file && file.type.startsWith('image/')) {
    appStore.handleImageUpload(file)
  }
}

// 点击外部关闭建议框
const handleClickOutside = () => {
  showSuggestions.value = false
}

// 暴露方法给父组件
defineExpose({
  focus: () => searchInputRef.value?.focus(),
  blur: () => searchInputRef.value?.blur()
})
</script>

<style scoped lang="scss">
.floating-search-box {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-container {
  position: relative;
}

.search-input-wrapper {
  background: var(--surface-tertiary);
  border-radius: var(--radius-xl);
  border: 2px solid var(--border-primary);
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-normal);
  overflow: hidden;

  &:hover {
    border-color: rgba(var(--accent-cyan-rgb), 0.3);
    box-shadow: 0 16px 64px rgba(0, 0, 0, 0.6);
  }

  &:focus-within {
    border-color: var(--accent-cyan);
    box-shadow: var(--shadow-glow-primary);
  }
}

.search-input-container {
  display: flex;
  align-items: center;
  padding: var(--space-4);
  gap: var(--space-4);
}

.search-tools {
  display: flex;
  gap: var(--space-2);
  padding-right: var(--space-3);
  border-right: 1px solid var(--border-secondary);
}

.tool-button {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-base);
  background: var(--surface-quaternary);
  border: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;

  &:hover {
    background: var(--primary-light);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}

.search-main {
  flex: 1;
  min-width: 0;
}

.search-input-field {
  position: relative;
}

.search-input {
  width: 100%;
  padding: var(--space-4) var(--space-5);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-family: var(--font-display);
  outline: none;

  &::placeholder {
    color: var(--text-tertiary);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.voice-visualization {
  position: absolute;
  top: 50%;
  left: var(--space-5);
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  pointer-events: none;
}

.voice-bars {
  display: flex;
  align-items: center;
  gap: 2px;
}

.voice-bar {
  width: 3px;
  height: 20px;
  background: linear-gradient(to top, var(--accent-magenta), var(--accent-cyan));
  border-radius: var(--radius-sm);
  animation: voiceWave 0.6s ease-in-out infinite;
  transform-origin: center;
}

.voice-timer {
  font-size: var(--text-xs);
  color: var(--accent-cyan);
  font-weight: 600;
  background: rgba(var(--accent-cyan-rgb), 0.1);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(var(--accent-cyan-rgb), 0.3);
}

.search-actions {
  display: flex;
  gap: var(--space-3);
}

.action-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
  white-space: nowrap;

  &.primary {
    background: linear-gradient(135deg, var(--primary-core), var(--primary-light));
    color: var(--text-primary);
    border-color: var(--accent-cyan);

    &:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 8px 24px rgba(var(--accent-cyan-rgb), 0.3);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }

  &.secondary {
    background: var(--surface-quaternary);
    color: var(--text-secondary);
    border-color: var(--border-primary);

    &:hover {
      background: var(--primary-light);
      color: var(--text-primary);
      border-color: var(--accent-cyan);
    }
  }
}

.action-icon {
  font-size: 14px;
}

.search-suggestions {
  position: absolute;
  top: calc(100% + var(--space-2));
  left: 0;
  right: 0;
  background: var(--surface-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  overflow: hidden;
}

.suggestions-header {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-secondary);
  background: var(--surface-quaternary);
}

.suggestions-title {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.suggestions-list {
  max-height: 240px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background-color var(--transition-fast);

  &:hover {
    background: var(--surface-quaternary);
  }

  &:focus-visible {
    outline: none;
    background: var(--surface-quaternary);
    border-left: 3px solid var(--accent-cyan);
  }
}

.suggestion-icon {
  font-size: 14px;
  opacity: 0.7;
}

.suggestion-text {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

// 动画定义
@keyframes voiceWave {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(1.5);
  }
}

// 过渡动画
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-normal);
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// 响应式设计
@media (max-width: 768px) {
  .search-input-container {
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-3);
  }

  .search-tools {
    order: 1;
    width: 100%;
    justify-content: center;
    padding-right: 0;
    padding-bottom: var(--space-3);
    border-right: none;
    border-bottom: 1px solid var(--border-secondary);
  }

  .search-main {
    order: 2;
    width: 100%;
  }

  .search-actions {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .action-button {
    flex: 1;
    justify-content: center;
  }
}

// 高对比度模式
@media (prefers-contrast: high) {
  .search-input-wrapper {
    border-width: 3px;
  }

  .action-button {
    border-width: 2px;
  }

  .suggestion-item:focus-visible {
    border-left-width: 4px;
  }
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
  .voice-bar {
    animation: none;
  }

  .dropdown-enter-active,
  .dropdown-leave-active {
    transition: none;
  }
}
</style>