<template>
  <div class="home-page">
    <!-- 主搜索区域 -->
    <div class="search-section">
      <div class="search-container">
        <!-- 多模态悬浮指示器 -->
        <MultiModalIndicator
          :active-mode="activeInputMode"
          :is-recording="isRecording"
          @mode-change="handleModeChange"
          @voice-toggle="handleVoiceToggle"
        />

        <!-- 悬浮式搜索框 -->
        <FloatingSearchBox
          v-model="searchQuery"
          :active-mode="activeInputMode"
          :is-recording="isRecording"
          :recording-time="recordingTime"
          :suggestions="searchSuggestions"
          :is-loading="isSearching"
          @search="handleSearch"
          @voice-toggle="handleVoiceToggle"
          @file-upload="handleFileUpload"
          @suggestion-select="handleSuggestionSelect"
        />

        <!-- 搜索状态指示器 -->
        <div class="search-status" v-if="searchStats.total > 0 || isSearching">
          <div class="status-left">
            <span class="ai-engine">●AI引擎: {{ currentAIEngine }}</span>
            <span class="search-space">●搜索空间: {{ searchSpace }}</span>
          </div>
          <div class="status-right">
            <span v-if="isSearching" class="loading-indicator">
              <SimpleIcon type="loading" />
              正在搜索...
            </span>
            <span v-else-if="searchStats.total > 0" class="result-count">
              🎯 找到 {{ searchStats.total }} 个结果 ⚡ 耗时 {{ searchStats.searchTime }}s
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果区域 -->
    <div class="results-section" v-if="searchResults.length > 0 || isSearching">
      <div class="results-container">
        <!-- 搜索结果网格 -->
        <div class="results-grid" :class="{ 'loading': isSearching }">
          <!-- 加载骨架屏 -->
          <template v-if="isSearching">
            <ResultCardSkeleton
              v-for="i in 6"
              :key="`skeleton-${i}`"
            />
          </template>

          <!-- 搜索结果卡片 -->
          <ResultCard
            v-for="(result, index) in searchResults"
            :key="result.file_id"
            :result="result"
            :index="index"
            @preview="handlePreview"
            @open="handleOpenFile"
            @favorite="handleToggleFavorite"
            @delete="handleDelete"
          />
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="searchResults.length > 0 && hasMore">
          <a-button
            type="primary"
            ghost
            size="large"
            :loading="isLoadingMore"
            @click="handleLoadMore"
          >
            加载更多结果
          </a-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!isSearching && !hasSearched">
      <div class="empty-content">
        <div class="empty-icon">🔍</div>
        <h2 class="empty-title">开始你的智能搜索之旅</h2>
        <p class="empty-description">
          使用语音、文本或图片进行搜索，小遥搜索将为你快速找到相关文件
        </p>
        <div class="empty-actions">
          <a-button type="primary" size="large" @click="focusSearch">
            开始搜索
          </a-button>
          <a-button size="large" ghost @click="$router.push('/index')">
            管理索引
          </a-button>
        </div>
      </div>
    </div>

    <!-- 无结果状态 -->
    <div class="no-results" v-else-if="!isSearching && hasSearched && searchResults.length === 0">
      <div class="no-results-content">
        <div class="no-results-icon">🔍</div>
        <h3 class="no-results-title">未找到相关文件</h3>
        <p class="no-results-description">
          尝试使用不同的关键词或检查索引文件夹是否包含相关文件
        </p>
        <div class="no-results-actions">
          <a-button @click="focusSearch">重新搜索</a-button>
          <a-button type="link" @click="$router.push('/index')">
            管理索引
          </a-button>
        </div>
      </div>
    </div>

    <!-- 底部统计信息 -->
    <div class="footer-stats" v-if="indexStats">
      <div class="stats-container">
        <span class="stat-item">
          📊 已索引: {{ formatNumber(indexStats.indexedFiles) }}文件
        </span>
        <span class="stat-item">
          💾 数据: {{ formatFileSize(indexStats.totalSize) }}
        </span>
        <span class="stat-item">
          🔍 今日: {{ indexStats.todaySearches }}次搜索
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'
import { useAppStore } from '@/stores/useAppStore'
import { useSearchStore } from '@/stores/useSearchStore'
import MultiModalIndicator from '@/components/search/MultiModalIndicator.vue'
import FloatingSearchBox from '@/components/search/FloatingSearchBox.vue'
import ResultCard from '@/components/search/ResultCard.vue'
import ResultCardSkeleton from '@/components/search/ResultCardSkeleton.vue'
import type { SearchResult, SearchRequest, InputType } from '@/types/api'

