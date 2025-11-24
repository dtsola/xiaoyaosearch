<template>
  <div class="floating-search-box">
    <div class="search-wrapper">
      <!-- 悬浮式搜索框主体 -->
      <div class="search-box-container">
        <div class="search-box">
          <!-- 斜切设计边框 -->
          <div class="search-box-border">
            <!-- 搜索图标区域 -->
            <div class="search-icon-area">
              <div class="search-icon">
                <SimpleIcon type="search" v-if="!isLoading" />
                <SimpleIcon type="loading" v-else />
              </div>
            </div>

            <!-- 搜索输入区域 -->
            <div class="search-input-area">
              <input
                ref="searchInputRef"
                v-model="searchValue"
                type="text"
                :placeholder="getPlaceholder()"
                :disabled="isLoading"
                class="search-input"
                @keydown="handleKeydown"
                @input="handleInput"
                @focus="handleFocus"
                @blur="handleBlur"
              />

              <!-- 语音录制时间显示 -->
              <div class="recording-timer" v-if="isRecording">
                <div class="timer-display">
                  <span class="timer-text">{{ formatTime(recordingTime) }}</span>
                </div>
                <div class="timer-progress">
                  <div
                    class="progress-bar"
                    :style="{ width: `${(recordingTime / 30) * 100}%` }"
                  ></div>
                </div>
              </div>

              <!-- 搜索建议下拉 -->
              <div
                class="search-suggestions"
                v-if="showSuggestions && suggestions.length > 0"
              >
                <div
                  v-for="(suggestion, index) in suggestions"
                  :key="index"
                  class="suggestion-item"
                  :class="{ 'selected': selectedIndex === index }"
                  @click="handleSuggestionSelect(suggestion)"
                  @mouseenter="selectedIndex = index"
                >
                  <SimpleIcon type="history" class="suggestion-icon" />
                  <span class="suggestion-text">{{ suggestion }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮区域 -->
            <div class="search-actions">
              <!-- 语音录制按钮 -->
              <button
                v-if="activeMode === 'voice'"
                class="action-btn voice-btn"
                :class="{ 'recording': isRecording }"
                @click="$emit('voiceToggle')"
                :disabled="isLoading"
              >
                <SimpleIcon type="audio" v-if="!isRecording" />
                <SimpleIcon type="pause" v-else />
              </button>

              <!-- 文件上传按钮 -->
              <button
                v-if="activeMode === 'image'"
                class="action-btn upload-btn"
                @click="handleFileUpload"
                :disabled="isLoading"
              >
                <SimpleIcon type="camera" />
              </button>

              <!-- 搜索按钮 -->
              <button
                class="action-btn search-btn"
                :disabled="!searchValue.trim() || isLoading"
                @click="handleSearch"
              >
                <SimpleIcon type="search" />
              </button>
            </div>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="search-toolbar">
          <div class="toolbar-left">
            <a-button
              type="text"
              size="small"
              @click="handleAIEnhance"
              :disabled="isLoading"
            >
              <SimpleIcon type="bulb" />
              AI增强
            </a-button>
            <a-button
              type="text"
              size="small"
              @click="handlePreciseMatch"
              :disabled="isLoading"
            >
              <SimpleIcon type="search" />
              精准匹配
            </a-button>
            <a-button
              type="text"
              size="small"
              @click="handleSelectDirectory"
              :disabled="isLoading"
            >
              <SimpleIcon type="open" />
              选择目录
            </a-button>
          </div>

          <div class="toolbar-right">
            <a-button
              type="text"
              size="small"
              @click="handleClear"
              :disabled="isLoading"
            >
              清空
            </a-button>
          </div>
        </div>
      </div>

      <!-- 装饰性元素 -->
      <div class="search-decoration">
        <div class="decoration-orb orb-1"></div>
        <div class="decoration-orb orb-2"></div>
        <div class="decoration-line line-1"></div>
        <div class="decoration-line line-2"></div>
      </div>
    </div>

    <!-- 隐藏的文件上传输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import SimpleIcon from '@/components/SimpleIcon.vue'
import type { InputType } from '@/types/api'

interface Props {
  modelValue: string
  activeMode: InputType
  isRecording: boolean
  recordingTime: number
  suggestions: string[]
  isLoading: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string): void
  (e: 'voiceToggle'): void
  (e: 'fileUpload', file: File): void
  (e: 'suggestionSelect', suggestion: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// refs
const searchInputRef = ref<HTMLInputElement>()
const fileInputRef = ref<HTMLInputElement>()

// 响应式数据
const searchValue = ref(props.modelValue)
const showSuggestions = ref(false)
const selectedIndex = ref(-1)

// 计算属性
const hasValue = computed(() => searchValue.value.trim().length > 0)

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  searchValue.value = newValue
})

