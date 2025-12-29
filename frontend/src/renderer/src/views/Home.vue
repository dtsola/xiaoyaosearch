<template>
  <div class="home-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">{{ t('home.title') }}</h1>
      <p class="page-subtitle">{{ t('home.subtitle') }}</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <!-- 多模态输入指示器 -->
      <div class="multimodal-indicators">
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'text' }"
          @click="setInputMode('text')"
          :title="t('home.textInput')"
        >
          <FormOutlined />
          <span>•</span>
        </div>
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'voice' }"
          @click="setInputMode('voice')"
          :title="t('home.voiceInput')"
        >
          <AudioOutlined />
          <span>5</span>
        </div>
        <div
          class="multimodal-indicator"
          :class="{ active: inputMode === 'image' }"
          @click="setInputMode('image')"
          :title="t('home.imageInput')"
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
            :placeholder="t('home.searchPlaceholder')"
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
                :title="t('search.options')"
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
              {{ isRecording ? t('home.recording') : t('home.clickToRecord') }}
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
                {{ isRecording ? t('home.stopRecording') : t('home.startRecording') }}
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
              <p class="ant-upload-text">{{ t('home.dragImageHere') }}</p>
              <p class="ant-upload-hint">
                {{ t('home.supportImageFormats') }}
              </p>
            </a-upload-dragger>
            <div v-if="uploadedImage" class="uploaded-image">
              <img :src="uploadedImage" :alt="t('home.selectImageFirst')" />
              <div class="image-overlay">
                <a-button type="primary" @click="analyzeImage">
                  <EyeOutlined />
                  {{ t('home.startAnalyze') }}
                </a-button>
                <a-button @click="clearImage">
                  <DeleteOutlined />
                  {{ t('home.remove') }}
                </a-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 搜索选项 -->
        <div v-if="showSearchOptions && inputMode === 'text'" class="search-options">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item :label="t('search.searchType')">
                <a-select v-model:value="searchOptions.searchType" style="width: 100%">
                  <a-select value="semantic">{{ t('search.semantic') }}</a-select>
                  <a-select value="fulltext">{{ t('search.fulltext') }}</a-select>
                  <a-select value="hybrid">{{ t('search.hybrid') }}</a-select>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item :label="t('search.fileType')">
                <a-select
                  v-model:value="searchOptions.fileTypes"
                  mode="multiple"
                  style="width: 100%"
                >
                  <a-select value="document">{{ t('fileType.document') }}</a-select>
                  <a-select value="audio">{{ t('fileType.audio') }}</a-select>
                  <a-select value="video">{{ t('fileType.video') }}</a-select>
                  <a-select value="image">{{ t('fileType.image') }}</a-select>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item :label="t('search.threshold')">
                <a-slider
                  v-model:value="searchOptions.threshold"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :tooltip-formatter="(value: number) => `${(value * 100).toFixed(0)}%`"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <!-- 搜索按钮组 -->
        <div class="search-actions" v-if="inputMode === 'text'">
          <a-button
            type="primary"
            size="large"
            @click="handleSearch"
            :loading="isSearching"
            :disabled="!canSearch"
          >
            <SearchOutlined />
            {{ t('home.startSearch') }}
          </a-button>
          </div>
      </div>

    </div>

    <!-- 搜索结果 -->
    <div class="results-section" v-if="searchResults.length > 0 || isSearching">
      <div class="results-header">
        <h3 class="results-title">{{ t('search.results') }}</h3>
        <div class="results-stats">
          <span class="results-count">
            {{ t('search.resultsCount', { count: searchStats.total }) }}
          </span>
          <span class="results-time">
            {{ t('search.searchTime', { time: searchStats.searchTime?.toFixed(2) }) }}
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
          {{ t('search.loadMore') }}
        </a-button>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!isSearching && hasSearched">
      <a-empty
        :description="t('search.noResults')"
      >
        <template #image>
          <SearchOutlined style="font-size: 64px; color: var(--text-quaternary)" />
        </template>
        <a-button type="primary" @click="showAdvancedSearch">
          {{ t('home.advancedSearch') }}
        </a-button>
      </a-empty>
    </div>

    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { SearchService } from '@/api/search'