// Store
const appStore = useAppStore()
const searchStore = useSearchStore()

// 响应式数据
const searchQuery = ref('')
const activeInputMode = ref<InputType>('text')
const isRecording = ref(false)
const recordingTime = ref(0)
const isSearching = ref(false)
const hasSearched = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(false)

// 计算属性
const searchResults = computed(() => searchStore.results)
const searchSuggestions = computed(() => searchStore.suggestions)
const searchStats = computed(() => searchStore.searchStats)
const indexStats = computed(() => searchStore.indexStats)
const currentAIEngine = computed(() => searchStore.currentAIEngine)
const searchSpace = computed(() => searchStore.searchSpace)

// 录音计时器
let recordingTimer: number | null = null

// 处理搜索
const handleSearch = async (query: string, inputType: InputType = 'text') => {
  if (!query.trim()) {
    message.warning('请输入搜索内容')
    return
  }

  try {
    isSearching.value = true
    hasSearched.value = true

    const searchRequest: SearchRequest = {
      query: query.trim(),
      input_type: inputType,
      search_type: 'hybrid',
      limit: 20,
      threshold: 0.7
    }

    const response = await searchStore.search(searchRequest)

    if (response.success) {
      // 添加到搜索历史
      appStore.addSearchHistory(query, inputType, response.data.total)

      // 检查是否有更多结果
      hasMore.value = response.data.total > searchRequest.limit!

      message.success(`找到 ${response.data.total} 个相关文件`)
    } else {
      message.error('搜索失败，请重试')
    }
  } catch (error) {
    console.error('搜索错误:', error)
    message.error('搜索失败，请检查网络连接')
  } finally {
    isSearching.value = false
  }
}

// 处理语音录制
const handleVoiceToggle = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  recordingTime.value = 0

  // 开始计时
  recordingTimer = window.setInterval(() => {
    recordingTime.value += 1
    // 最多录制30秒
    if (recordingTime.value >= 30) {
      stopRecording()
    }
  }, 1000)

  // 这里应该启动实际的录音功能
  console.log('开始录音...')
}

const stopRecording = () => {
  isRecording.value = false

  if (recordingTimer) {
    clearInterval(recordingTimer)
    recordingTimer = null
  }

  // 这里应该停止录音并进行语音识别
  console.log('停止录音，进行识别...')

  // 模拟语音识别结果
  const mockText = '人工智能发展趋势'
  searchQuery.value = mockText
  handleSearch(mockText, 'voice')
}

// 处理文件上传
const handleFileUpload = async (file: File) => {
  const isImage = file.type.startsWith('image/')
  const inputType: InputType = isImage ? 'image' : 'voice'

  try {
    isSearching.value = true
    hasSearched.value = true

    const response = await searchStore.multimodalSearch(inputType, file)

    if (response.success) {
      // 添加到搜索历史
      appStore.addSearchHistory(
        response.data.converted_text || file.name,
        inputType,
        response.data.search_results.length
      )

      hasMore.value = response.data.search_results.length >= 20

      if (response.data.converted_text) {
        message.success(`${inputType === 'voice' ? '语音识别' : '图片识别'}: "${response.data.converted_text}"`)
      } else {
        message.success(`找到 ${response.data.search_results.length} 个相关文件`)
      }
    } else {
      message.error('搜索失败，请重试')
    }
  } catch (error) {
    console.error('多模态搜索错误:', error)
    message.error('搜索失败，请检查文件格式')
  } finally {
    isSearching.value = false
  }
}

// 处理输入模式切换
const handleModeChange = (mode: InputType) => {
  activeInputMode.value = mode
}

