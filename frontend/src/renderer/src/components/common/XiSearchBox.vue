<template>
  <div class="search-container">
    <!-- 多模态输入指示器 -->
    <div class="multimodal-indicators">
      <div
        class="indicator"
        :class="{ active: inputMode === 'text' }"
        @click="setInputMode('text')"
      >
        <XiIcon icon="lucide:keyboard" :size="24" />
        <span>•</span>
      </div>
      <div
        class="indicator"
        :class="{ active: inputMode === 'voice' }"
        @click="setInputMode('voice')"
      >
        <XiIcon icon="lucide:mic" :size="24" />
        <span>5</span>
      </div>
      <div
        class="indicator disabled"
        @click="setInputMode('image')"
      >
        <XiIcon icon="lucide:image" :size="24" />
        <span>✗</span>
      </div>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <div class="search-input-wrapper">
        <a-input
          v-model:value="searchQuery"
          placeholder="✨ 说出你的想法，或开始输入..."
          size="large"
          class="search-input"
          @press-enter="handleSearch"
        >
          <template #suffix>
            <span class="timer">⏱️ 30s</span>
          </template>
        </a-input>
      </div>

      <!-- 操作按钮 -->
      <div class="search-actions">
        <a-button type="primary" size="large" @click="handleSearch">
          <XiIcon icon="lucide:sparkles" :size="18" />
          智能搜索
        </a-button>
        <a-button size="large">
          <XiIcon icon="lucide:bar-chart-3" :size="18" />
          AI增强
        </a-button>
        <a-button size="large">
          <XiIcon icon="lucide:folder-open" :size="18" />
          选择目录
        </a-button>
      </div>
    </div>

    <!-- 搜索状态 -->
    <div class="search-status">
      <span>🎯 AI引擎: Ollama</span>
      <span>📊 搜索空间: 所有文件夹</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import XiIcon from './XiIcon.vue'

/**
 * 输入模式类型
 */
type InputMode = 'text' | 'voice' | 'image'

// 响应式数据
const inputMode = ref<InputMode>('text')
const searchQuery = ref('')

/**
 * 设置输入模式
 */
const setInputMode = (mode: InputMode) => {
  inputMode.value = mode
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  // 触发搜索事件
  console.log('搜索:', searchQuery.value)
}
</script>

<style scoped>
.search-container {
  max-width: 700px;
  margin: 0 auto;
}

.multimodal-indicators {
  display: flex;
  justify-content: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.indicator {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: var(--border-standard);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--text-secondary);
}

.indicator:hover {
  border-color: var(--brand-blue);
  background: var(--brand-blue-light);
}

.indicator.active {
  background: var(--brand-blue-light);
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 2px rgba(0, 117, 222, 0.2);
  color: var(--brand-blue);
}

.indicator.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-box {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-lg);
}

.search-input-wrapper {
  margin-bottom: var(--space-lg);
}

.search-input :deep(.ant-input) {
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.timer {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

.search-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.search-status {
  display: flex;
  justify-content: center;
  gap: var(--space-xl);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

@media (max-width: 768px) {
  .search-actions {
    flex-direction: column;
  }

  .search-status {
    flex-direction: column;
    gap: var(--space-sm);
  }
}
</style>
