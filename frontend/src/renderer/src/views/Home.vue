<template>
  <div class="home-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">小遥搜索</h1>
      <p class="page-subtitle">多模态智能搜索，让文件触手可及</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <!-- 多模态输入指示器 -->
      <div class="multimodal-indicators">
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'text' }"
          @click="setInputMode('text')"
          title="文本输入"
        >
          <FormOutlined />
          <span>•</span>
        </div>
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'voice' }"
          @click="setInputMode('voice')"
          title="语音输入"
        >
          <AudioOutlined />
          <span>5</span>
        </div>
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'image' }"
          @click="setInputMode('image')"
          title="图片输入"
        >
          <PictureOutlined />
          <span>✗</span>
        </div>
      </div>

      <!-- 搜索容器 -->
      <div class="search-container" :class="{ focused: isSearchFocused }">
        <div class="search-input-wrapper">
          <!-- 搜索输入框 -->
          <a-input
            v-if="inputMode === 'text'"
            v-model:value="searchQuery"
            placeholder="输入搜索内容..."
            size="large"
            class="search-input"
            @focus="isSearchFocused = true"
            @blur="handleSearchBlur"
            @press-enter="handleSearch"
            @input="handleSearchInput"
            :loading="isSearching"
          >
            <template #prefix>
              <SearchOutlined class="search-icon" />
            </template>
            <template #suffix>
              <a-button
                type="text"
                size="small"
                @click="showSearchOptions = !showSearchOptions"
                title="搜索选项"
              >
                <SettingOutlined />
              </a-button>
            </template>
          </a-input>

          <!-- 搜索建议下拉列表 -->
          <div v-if="showSuggestions && searchSuggestions.length > 0" class="search-suggestions">
            <div
              v-for="(suggestion, index) in searchSuggestions"
              :key="index"
              class="suggestion-item"
              @click="selectSuggestion(suggestion)"
            >
              <SearchOutlined class="suggestion-icon" />
              <span class="suggestion-text">{{ suggestion }}</span>
            </div>
          </div>

          <!-- 语音输入界面 -->
          <div v-if="inputMode === 'voice'" class="voice-input">
            <div class="voice-visualizer">
              <div class="voice-waves" v-if="isRecording">
                <div class="wave" v-for="i in 5" :key="i"></div>
              </div>
              <AudioOutlined v-else class="voice-icon" />
            </div>
            <div class="voice-text">
              {{ isRecording ? '正在录音...' : '点击开始语音输入' }}
            </div>
            <div class="voice-timer" v-if="isRecording">
              {{ formatTime(recordingTime) }}
            </div>
            <div class="voice-controls">
              <a-button
                :type="isRecording ? 'danger' : 'primary'"
                size="large"
                @click="toggleRecording"
              >
                <VideoCameraOutlined v-if="isRecording" />
                <AudioOutlined v-else />
                {{ isRecording ? '停止录音' : '开始录音' }}
              </a-button>
            </div>
          </div>

          <!-- 图片输入界面 -->
          <div v-if="inputMode === 'image'" class="image-input">
            <a-upload-dragger
              :show-upload-list="false"
              :before-upload="handleImageUpload"
              accept="image/*"
              class="image-uploader"
            >
              <p class="ant-upload-drag-icon">
                <PictureOutlined />
              </p>
              <p class="ant-upload-text">拖拽图片到此处，或点击选择</p>
              <p class="ant-upload-hint">
                支持 JPG、JPEG、PNG 格式，最大 10MB
              </p>
            </a-upload-dragger>
            <div v-if="uploadedImage" class="uploaded-image">
              <img :src="uploadedImage" alt="上传的图片" />
              <div class="image-overlay">
                <a-button type="primary" @click="analyzeImage">
                  <EyeOutlined />
                  开始分析
                </a-button>
                <a-button @click="clearImage">
                  <DeleteOutlined />
                  移除
                </a-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 搜索选项 -->
        <div v-if="showSearchOptions && inputMode === 'text'" class="search-options">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item label="搜索类型">
                <a-select v-model:value="searchOptions.searchType" style="width: 100%">
                  <a-select value="semantic">语义搜索</a-select>
                  <a-select value="fulltext">全文搜索</a-select>
                  <a-select value="hybrid">混合搜索</a-select>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="文件类型">
                <a-select
                  v-model:value="searchOptions.fileTypes"
                  mode="multiple"
                  style="width: 100%"
                >
                  <a-select value="document">文档</a-select>
                  <a-select value="audio">音频</a-select>
                  <a-select value="video">视频</a-select>
                  <a-select value="image">图片</a-select>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="相似度">
                <a-slider
                  v-model:value="searchOptions.threshold"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :tooltip-formatter="(value) => `${(value * 100).toFixed(0)}%`"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <!-- 搜索按钮组 -->
        <div class="search-actions">
          <a-button
            type="primary"
            size="large"
            @click="handleSearch"
            :loading="isSearching"
            :disabled="!canSearch"
          >
            <SearchOutlined />
            开始搜索
          </a-button>
          </div>
      </div>

    </div>

    <!-- 搜索结果 -->
    <div class="results-section" v-if="searchResults.length > 0 || isSearching">
      <div class="results-header">
        <h3 class="results-title">搜索结果</h3>
        <div class="results-stats">
          <span class="results-count">
            找到 {{ searchStats.total }} 个结果
          </span>
          <span class="results-time">
            耗时 {{ searchStats.searchTime?.toFixed(2) }}s
          </span>
        </div>
      </div>

      <!-- 结果列表 -->
      <div class="results-list">
        <a-spin :spinning="isSearching" size="large">
          <TransitionGroup name="result">
            <SearchResultCard
              v-for="result in searchResults"
              :key="result.file_id"
              :result="result"
              @open="handleOpen"
            />
          </TransitionGroup>
        </a-spin>
      </div>

      <!-- 加载更多 -->
      <div class="results-footer" v-if="searchResults.length < searchStats.total">
        <a-button type="link" @click="loadMore" :loading="isLoadingMore">
          加载更多结果
        </a-button>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!isSearching && hasSearched">
      <a-empty
        description="没有找到相关文件"
      >
        <template #image>
          <SearchOutlined style="font-size: 64px; color: var(--text-quaternary)" />
        </template>
        <a-button type="primary" @click="showAdvancedSearch">
          高级搜索
        </a-button>
      </a-empty>
    </div>

    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { SearchServiceMock } from '@/api/search'
