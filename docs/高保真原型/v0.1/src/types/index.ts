// 小遥搜索 v2.0 类型定义

// 多模态输入类型
export type InputMode = 'voice' | 'text' | 'image'

// 文件类型
export type FileType = 'audio' | 'document' | 'image' | 'video' | 'code' | 'other'

// 搜索结果项
export interface SearchResult {
  id: string
  name: string
  type: FileType
  path: string
  size: string
  sizeInBytes: number
  matchScore: number
  preview: string
  lastModified: string
  icon: string
  tags?: string[]
}

// 搜索状态
export interface SearchState {
  query: string
  mode: InputMode
  isSearching: boolean
  results: SearchResult[]
  totalResults: number
  searchTime: number
  hasSearched: boolean
}

// AI引擎配置
export interface AIEngine {
  id: string
  name: string
  type: 'local' | 'cloud'
  status: 'active' | 'inactive' | 'loading'
  model?: string
}

// 用户设置
export interface UserSettings {
  aiEngine: AIEngine
  searchScope: string[]
  theme: 'dark' | 'light' | 'auto'
  language: 'zh-CN' | 'en-US'
  animations: boolean
  highContrast: boolean
  reducedMotion: boolean
}

// 应用状态
export interface AppState {
  // 当前页面
  currentPage: 'home' | 'settings' | 'index' | 'help'

  // 搜索状态
  search: SearchState

  // 用户设置
  settings: UserSettings

  // 系统状态
  systemStats: {
    indexedFiles: number
    totalSearches: number
    dataSize: string
    lastUpdate: string
  }
}

// 组件 Props 类型
export interface MultiModalIndicatorProps {
  mode: InputMode
  voiceActivity?: number
  onModeChange: (mode: InputMode) => void
}

export interface SearchBoxProps {
  query: string
  mode: InputMode
  isRecording: boolean
  onQueryChange: (query: string) => void
  onSearch: () => void
  onVoiceStart: () => void
  onVoiceStop: () => void
  onImageUpload: (file: File) => void
}

export interface ResultCardProps {
  result: SearchResult
  onPreview: (result: SearchResult) => void
  onOpen: (result: SearchResult) => void
  onFavorite: (result: SearchResult) => void
  onDelete: (result: SearchResult) => void
}

// 事件类型
export interface SearchEvent {
  type: 'search-start' | 'search-complete' | 'search-error'
  payload?: any
}

export interface VoiceEvent {
  type: 'voice-start' | 'voice-stop' | 'voice-data' | 'voice-error'
  payload?: any
}

// API 响应类型
export interface SearchResponse {
  success: boolean
  data: SearchResult[]
  total: number
  searchTime: number
  message?: string
}

export interface APIResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}