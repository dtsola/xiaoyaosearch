import { defineStore } from 'pinia'
import type { AppState, SearchState, UserSettings, SearchResult, InputMode } from '@/types'

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    currentPage: 'home',
    search: {
      query: '',
      mode: 'text',
      isSearching: false,
      results: [],
      totalResults: 0,
      searchTime: 0,
      hasSearched: false
    },
    settings: {
      aiEngine: {
        id: 'ollama',
        name: 'Ollama',
        type: 'local',
        status: 'active',
        model: 'qwen2.5:7b'
      },
      searchScope: ['全部文件夹'],
      theme: 'dark',
      language: 'zh-CN',
      animations: true,
      highContrast: false,
      reducedMotion: false
    },
    systemStats: {
      indexedFiles: 1234,
      totalSearches: 15,
      dataSize: '8.7GB',
      lastUpdate: '2小时前'
    }
  }),

  getters: {
    // 当前输入模式
    currentMode: (state): InputMode => state.search.mode,

    // 是否有搜索结果
    hasResults: (state): boolean => state.search.results.length > 0,

    // 搜索结果数量
    resultsCount: (state): number => state.search.results.length,

    // 是否正在录音
    isRecording: (state): boolean => state.search.mode === 'voice' && state.search.isSearching,

    // 格式化的搜索时间
    formattedSearchTime: (state): string => `${state.search.searchTime.toFixed(1)}s`
  },

  actions: {
    // 切换页面
    setCurrentPage(page: AppState['currentPage']) {
      this.currentPage = page
    },

    // 设置搜索查询
    setQuery(query: string) {
      this.search.query = query
    },

    // 切换输入模式
    setInputMode(mode: InputMode) {
      this.search.mode = mode
      if (mode !== 'voice') {
        this.search.isSearching = false
      }
    },

    // 开始搜索
    startSearch() {
      this.search.isSearching = true
      this.search.hasSearched = true

      // 模拟搜索过程
      setTimeout(() => {
        this.completeSearch()
      }, 800 + Math.random() * 400)
    },

    // 完成搜索
    completeSearch() {
      this.search.isSearching = false
      this.search.searchTime = 0.5 + Math.random() * 1.5

      // 生成模拟搜索结果
      if (this.search.query.trim()) {
        this.search.results = this.generateMockResults(this.search.query)
        this.search.totalResults = this.search.results.length
      } else {
        this.search.results = []
        this.search.totalResults = 0
      }
    },

    // 生成模拟搜索结果
    generateMockResults(query: string): SearchResult[] {
      const mockResults: SearchResult[] = [
        {
          id: '1',
          name: 'AI讨论_2024-11-15.mp3',
          type: 'audio',
          path: 'D:\\Work\\Audio\\AI_2024.mp3',
          size: '2.3MB',
          sizeInBytes: 2411724,
          matchScore: 95,
          preview: '技术会议录音，深入讨论AI发展趋势、机器学习算法优化...',
          lastModified: '2024-11-15',
          icon: '🎵',
          tags: ['AI', '技术', '讨论']
        },
        {
          id: '2',
          name: 'API接口文档_v2.1.md',
          type: 'document',
          path: 'D:\\Work\\API_Documentation.md',
          size: '156KB',
          sizeInBytes: 159744,
          matchScore: 87,
          preview: 'RESTful API完整规范，包含认证机制、请求参数详解、响应格式说明...',
          lastModified: '2024-11-14',
          icon: '📄',
          tags: ['API', '文档', '规范']
        },
        {
          id: '3',
          name: '机器学习算法优化.pdf',
          type: 'document',
          path: 'D:\\Work\\ML_Algorithms.pdf',
          size: '2.1MB',
          sizeInBytes: 2202009,
          matchScore: 82,
          preview: '机器学习算法性能优化方法，包含梯度下降改进、神经网络调参技巧...',
          lastModified: '2024-11-13',
          icon: '📊',
          tags: ['机器学习', '算法', '优化']
        },
        {
          id: '4',
          name: '前端开发笔记.txt',
          type: 'document',
          path: 'D:\\Work\\Frontend_Notes.txt',
          size: '45KB',
          sizeInBytes: 46080,
          matchScore: 78,
          preview: 'Vue3组件开发最佳实践，Composition API使用技巧，性能优化策略...',
          lastModified: '2024-11-12',
          icon: '📝',
          tags: ['前端', 'Vue3', '开发']
        },
        {
          id: '5',
          name: '产品设计原型.png',
          type: 'image',
          path: 'D:\\Work\\Design_Prototype.png',
          size: '3.7MB',
          sizeInBytes: 3879731,
          matchScore: 75,
          preview: '小遥搜索应用原型设计图，包含主界面布局和交互流程设计...',
          lastModified: '2024-11-11',
          icon: '🖼️',
          tags: ['设计', '原型', 'UI']
        }
      ]

      // 根据查询关键词过滤结果
      return mockResults.filter(result =>
        result.name.toLowerCase().includes(query.toLowerCase()) ||
        result.preview.toLowerCase().includes(query.toLowerCase()) ||
        result.tags?.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
      )
    },

    // 清空搜索结果
    clearResults() {
      this.search.results = []
      this.search.totalResults = 0
      this.search.hasSearched = false
      this.search.query = ''
    },

    // 更新设置
    updateSettings(settings: Partial<UserSettings>) {
      this.settings = { ...this.settings, ...settings }
    },

    // 开始语音录制
    startVoiceRecording() {
      this.search.mode = 'voice'
      this.search.isSearching = true
    },

    // 停止语音录制
    stopVoiceRecording() {
      this.search.isSearching = false
      // 模拟语音转文字
      this.search.query = 'AI技术发展趋势讨论'
    },

    // 处理图片上传
    handleImageUpload(file: File) {
      this.search.mode = 'image'
      // 模拟图片分析
      setTimeout(() => {
        this.search.query = '图片中的文字内容'
        this.startSearch()
      }, 1000)
    }
  }
})