import type { SearchResult, SearchType, FileType } from '@/types/api'
import SearchResultCard from '@/components/SearchResultCard.vue'
import {
  FormOutlined,
  AudioOutlined,
  PictureOutlined,
  SearchOutlined,
  SettingOutlined,
  VideoCameraOutlined,
  EyeOutlined,
  DeleteOutlined,
  RobotOutlined,
  DatabaseOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const inputMode = ref<'text' | 'voice' | 'image'>('text')
const isSearchFocused = ref(false)
const searchQuery = ref('')
const isSearching = ref(false)
const hasSearched = ref(false)
const showSearchOptions = ref(false)

// 搜索建议
const searchSuggestions = ref<string[]>([])
const showSuggestions = ref(false)
const suggestionTimer = ref<NodeJS.Timeout>()

// 语音录制
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingTimer = ref<NodeJS.Timeout>()

// 图片上传
const uploadedImage = ref<string>('')

// 搜索结果
const searchResults = ref<SearchResult[]>([])
const isLoadingMore = ref(false)

// 搜索选项
const searchOptions = reactive({
  searchType: 'hybrid' as SearchType,
  fileTypes: [] as FileType[],
  threshold: 0.7
})

// 搜索统计
const searchStats = reactive({
  total: 0,
  searchTime: 0
})

// 系统信息
const aiEngine = ref('Ollama')
const searchScope = ref('所有文件夹')


// 计算属性
const canSearch = computed(() => {
  switch (inputMode.value) {
    case 'text':
      return searchQuery.value.trim().length > 0
    case 'voice':
      return !isRecording.value
    case 'image':
      return uploadedImage.value !== ''
    default:
      return false
  }
})

// 设置输入模式
const setInputMode = (mode: 'text' | 'voice' | 'image') => {
  inputMode.value = mode
  // 清理之前的状态
  if (isRecording.value) {
    stopRecording()
  }
  if (uploadedImage.value) {
    clearImage()
  }
}

// 处理搜索
const handleSearch = async () => {
  if (!canSearch.value) return

  isSearching.value = true
  hasSearched.value = true

  try {
    const response = await SearchServiceMock.search({
      query: searchQuery.value,
      search_type: searchOptions.searchType,
      threshold: searchOptions.threshold,
      file_types: searchOptions.fileTypes,
      limit: 20
    })

    if (response.success) {
      searchResults.value = response.data.results
      searchStats.total = response.data.total
      searchStats.searchTime = response.data.search_time

      message.success(`找到 ${response.data.total} 个相关文件`)
    }
  } catch (error) {
    message.error('搜索失败，请重试')
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}

// 搜索建议相关
const handleSearchInput = () => {
  // 清除之前的定时器
  if (suggestionTimer.value) {
    clearTimeout(suggestionTimer.value)
  }

  // 如果搜索框获得焦点且有内容，显示建议
  if (isSearchFocused.value && searchQuery.value.trim()) {
    // 延迟200ms后获取搜索建议
    suggestionTimer.value = setTimeout(() => {
      fetchSearchSuggestions()
    }, 200)
  } else {
    showSuggestions.value = false
    searchSuggestions.value = []
  }
}

const handleSearchBlur = () => {
  // 延迟隐藏建议，让用户有机会点击建议项
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const fetchSearchSuggestions = async () => {
  if (!searchQuery.value.trim()) {
    showSuggestions.value = false
    searchSuggestions.value = []
    return
  }

  try {
    const response = await SearchServiceMock.getSuggestions(searchQuery.value, 5)

    if (response.success && response.data.suggestions.length > 0) {
      searchSuggestions.value = response.data.suggestions
      showSuggestions.value = true
    } else {
      showSuggestions.value = false
      searchSuggestions.value = []
    }
  } catch (error) {
    console.error('获取搜索建议失败:', error)
    showSuggestions.value = false
    searchSuggestions.value = []
  }
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  searchSuggestions.value = []

  // 自动触发搜索
  handleSearch()
}

// 语音录制相关
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  recordingTime.value = 0

  recordingTimer.value = setInterval(() => {
    recordingTime.value += 1
    if (recordingTime.value >= 30) {
      stopRecording()
      message.warning('录音时长达到上限(30秒)')
    }
  }, 1000)

  message.info('开始录音...')
}

const stopRecording = () => {
  isRecording.value = false
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
  }

  if (recordingTime.value > 0) {
    searchQuery.value = '语音转文字结果：AI技术发展趋势讨论'
    inputMode.value = 'text'
    message.success('语音转文字完成')
  }
}

// 图片上传相关
const handleImageUpload = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false // 阻止默认上传
}