watch(() => props.suggestions, (newSuggestions) => {
  if (newSuggestions.length > 0 && searchValue.value.trim()) {
    showSuggestions.value = true
  } else {
    showSuggestions.value = false
  }
})

// 监听点击外部关闭建议
document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement
  if (!target.closest('.floating-search-box')) {
    showSuggestions.value = false
  }
})

// 获取占位符文本
const getPlaceholder = () => {
  if (props.isRecording) {
    return '正在录音...'
  }

  switch (props.activeMode) {
    case 'voice':
      return '🎙️ 点击录音或输入搜索内容...'
    case 'text':
      return '🔍 说出或输入你的想法...'
    case 'image':
      return '📷 上传图片或输入描述文字...'
    default:
      return '🌟 说出或输入你的想法...'
  }
}

// 格式化时间
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 处理键盘事件
const handleKeydown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'Enter':
      e.preventDefault()
      if (showSuggestions.value && selectedIndex.value >= 0) {
        handleSuggestionSelect(props.suggestions[selectedIndex.value])
      } else {
        handleSearch()
      }
      break
    case 'ArrowDown':
      e.preventDefault()
      if (showSuggestions.value) {
        selectedIndex.value = Math.min(
          selectedIndex.value + 1,
          props.suggestions.length - 1
        )
      }
      break
    case 'ArrowUp':
      e.preventDefault()
      if (showSuggestions.value) {
        selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
      }
      break
    case 'Escape':
      showSuggestions.value = false
      selectedIndex.value = -1
      break
  }
}

// 处理输入
const handleInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  searchValue.value = target.value
  emit('update:modelValue', target.value)

  // 重置选择索引
  selectedIndex.value = -1

  // 如果有输入内容，显示建议
  if (target.value.trim()) {
    showSuggestions.value = true
  } else {
    showSuggestions.value = false
  }
}

// 处理焦点
const handleFocus = () => {
  if (searchValue.value.trim() && props.suggestions.length > 0) {
    showSuggestions.value = true
  }
}

const handleBlur = () => {
  // 延迟关闭建议，以便点击建议项
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// 处理搜索
const handleSearch = () => {
  if (!hasValue.value || props.isLoading) return

  showSuggestions.value = false
  selectedIndex.value = -1
  emit('search', searchValue.value.trim())
}

// 处理建议选择
const handleSuggestionSelect = (suggestion: string) => {
  searchValue.value = suggestion
  emit('update:modelValue', suggestion)
  showSuggestions.value = false
  selectedIndex.value = -1
  emit('suggestionSelect', suggestion)
}

// 处理文件上传
const handleFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    emit('fileUpload', file)
  }
  // 清空input值，允许重复选择同一文件
  target.value = ''
}

// 处理AI增强
const handleAIEnhance = () => {
  console.log('AI增强搜索')
  // 这里可以实现AI增强搜索逻辑
  handleSearch()
}

// 处理精准匹配
const handlePreciseMatch = () => {
  console.log('精准匹配搜索')
  // 这里可以实现精准匹配逻辑
  handleSearch()
}

// 处理选择目录
const handleSelectDirectory = () => {
  console.log('选择目录')
  // 这里可以实现目录选择逻辑
}

// 处理清空
const handleClear = () => {
  searchValue.value = ''
  emit('update:modelValue', '')
  showSuggestions.value = false
  selectedIndex.value = -1
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// 聚焦输入框
const focus = () => {
  searchInputRef.value?.focus()
}

// 暴露方法
defineExpose({
  focus
})
</script>

<style lang="scss" scoped>
.floating-search-box {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-wrapper {
  position: relative;
}

.search-box-container {
  position: relative;
  z-index: 10;
}

.search-box {
  position: relative;
  padding: var(--space-2);
  background: var(--surface-secondary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-medium);

  @include glass-morphism;
}

.search-box-border {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: rgba(26, 31, 75, 0.6);
  border-radius: var(--radius-xl);
  border: 2px solid transparent;
  background-clip: padding-box;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--primary-gradient);
    border-radius: var(--radius-xl);
    z-index: -1;
    opacity: 0.8;
  }

  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    right: 2px;
    bottom: 2px;
    background: var(--surface-secondary);
    border-radius: var(--radius-lg);
    z-index: -1;
  }

  transition: all 0.3s var(--ease-out-cubic);

  &:hover {
    border-color: rgba(0, 229, 255, 0.3);
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.2);
  }

  &:focus-within {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 40px rgba(0, 229, 255, 0.4);
  }
}

.search-icon-area {
  flex-shrink: 0;
}

.search-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 229, 255, 0.1);
  border-radius: var(--radius-full);
  color: var(--accent-cyan);
  font-size: 20px;
  border: 2px solid rgba(0, 229, 255, 0.3);
  transition: all 0.3s var(--ease-out-cubic);
}

