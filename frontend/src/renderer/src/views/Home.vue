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
            @blur="isSearchFocused = false"
            @press-enter="handleSearch"
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
        <div v-if="showSearchOptions" class="search-options">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item label="搜索类型">
                <a-select v-model:value="searchOptions.searchType" style="width: 100%">
                  <a-select-option value="semantic">语义搜索</a-select-option>
                  <a-select-option value="fulltext">全文搜索</a-select-option>
                  <a-select-option value="hybrid">混合搜索</a-select-option>
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
                  <a-select-option value="document">文档</a-select-option>
                  <a-select-option value="audio">音频</a-select-option>
                  <a-select-option value="video">视频</a-select-option>
                  <a-select-option value="image">图片</a-select-option>
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
          <a-button size="large" @click="showFolderSelector = true">
            <FolderOutlined />
            选择目录
          </a-button>
        </div>
      </div>

      <!-- 搜索状态信息 -->
      <div class="search-status">
        <a-tag color="blue">
          <RobotOutlined />
          AI引擎: {{ aiEngine }}
        </a-tag>
        <a-tag color="green">
          <DatabaseOutlined />
          搜索范围: {{ searchScope }}
        </a-tag>
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

      <!-- 支持的文件格式信息 -->
      <div class="supported-formats" v-if="!isSearching">
        <a-alert
          message="支持的文件格式"
          type="info"
          show-icon
          closable
        >
          <template #description>
            <div class="formats-grid">
              <div class="format-category">
                <strong>📄 文档文件:</strong>
                <span>txt, md, pdf, docx, xlsx, pptx, doc, xls, ppt</span>
              </div>
              <div class="format-category">
                <strong>🎵 音频文件:</strong>
                <span>mp3, wav</span>
              </div>
              <div class="format-category">
                <strong>🎬 视频文件:</strong>
                <span>mp4, avi</span>
              </div>
              <div class="format-category">
                <strong>🖼️ 图片文件:</strong>
                <span>jpg, jpeg, png</span>
              </div>
            </div>
          </template>
        </a-alert>
      </div>

      <!-- 结果列表 -->
      <div class="results-list">
        <a-spin :spinning="isSearching" size="large">
          <TransitionGroup name="result">
            <SearchResultCard
              v-for="result in searchResults"
              :key="result.file_id"
              :result="result"
              @preview="handlePreview"
              @open="handleOpen"
              @favorite="handleFavorite"
              @delete="handleDelete"
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

    <!-- 文件夹选择器 -->
    <a-modal
      v-model:open="showFolderSelector"
      title="选择搜索目录"
      @ok="handleFolderSelect"
    >
      <a-list
        :data-source="recentFolders"
        item-layout="horizontal"
        size="small"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <a-checkbox
                  :checked="selectedFolders.includes(item.path)"
                  @change="handleFolderCheck(item.path)"
                >
                  {{ item.name }}
                </a-checkbox>
              </template>
              <template #description>
                {{ item.path }}
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
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
  FolderOutlined,
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
const showFolderSelector = ref(false)
const selectedFolders = ref<string[]>([])

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

