<template>
  <div id="app" class="app" :class="{ 'high-contrast': settings.highContrast }">
    <!-- 应用头部 -->
    <header class="app-header">
      <div class="header-content">
        <div class="app-title">
          <h1 class="title-text">
            <span class="title-symbol">◤</span>
            <span class="title-name">小遥搜索</span>
            <span class="title-symbol">◢</span>
          </h1>
          <span class="app-version">v2.0</span>
        </div>

        <nav class="main-nav" role="navigation" aria-label="主导航">
          <button
            v-for="page in navigationPages"
            :key="page.key"
            :class="['nav-item', { active: currentPage === page.key }]"
            @click="setCurrentPage(page.key)"
            :aria-current="currentPage === page.key ? 'page' : undefined"
            :title="page.title"
          >
            <span class="nav-icon">{{ page.icon }}</span>
            <span class="nav-text">{{ page.name }}</span>
          </button>
        </nav>

        <div class="header-actions">
          <button
            class="action-btn notification"
            @click="toggleNotifications"
            title="通知"
            aria-label="查看通知"
          >
            <span class="btn-icon">🔔</span>
            <span v-if="hasNotifications" class="notification-badge">2</span>
          </button>
          <button
            class="action-btn"
            @click="toggleTheme"
            :title="settings.theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'"
            :aria-label="settings.theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'"
          >
            <span class="btn-icon">{{ settings.theme === 'dark' ? '🌙' : '☀️' }}</span>
          </button>
          <button
            class="action-btn"
            @click="toggleAnimations"
            :title="settings.animations ? '禁用动画' : '启用动画'"
            :aria-label="settings.animations ? '禁用动画' : '启用动画'"
          >
            <span class="btn-icon">🎨</span>
          </button>
          <button
            class="action-btn user"
            @click="showUserMenu"
            title="用户菜单"
            aria-label="用户菜单"
          >
            <span class="btn-icon">👤</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content" role="main">
      <!-- 跳转到内容的链接 -->
      <a href="#main-content" class="skip-link">跳转到主要内容</a>

      <div id="main-content" class="content-wrapper">
        <!-- 首页 -->
        <transition name="page" mode="out-in">
          <div v-if="currentPage === 'home'" key="home" class="page home-page">
            <!-- AI引擎和搜索空间状态 -->
            <div class="search-status">
              <div class="status-item">
                <span class="status-icon">●</span>
                <span class="status-label">AI引擎:</span>
                <span class="status-value">{{ settings.aiEngine.name }}</span>
              </div>
              <div class="status-item">
                <span class="status-icon">●</span>
                <span class="status-label">模型:</span>
                <span class="status-value">{{ settings.aiEngine.model || 'qwen2.5:7b' }}</span>
              </div>
              <div class="status-item">
                <span class="status-icon">●</span>
                <span class="status-label">搜索范围:</span>
                <span class="status-value">{{ settings.searchScope[0] }}</span>
              </div>
            </div>

            <!-- 多模态指示器 -->
            <MultiModalIndicator
              :voice-activity="isRecording ? recordingActivity : undefined"
              @mode-change="handleModeChange"
            />

            <!-- 悬浮式搜索框 -->
            <FloatingSearchBox
              @search="handleSearch"
              @voice-toggle="handleVoiceToggle"
              @text-mode="handleTextMode"
              @image-mode="handleImageMode"
              @ai-enhance="handleAIEnhance"
            />

            <!-- 搜索结果区域 -->
            <div v-if="hasSearched" class="search-results">
              <!-- 搜索统计信息 -->
              <div class="search-stats">
                <div class="stats-left">
                  <span class="result-count">
                    <span class="stats-icon">🎯</span>
                    找到 {{ resultsCount }} 个结果
                  </span>
                  <span class="search-time">
                    <span class="stats-icon">⚡</span>
                    耗时 {{ formattedSearchTime }}
                  </span>
                </div>
                <div v-if="search.isSearching" class="search-status">
                  <span class="status-icon">🔄</span>
                  正在分析相似文件...
                </div>
              </div>

              <!-- 结果列表 -->
              <div class="results-container">
                <transition-group name="result" tag="div" class="results-grid">
                  <ResultCard
                    v-for="(result, index) in search.results"
                    :key="result.id"
                    :result="result"
                    :is-highlighted="index === 0"
                    @preview="handlePreview"
                    @open="handleOpen"
                    @favorite="handleFavorite"
                    @delete="handleDelete"
                  />
                </transition-group>
              </div>

              <!-- 空状态 -->
              <div v-if="!hasResults && !search.isSearching" class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3 class="empty-title">未找到相关文件</h3>
                <p class="empty-description">
                  尝试使用不同的关键词或调整搜索范围
                </p>
                <button class="empty-action" @click="clearSearch">
                  清空搜索
                </button>
              </div>
            </div>
          </div>

          <!-- 设置页面 -->
          <div v-else-if="currentPage === 'settings'" key="settings" class="page settings-page">
            <h2 class="page-title">设置</h2>
            <div class="settings-content">
              <p class="settings-coming-soon">
                设置功能正在开发中...
              </p>
            </div>
          </div>

          <!-- 索引管理页面 -->
          <div v-else-if="currentPage === 'index'" key="index" class="page index-page">
            <h2 class="page-title">索引管理</h2>
            <div class="index-content">
              <p class="index-coming-soon">
                索引管理功能正在开发中...
              </p>
            </div>
          </div>

          <!-- 帮助页面 -->
          <div v-else-if="currentPage === 'help'" key="help" class="page help-page">
            <h2 class="page-title">帮助与关于</h2>
            <div class="help-content">
              <p class="help-coming-soon">
                帮助文档正在完善中...
              </p>
            </div>
          </div>
        </transition>
      </div>
    </main>

    <!-- 应用底部 -->
    <footer class="app-footer">
      <div class="footer-content">
        <div class="system-stats">
          <span class="stat-item">
            <span class="stat-icon">📊</span>
            索引: {{ systemStats.indexedFiles.toLocaleString() }}文件
          </span>
          <span class="stat-item">
            <span class="stat-icon">💾</span>
            数据: {{ systemStats.dataSize }}
          </span>
          <span class="stat-item">
            <span class="stat-icon">🔍</span>
            今日: {{ systemStats.totalSearches }}次搜索
          </span>
        </div>
        <div class="footer-info">
          <span class="version-info">小遥搜索 v2.0 - 高保真原型</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/useAppStore'