// 处理搜索建议选择
const handleSuggestionSelect = (suggestion: string) => {
  searchQuery.value = suggestion
  handleSearch(suggestion)
}

// 处理结果预览
const handlePreview = (result: SearchResult) => {
  // 实现文件预览功能
  console.log('预览文件:', result.file_path)
  // 这里可以打开预览模态框
}

// 处理打开文件
const handleOpenFile = (result: SearchResult) => {
  // 实现打开文件功能
  console.log('打开文件:', result.file_path)
  // 这里可以调用系统API打开文件
}

// 处理收藏切换
const handleToggleFavorite = (result: SearchResult) => {
  // 实现收藏功能
  console.log('切换收藏:', result.file_id)
  // 这里可以调用收藏API
}

// 处理删除
const handleDelete = (result: SearchResult) => {
  // 实现删除功能
  console.log('删除文件:', result.file_id)
  // 这里可以调用删除API
}

// 处理加载更多
const handleLoadMore = async () => {
  if (isLoadingMore.value || !searchQuery.value) return

  try {
    isLoadingMore.value = true

    const currentCount = searchResults.value.length
    const response = await searchStore.loadMore(searchQuery.value, currentCount)

    if (response.success) {
      hasMore.value = response.data.total > searchResults.value.length
    } else {
      message.error('加载更多失败')
    }
  } catch (error) {
    console.error('加载更多错误:', error)
    message.error('加载更多失败')
  } finally {
    isLoadingMore.value = false
  }
}

// 聚焦搜索框
const focusSearch = () => {
  appStore.setSearchFocus(true)
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
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

// 监听搜索框焦点状态
watch(() => appStore.searchFocus, (focused) => {
  if (focused) {
    // 聚焦时可以显示搜索建议
  }
})

// 生命周期
onMounted(async () => {
  // 初始化搜索相关数据
  await searchStore.initializeSearch()

  // 监听键盘快捷键
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // 清理监听器
  document.removeEventListener('keydown', handleKeydown)

  // 清理录音计时器
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
})

// 键盘快捷键处理
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + K 聚焦搜索框
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    focusSearch()
  }

  // Enter 执行搜索
  if (event.key === 'Enter' && searchQuery.value.trim()) {
    handleSearch(searchQuery.value)
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: var(--space-6);
  overflow: hidden;
  position: relative;
}

// 搜索区域
.search-section {
  flex-shrink: 0;
  margin-bottom: var(--space-8);
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.search-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-4);
  padding: 0 var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-tertiary);

  .status-left,
  .status-right {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .loading-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--accent-cyan);
  }

  .result-count {
    color: var(--text-secondary);
  }
}

// 结果区域
.results-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.results-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-4);
  @include custom-scrollbar;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: var(--space-6);
  padding: var(--space-4) 0;

  &.loading {
    opacity: 0.7;
  }
}

.load-more {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

// 空状态
.empty-state,
.no-results {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-content,
.no-results-content {
  max-width: 500px;
  padding: var(--space-12);
}

.empty-icon,
.no-results-icon {
  font-size: 80px;
  margin-bottom: var(--space-6);
  opacity: 0.6;
}

.empty-title,
.no-results-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-4);
  color: var(--text-primary);
}

.empty-description,
.no-results-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin-bottom: var(--space-8);
  line-height: 1.6;
}

.empty-actions,
.no-results-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

// 底部统计
.footer-stats {
  flex-shrink: 0;
  padding: var(--space-4) 0;
  border-top: 1px solid var(--border-light);
  margin-top: var(--space-6);
}

.stats-container {
  display: flex;
  justify-content: center;
  gap: var(--space-8);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

// 响应式设计
@media (max-width: 768px) {
  .home-page {
    padding: var(--space-4);
  }

  .search-status {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }

  .results-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .stats-container {
    flex-direction: column;
    gap: var(--space-2);
    text-align: center;
  }

  .empty-actions,
  .no-results-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .empty-icon,
  .no-results-icon {
    font-size: 60px;
  }

  .empty-title,
  .no-results-title {
    font-size: var(--text-2xl);
  }

  .empty-description,
  .no-results-description {
    font-size: var(--text-base);
  }
}
</style>