const analyzeImage = async () => {
  if (!uploadedImage.value) return

  isSearching.value = true
  try {
    // 模拟图片分析
    await new Promise(resolve => setTimeout(resolve, 2000))
    searchQuery.value = '图片分析结果：技术架构图、产品原型设计'
    inputMode.value = 'text'
    await handleSearch()
  } catch (error) {
    message.error('图片分析失败')
  } finally {
    isSearching.value = false
  }
}

const clearImage = () => {
  uploadedImage.value = ''
}

// 搜索结果操作
const handleOpen = (result: SearchResult) => {
  message.success(`打开文件: ${result.file_name}`)
}



// 加载更多
const loadMore = async () => {
  isLoadingMore.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    // 模拟加载更多数据
    message.info('没有更多结果了')
  } finally {
    isLoadingMore.value = false
  }
}

// 高级搜索
const showAdvancedSearch = () => {
  showSearchOptions.value = true
}


// 工具函数
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 组件挂载
onMounted(() => {
  // 初始化
  // message.info('欢迎使用小遥搜索 v2.0')
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin: 0;
}

.search-section {
  margin-bottom: var(--space-8);
}

.multimodal-indicators {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.search-container {
  position: relative;
  margin-bottom: var(--space-4);
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  padding: var(--space-4) var(--space-6);
  font-size: 1.125rem;
  border-radius: var(--radius-2xl);
  border: 2px solid var(--border-light);
  transition: all var(--transition-base);
}

.search-input:focus {
  border-color: var(--primary-300);
  box-shadow: 0 0 0 3px var(--primary-100);
}

/* 搜索建议样式 */
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background-color var(--transition-base);
  border-bottom: 1px solid var(--border-lighter);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background-color: var(--surface-01);
}

.suggestion-icon {
  color: var(--text-secondary);
  margin-right: var(--space-2);
  font-size: 0.875rem;
}

.suggestion-text {
  color: var(--text-primary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.voice-input,
.image-input {
  text-align: center;
  padding: var(--space-8);
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-2xl);
  background: var(--surface-01);
}

.voice-visualizer {
  margin-bottom: var(--space-4);
}

.voice-waves {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-1);
  height: 40px;
}

.wave {
  width: 4px;
  background: var(--primary-500);
  border-radius: var(--radius-full);
  animation: wave 1s ease-in-out infinite;
}

.wave:nth-child(1) { animation-delay: 0s; height: 20px; }
.wave:nth-child(2) { animation-delay: 0.1s; height: 30px; }
.wave:nth-child(3) { animation-delay: 0.2s; height: 40px; }
.wave:nth-child(4) { animation-delay: 0.3s; height: 30px; }
.wave:nth-child(5) { animation-delay: 0.4s; height: 20px; }

@keyframes wave {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

.voice-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
}

.voice-text {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.voice-timer {
  font-size: 2rem;
  font-weight: 600;
  color: var(--primary-600);
  margin-bottom: var(--space-4);
}

.voice-controls {
  display: flex;
  justify-content: center;
}

.image-uploader {
  border: none !important;
  background: transparent !important;
}

.uploaded-image {
  margin-top: var(--space-4);
  position: relative;
  display: inline-block;
}

.uploaded-image img {
  max-width: 200px;
  max-height: 200px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-lg);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.uploaded-image:hover .image-overlay {
  opacity: 1;
}

.search-options {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--surface-02);
  border-radius: var(--radius-lg);
}

.search-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
  justify-content: center;
}

.search-status {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
}

.results-section {
  margin-top: var(--space-8);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.results-stats {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  color: var(--text-secondary);
}

.results-list {
  min-height: 200px;
}

.results-footer {
  text-align: center;
  margin-top: var(--space-6);
}

.empty-state {
  text-align: center;
  margin-top: var(--space-12);
}

/* 过渡动画 */
.result-enter-active,
.result-leave-active {
  transition: all var(--transition-base);
}

.result-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.result-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .search-actions {
    flex-direction: column;
  }

  .results-header {
    flex-direction: column;
    gap: var(--space-2);
    text-align: center;
  }

  .multimodal-indicators {
    gap: var(--space-2);
  }
}
</style>