import MultiModalIndicator from '@/components/MultiModalIndicator.vue'
import FloatingSearchBox from '@/components/FloatingSearchBox.vue'
import ResultCard from '@/components/ResultCard.vue'
import type { SearchResult, InputMode } from '@/types'

const appStore = useAppStore()
const {
  currentPage,
  search,
  settings,
  systemStats,
  hasResults,
  resultsCount,
  formattedSearchTime,
  hasSearched,
  isRecording
} = storeToRefs(appStore)

const recordingActivity = ref(0)
const hasNotifications = ref(true)

// 导航页面配置
const navigationPages = [
  { key: 'home', name: '首页', icon: '●', title: '返回主页' },
  { key: 'settings', name: '设置', icon: '◆', title: '应用设置' },
  { key: 'index', name: '索引', icon: '◆', title: '索引管理' },
  { key: 'help', name: '帮助', icon: '◆', title: '帮助文档' }
]

// 页面切换
const setCurrentPage = (page: typeof currentPage.value) => {
  appStore.setCurrentPage(page)
}

// 处理模式变化
const handleModeChange = (mode: InputMode) => {
  console.log('切换到模式:', mode)
}

// 处理搜索
const handleSearch = () => {
  console.log('执行搜索:', search.value.query)
}

// 处理语音录制
const handleVoiceToggle = () => {
  if (isRecording.value) {
    appStore.stopVoiceRecording()
  } else {
    appStore.startVoiceRecording()
    // 模拟录音活动变化
    const interval = setInterval(() => {
      if (!isRecording.value) {
        clearInterval(interval)
        return
      }
      recordingActivity.value = Math.floor(Math.random() * 10) + 1
    }, 200)
  }
}

// 切换到文本模式
const handleTextMode = () => {
  appStore.setInputMode('text')
}

// 切换到图片模式
const handleImageMode = () => {
  appStore.setInputMode('image')
}

// AI增强分析
const handleAIEnhance = () => {
  console.log('AI增强分析')
}

// 结果操作
const handlePreview = (result: SearchResult) => {
  console.log('预览文件:', result.name)
}

const handleOpen = (result: SearchResult) => {
  console.log('打开文件:', result.path)
}

const handleFavorite = (result: SearchResult) => {
  console.log('收藏文件:', result.name)
}

const handleDelete = (result: SearchResult) => {
  console.log('删除文件:', result.name)
}

// 清空搜索
const clearSearch = () => {
  appStore.clearResults()
}

// 头部操作
const toggleNotifications = () => {
  console.log('切换通知面板')
}

const toggleTheme = () => {
  const newTheme = settings.value.theme === 'dark' ? 'light' : 'dark'
  appStore.updateSettings({ theme: newTheme })
  document.documentElement.setAttribute('data-theme', newTheme)
}

const toggleAnimations = () => {
  const newAnimations = !settings.value.animations
  appStore.updateSettings({ animations: newAnimations })
}

const showUserMenu = () => {
  console.log('显示用户菜单')
}

// 键盘快捷键
const handleKeyDown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + K 聚焦搜索框
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    // 聚焦到搜索框
    const searchInput = document.querySelector('.search-input') as HTMLInputElement
    searchInput?.focus()
  }

  // Escape 清空搜索
  if (event.key === 'Escape') {
    if (search.value.query) {
      clearSearch()
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  document.documentElement.setAttribute('data-theme', settings.value.theme)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped lang="scss">
.app {
  min-height: 100vh;
  background: var(--surface-primary);
  color: var(--text-primary);
  font-family: var(--font-body);
  position: relative;
  overflow-x: hidden;
}

.app-header {
  background: var(--surface-secondary);
  border-bottom: 1px solid var(--border-primary);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(10px);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-6);
}

.app-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.title-text {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-artistic);
}