import type { SearchResult, SearchType, FileType } from '@/types/api'
import { InputType } from '@/types/api'
import SearchResultCard from '@/components/SearchResultCard.vue'
import {
  FormOutlined,
  AudioOutlined,
  PictureOutlined,
  SearchOutlined,
  SettingOutlined,
  VideoCameraOutlined,
  EyeOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'

// 国际化
const { t } = useI18n()

// 响应式数据
const inputMode = ref<'text' | 'voice' | 'image'>('text')
const isSearchFocused = ref(false)
const searchQuery = ref('')
const isSearching = ref(false)
const hasSearched = ref(false)
const showSearchOptions = ref(false)


// 语音录制
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingTimer = ref<NodeJS.Timeout>()
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])

// 图片上传
const uploadedImage = ref<string>('')

// 搜索结果
const searchResults = ref<SearchResult[]>([])
const isLoadingMore = ref(false)

// 搜索选项
const searchOptions = reactive({
  searchType: 'hybrid' as SearchType,
  fileTypes: [] as FileType[],
  threshold: 0.5
})

// 搜索统计
const searchStats = reactive({
  total: 0,
  searchTime: 0
})


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
    const response = await SearchService.search({
      query: searchQuery.value,
      search_type: searchOptions.searchType,
      threshold: searchOptions.threshold,
      file_types: searchOptions.fileTypes,
      limit: 50
    })

    if (response.success) {
      searchResults.value = response.data.results
      searchStats.total = response.data.total
      searchStats.searchTime = response.data.search_time

      message.success(t('home.searchComplete', { count: response.data.total }))
    }
  } catch (error) {
    message.error(t('home.searchFailed'))
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}


// 存储录音和上传的文件
const recordedAudioFile = ref<File | null>(null)
const uploadedImageFile = ref<File | null>(null)

// 图片上传相关
const handleImageUpload = async (file: File) => {
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!validTypes.includes(file.type)) {
    message.error(t('home.imageFormatError'))
    return false // 阻止默认上传
  }

  // 验证文件大小（10MB）
  if (file.size > 10 * 1024 * 1024) {
    message.error(t('home.imageSizeError'))
    return false // 阻止默认上传
  }

  uploadedImageFile.value = file
  // 生成预览
  const reader = new FileReader()
  reader.onload = async (e) => {
    uploadedImage.value = e.target?.result as string
    // 图片上传完成后自动开始分析
    await analyzeImage()
  }
  reader.readAsDataURL(file)
  return false // 阻止默认上传
}

const analyzeImage = async () => {
  if (!uploadedImageFile.value) {
    message.error(t('home.selectImageFirst'))
    return
  }

  isSearching.value = true
  try {
    // 调用多模态搜索API
    const response = await SearchService.multimodalSearch(
      InputType.IMAGE,
      uploadedImageFile.value,
      searchOptions.searchType,
      50,
      searchOptions.threshold,
      searchOptions.fileTypes
    )

    if (response.success) {
      // 图片搜索完成，保持在图片模式，不切换到文本模式
      // 清空搜索查询以避免显示在文本输入框中
      searchQuery.value = ''
      // inputMode.value 保持为 'image'，不强制切换

      // 更新搜索结果
      searchResults.value = response.data.search_results || []
      searchStats.total = response.data.search_results?.length || 0
      searchStats.searchTime = 0.95 // 图片搜索的固定时间

      message.success(t('home.imageAnalyzeComplete', { count: response.data.search_results?.length || 0 }))
    } else {
      message.error(t('home.imageAnalyzeFailed'))
    }
  } catch (error) {
    message.error(t('home.imageAnalyzeFailed'))
    console.error('Image analysis error:', error)
  } finally {
    isSearching.value = false
  }
}

const clearImage = () => {
  uploadedImage.value = ''
  uploadedImageFile.value = null
}