.search-input-area {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  height: 48px;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-family: var(--font-display);
  font-weight: 500;
  padding: 0 var(--space-3);

  &::placeholder {
    color: var(--text-tertiary);
    opacity: 0.7;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

// 录音计时器
.recording-timer {
  position: absolute;
  bottom: -40px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
}

.timer-display {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.timer-text {
  font-size: var(--text-sm);
  color: var(--error);
  font-weight: 600;
  font-family: var(--font-mono);
}

.timer-progress {
  flex: 1;
  height: 4px;
  background: rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--error);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

// 搜索建议
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: var(--space-2);
  background: var(--surface-tertiary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
  overflow: hidden;
  z-index: 100;

  @include glass-morphism;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: all 0.2s var(--ease-out-cubic);
  border-bottom: 1px solid var(--border-light);

  &:last-child {
    border-bottom: none;
  }

  &:hover,
  &.selected {
    background: rgba(0, 229, 255, 0.1);
  }

  &:hover {
    transform: translateX(4px);
  }
}

.suggestion-icon {
  color: var(--text-tertiary);
  font-size: 14px;
}

.suggestion-text {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  flex: 1;
}

// 操作按钮
.search-actions {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.action-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s var(--ease-out-cubic);
  position: relative;
  overflow: hidden;

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  &:not(:disabled):hover {
    transform: translateY(-2px);
  }
}

.voice-btn {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
  border: 2px solid rgba(239, 68, 68, 0.3);

  &:not(:disabled):hover {
    background: rgba(239, 68, 68, 0.2);
    box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
  }

  &.recording {
    background: var(--error);
    color: white;
    animation: recording-pulse 1.5s ease-in-out infinite;
  }
}

.upload-btn {
  background: rgba(74, 20, 140, 0.1);
  color: var(--accent-magenta);
  border: 2px solid rgba(74, 20, 140, 0.3);

  &:not(:disabled):hover {
    background: rgba(74, 20, 140, 0.2);
    box-shadow: 0 8px 16px rgba(74, 20, 140, 0.3);
  }
}

.search-btn {
  background: var(--primary-gradient);
  color: white;
  border: 2px solid transparent;

  &:not(:disabled):hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 12px 24px rgba(0, 229, 255, 0.4);
  }

  &:disabled {
    background: var(--surface-tertiary);
    color: var(--text-disabled);
    border-color: var(--border-light);
  }
}

@keyframes recording-pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);
  }
}

// 工具栏
.search-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-3);
  padding: 0 var(--space-4);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: var(--space-2);
}

// 装饰性元素
.search-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.decoration-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.4;
  animation: float 8s ease-in-out infinite;

  &.orb-1 {
    top: -20px;
    left: -30px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, var(--accent-cyan) 0%, transparent 70%);
    animation-delay: 0s;
  }

  &.orb-2 {
    bottom: -30px;
    right: -40px;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, var(--accent-magenta) 0%, transparent 70%);
    animation-delay: 2s;
  }
}

.decoration-line {
  position: absolute;
  background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
  height: 1px;
  opacity: 0.3;
  animation: line-slide 3s linear infinite;

  &.line-1 {
    top: 50%;
    left: -100px;
    right: -100px;
    transform: translateY(-50%);
    animation-delay: 0s;
  }

  &.line-2 {
    top: 50%;
    left: -100px;
    right: -100px;
    transform: translateY(-50%) rotate(90deg);
    animation-delay: 1s;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(10px, -10px) scale(1.1); }
}

@keyframes line-slide {
  0% { transform: translateX(-100%) translateY(-50%); }
  100% { transform: translateX(100%) translateY(-50%); }
}

// 响应式设计
@media (max-width: 768px) {
  .search-box {
    padding: var(--space-1);
  }

  .search-box-border {
    padding: var(--space-3);
    gap: var(--space-2);
  }

  .search-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .search-input {
    height: 40px;
    font-size: var(--text-base);
  }

  .action-btn {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .search-toolbar {
    flex-direction: column;
    gap: var(--space-2);
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }

  .decoration-orb {
    filter: blur(30px);

    &.orb-1 {
      width: 80px;
      height: 80px;
    }

    &.orb-2 {
      width: 100px;
      height: 100px;
    }
  }
}

@media (max-width: 480px) {
  .search-box-border {
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
  }

  .search-actions {
    width: 100%;
    justify-content: center;
  }

  .search-icon-area {
    order: -1;
  }

  .recording-timer {
    bottom: auto;
    top: calc(100% + var(--space-2));
  }
}

// 无障碍
@media (prefers-reduced-motion: reduce) {
  .search-box-border {
    transition: none;
  }

  .action-btn {
    transition: none;

    &:not(:disabled):hover {
      transform: none;
    }
  }

  .decoration-orb,
  .decoration-line {
    animation: none;
  }

  .voice-btn.recording {
    animation: none;
  }
}
</style>