.title-symbol {
  color: var(--accent-cyan);
  font-size: var(--text-xl);
}

.app-version {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  background: var(--surface-quaternary);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-primary);
}

.main-nav {
  display: flex;
  gap: var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-base);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--text-sm);
  font-weight: 500;

  &:hover {
    background: var(--surface-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-light);
    color: var(--text-primary);
    border-color: var(--accent-cyan);
  }

  &:focus-visible {
    outline: 2px solid var(--accent-cyan);
    outline-offset: 2px;
  }
}

.nav-icon {
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-base);
  background: var(--surface-tertiary);
  border: 1px solid var(--border-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &:hover {
    background: var(--primary-light);
    color: var(--text-primary);
    border-color: var(--accent-cyan);
  }

  &:focus-visible {
    outline: 2px solid var(--accent-cyan);
    outline-offset: 2px;
  }
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--accent-magenta);
  color: white;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  min-width: 18px;
  text-align: center;
  border: 2px solid var(--surface-secondary);
}

.main-content {
  flex: 1;
  min-height: calc(100vh - 140px);
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-core);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: var(--z-modal);
  border-radius: var(--radius-base);
  transition: top var(--transition-fast);

  &:focus {
    top: 6px;
  }
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

.page {
  min-height: 400px;
}

.home-page {
  .search-status {
    display: flex;
    justify-content: center;
    gap: var(--space-8);
    margin-bottom: var(--space-6);
    flex-wrap: wrap;

    @media (max-width: 768px) {
      gap: var(--space-4);
    }
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--text-secondary);

    .status-icon {
      color: var(--accent-cyan);
      font-size: 8px;
    }

    .status-label {
      color: var(--text-tertiary);
    }

    .status-value {
      color: var(--text-primary);
      font-weight: 600;
    }
  }

  .search-results {
    margin-top: var(--space-12);
  }

  .search-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding: var(--space-4) var(--space-6);
    background: var(--surface-tertiary);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-primary);
  }

  .stats-left {
    display: flex;
    gap: var(--space-6);
  }

  .result-count,
  .search-time {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--text-secondary);
  }

  .stats-icon {
    font-size: 14px;
  }

  .search-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--accent-cyan);
  }

  .status-icon {
    animation: spin 1s linear infinite;
  }

  .results-container {
    min-height: 200px;
  }

  .empty-state {
    text-align: center;
    padding: var(--space-16) var(--space-8);
    color: var(--text-secondary);
  }

  .empty-icon {
    font-size: 64px;
    margin-bottom: var(--space-6);
    opacity: 0.5;
  }

  .empty-title {
    font-size: var(--text-xl);
    margin-bottom: var(--space-4);
    color: var(--text-primary);
  }

  .empty-description {
    font-size: var(--text-base);
    margin-bottom: var(--space-6);
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }

  .empty-action {
    padding: var(--space-3) var(--space-6);
    background: var(--primary-light);
    color: var(--text-primary);
    border: 1px solid var(--accent-cyan);
    border-radius: var(--radius-base);
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--primary-core);
      transform: translateY(-1px);
    }
  }
}

.page-title {
  font-size: var(--text-3xl);
  margin-bottom: var(--space-6);
  color: var(--text-primary);
}

.app-footer {
  background: var(--surface-secondary);
  border-top: 1px solid var(--border-primary);
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.system-stats {
  display: flex;
  gap: var(--space-6);
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.stat-icon {
  font-size: 12px;
}

.footer-info {
  font-size: var(--text-xs);
  color: var(--text-quaternary);
}

// 页面切换动画
.page-enter-active,
.page-leave-active {
  transition: all var(--transition-slow);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(1.05);
}

// 结果卡片动画
.result-enter-active {
  transition: all var(--transition-normal);
}

.result-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

// 动画定义
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 高对比度模式
:deep(.high-contrast) {
  .nav-item,
  .action-btn {
    border-width: 2px;
  }

  .result-count,
  .search-time {
    font-weight: 600;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header-content {
    padding: var(--space-3) var(--space-4);
    flex-wrap: wrap;
    gap: var(--space-4);
  }

  .app-title {
    order: 1;
    flex: 1;
  }

  .main-nav {
    order: 2;
    flex: 1;
    justify-content: center;
  }

  .header-actions {
    order: 3;
  }

  .content-wrapper {
    padding: var(--space-6) var(--space-4);
  }

  .footer-content {
    padding: var(--space-3) var(--space-4);
    flex-direction: column;
    text-align: center;
  }

  .system-stats {
    justify-content: center;
  }
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition: none;
  }

  .result-enter-active {
    transition: none;
  }

  .search-status .status-icon {
    animation: none;
  }
}
</style>