// 语音录制相关
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    // 请求麦克风权限
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 44100
      }
    })

    // 创建 MediaRecorder 实例
    const options = { mimeType: 'audio/webm' }
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      // 如果 webm 不支持，尝试其他格式
      const mimeTypes = ['audio/mp4', 'audio/ogg', 'audio/wav']
      for (const type of mimeTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          options.mimeType = type
          break
        }
      }
    }

    mediaRecorder.value = new MediaRecorder(stream, options)
    audioChunks.value = []

    // 设置录音数据处理
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    // 录音停止时的处理
    mediaRecorder.value.onstop = async () => {
      // 将录音数据合并为一个 Blob
      const audioBlob = new Blob(audioChunks.value, {
        type: mediaRecorder.value?.mimeType || 'audio/webm'
      })

      // 创建 File 对象
      const fileName = `recording_${new Date().getTime()}.webm`
      const audioFile = new File([audioBlob], fileName, {
        type: audioBlob.type
      })

      // 保存录音文件
      recordedAudioFile.value = audioFile

      // 停止音轨
      stream.getTracks().forEach(track => track.stop())

      // 调用语音搜索API
      await processVoiceSearch(audioFile)
    }

    // 开始录音
    mediaRecorder.value.start(100) // 每100ms收集一次数据

    isRecording.value = true
    recordingTime.value = 0

    recordingTimer.value = setInterval(() => {
      recordingTime.value += 1
      if (recordingTime.value >= 30) {
        stopRecording()
        message.warning(t('home.recordingTimeLimit'))
      }
    }, 1000)

    message.info(t('home.startRecordingSuccess'))

  } catch (error) {
    console.error('录音失败:', error)
    message.error(t('error.microphoneAccessDenied'))
    isRecording.value = false
  }
}

const stopRecording = () => {
  isRecording.value = false
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
  }

  // 停止录音
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }
}

// 处理语音搜索
const processVoiceSearch = async (audioFile: File) => {
  isSearching.value = true
  try {
    message.loading(t('home.voiceRecognizing'), 0)
    const response = await SearchService.multimodalSearch(
      InputType.VOICE,
      audioFile,
      searchOptions.searchType,
      100,
      searchOptions.threshold,
      searchOptions.fileTypes
    )
    message.destroy() // 关闭loading

    if (response.success) {
      // 语音搜索完成，保持在语音模式，不切换到文本模式
      // 可以选择显示转换后的文本，但不强制切换模式
      searchQuery.value = response.data.converted_text
      // inputMode.value 保持为 'voice'，不强制切换

      // 更新搜索结果
      searchResults.value = response.data.search_results || []
      searchStats.total = response.data.search_results?.length || 0
      // 语音搜索没有返回search_time，使用默认值
      searchStats.searchTime = 1.2

      message.success(t('home.voiceRecognizeComplete', { count: response.data.search_results?.length || 0 }))
    } else {
      message.error(t('home.voiceRecognizeFailed'))
    }
  } catch (error) {
    message.destroy() // 关闭loading
    message.error(t('home.voiceRecognizeFailed'))
    console.error('Voice recognition error:', error)

    // 如果语音识别失败，可以选择保持在语音模式或切换到文本模式
    // 这里选择保持语音模式，让用户可以重新录音
    // inputMode.value = 'text'  // 注释掉强制切换
  } finally {
    isSearching.value = false
  }
}

// 搜索结果操作
const handleOpen = async (result: SearchResult) => {
  try {
    // 优先使用存储的API引用
    const api = electronAPI || (window as any).api

    if (api && typeof api.openFile === 'function') {
      const response = await api.openFile(result.file_path)

      if (response.success) {
        message.success(t('home.fileOpened', { filename: result.file_name }))
      } else {
        message.error(t('home.fileOpenFailed', { error: response.error }))
      }
    } else {
      // 备用方案：复制文件路径到剪贴板
      await navigator.clipboard.writeText(result.file_path)
      message.info(t('home.filePathCopied', { path: result.file_path }))
    }
  } catch (error) {
    console.error('打开文件时出错:', error)
    // 备用方案：复制文件路径到剪贴板
    await navigator.clipboard.writeText(result.file_path)
    message.info(t('home.filePathCopied', { path: result.file_path }))
  }
}



// 加载更多
const loadMore = async () => {
  isLoadingMore.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    // 模拟加载更多数据
    message.info(t('home.noMoreResults'))
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

// 在组件外部保存 API 引用
let electronAPI: any = null

// 组件挂载
onMounted(() => {
  // 保存 API 引用
  electronAPI = (window as any).api
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