// 最近使用的文件夹列表
const recentFolders = ref([
  { name: '文档', path: 'D:\\Documents' },
  { name: '下载', path: 'D:\\Downloads' },
  { name: '工作项目', path: 'D:\\Work\\Projects' },
  { name: '桌面', path: 'D:\\Desktop' }
])

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
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 模拟搜索结果
    const mockResults: SearchResult[] = [
      {
        file_id: 1,
        file_name: '技术方案文档.md',
        file_path: 'D:\\Documents\\Projects\\技术方案文档.md',
        file_type: 'document',
        relevance_score: 0.95,
        preview_text: '这是一个关于小遥搜索技术方案的文档，包含了详细的架构设计和实现细节...',
        highlight: '这是一个关于<em>小遥搜索</em>技术方案的文档，包含了详细的架构设计和实现细节...',
        created_at: '2024-01-15T10:30:00Z',
        modified_at: '2024-01-20T15:45:00Z',
        file_size: 1024000,
        match_type: 'semantic'
      },
      {
        file_id: 2,
        file_name: '项目需求文档.pdf',
        file_path: 'D:\\Documents\\Projects\\项目需求文档.pdf',
        file_type: 'document',
        relevance_score: 0.87,
        preview_text: '产品需求文档，详细描述了小遥搜索的功能特性和用户需求...',
        highlight: '产品需求文档，详细描述了<em>小遥搜索</em>的功能特性和用户需求...',
        created_at: '2024-01-10T09:15:00Z',
        modified_at: '2024-01-18T14:20:00Z',
        file_size: 2048000,
        match_type: 'hybrid'
      }
    ]

    searchResults.value = mockResults
    searchStats.total = mockResults.length
    searchStats.searchTime = 1.5

    message.success(`找到 ${mockResults.length} 个相关文件`)
  } catch (error) {
    message.error('搜索失败，请重试')
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
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
const handlePreview = (result: SearchResult) => {
  message.info(`预览文件: ${result.file_name}`)
}

const handleOpen = (result: SearchResult) => {
  message.success(`打开文件: ${result.file_name}`)
}

const handleFavorite = (result: SearchResult, isFavorite: boolean) => {
  message.success(`${isFavorite ? '已收藏' : '已取消收藏'}: ${result.file_name}`)
}

const handleDelete = (result: SearchResult) => {
  message.warning(`删除功能暂未实现`)
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

// 文件夹选择
const handleFolderCheck = (folderPath: string) => {
  const index = selectedFolders.value.indexOf(folderPath)
  if (index > -1) {
    selectedFolders.value.splice(index, 1)
  } else {
    selectedFolders.value.push(folderPath)
  }
}

const handleFolderSelect = () => {
  if (selectedFolders.value.length > 0) {
    searchScope.value = `${selectedFolders.value.length} 个文件夹`
    message.success('搜索范围已更新')
  }
  showFolderSelector.value = false
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
  message.info('欢迎使用小遥搜索 v2.0')
})
  SettingOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const isSearchFocused = ref(false)
const searchQuery = ref('')
const isSearching = ref(false)
const hasSearched = ref(false)
const showSearchOptions = ref(false)

// 搜索结果
const searchResults = ref<SearchResult[]>([])

// 搜索选项
const searchOptions = reactive({
  searchType: 'hybrid' as SearchType,
  threshold: 0.7
})

// 搜索统计
const searchStats = reactive({
  total: 0,
  searchTime: 0
})

// 计算属性
const canSearch = computed(() => {
  return searchQuery.value.trim().length > 0
})

// 处理搜索
const handleSearch = async () => {
  if (!canSearch.value) return

  isSearching.value = true
  hasSearched.value = true

  try {
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 模拟搜索结果
    const mockResults: SearchResult[] = [
      {
        file_id: 1,
        file_name: '技术方案文档.md',
        file_path: 'D:\\Documents\\Projects\\技术方案文档.md',
        file_type: 'document',
        relevance_score: 0.95,
        preview_text: '这是一个关于小遥搜索技术方案的文档，包含了详细的架构设计和实现细节...',
        highlight: '这是一个关于<em>小遥搜索</em>技术方案的文档，包含了详细的架构设计和实现细节...',
        created_at: '2024-01-15T10:30:00Z',
        modified_at: '2024-01-20T15:45:00Z',
        file_size: 1024000,
        match_type: 'semantic'
      },
      {
        file_id: 2,
        file_name: '项目需求文档.pdf',
        file_path: 'D:\\Documents\\Projects\\项目需求文档.pdf',
        file_type: 'document',
        relevance_score: 0.87,
        preview_text: '产品需求文档，详细描述了小遥搜索的功能特性和用户需求...',
        highlight: '产品需求文档，详细描述了<em>小遥搜索</em>的功能特性和用户需求...',
        created_at: '2024-01-10T09:15:00Z',
        modified_at: '2024-01-18T14:20:00Z',
        file_size: 2048000,
        match_type: 'hybrid'
      }
    ]

    searchResults.value = mockResults
    searchStats.total = mockResults.length
    searchStats.searchTime = 1.5

    message.success(`找到 ${mockResults.length} 个相关文件`)
  } catch (error) {
    message.error('搜索失败，请重试')
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}

// 搜索结果操作
const handlePreview = (result: SearchResult) => {
  message.info(`预览文件: ${result.file_name}`)
}

const handleOpen = (result: SearchResult) => {
  message.success(`打开文件: ${result.file_name}`)
}

const handleFavorite = (result: SearchResult, isFavorite: boolean) => {
  message.success(`${isFavorite ? '已收藏' : '已取消收藏'}: ${result.file_name}`)
}

const handleDelete = (result: SearchResult) => {
  message.warning(`删除功能暂未实现`)
}
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

.supported-formats {
  margin-bottom: var(--space-8);
}

.formats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.format-category {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.format-category strong {
  color: var(--text-primary);
}

.format-category span {
  color: var(--text-secondary);
  font-size: 0.875rem;
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

  .formats-grid {
    grid-template-columns: 1fr;
  }
}
</style>