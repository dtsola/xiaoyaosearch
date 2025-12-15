// 搜索API服务 - 包含真实API和Mock服务

import type {
  SearchRequest,
  SearchResponse,
  MultimodalResponse,
  SearchHistory,
  SearchResult
} from '@/types/api'
import { InputType, FileType, SearchType } from '@/types/api'
import { httpClient } from '@/utils/http'

// 真实API服务
export class SearchService {
  // 文本搜索
  static async search(params: SearchRequest): Promise<SearchResponse> {
    return await httpClient.post<SearchResponse>('/api/search', params)
  }

  // 多模态搜索
  static async multimodalSearch(
    inputType: InputType.VOICE | InputType.IMAGE,
    file: File,
    searchType: SearchType = SearchType.HYBRID,
    limit: number = 20,
    threshold: number = 0.7,
    fileTypes?: FileType[]
  ): Promise<MultimodalResponse> {
    const formData = new FormData()
    formData.append('file', file)  // 后端期望的文件字段名是 'file'
    formData.append('input_type', inputType)
    formData.append('search_type', searchType)
    formData.append('limit', limit.toString())
    formData.append('threshold', threshold.toString())

    if (fileTypes && fileTypes.length > 0) {
      fileTypes.forEach(fileType => {
        formData.append('file_types', fileType)
      })
    }

    return await httpClient.postFormData<MultimodalResponse>('/api/search/multimodal', formData)
  }

  // 获取搜索历史
  static async getHistory(limit = 20, offset = 0): Promise<{ success: boolean; data: { history: SearchHistory[]; total: number } }> {
    return await httpClient.get<{ success: boolean; data: { history: SearchHistory[]; total: number } }>(`/api/search/history?limit=${limit}&offset=${offset}`)
  }

  // 删除搜索历史
  static async deleteHistory(id: number): Promise<{ success: boolean; message: string }> {
    return await httpClient.delete<{ success: boolean; message: string }>(`/api/search/history/${id}`)
  }

  // 清空搜索历史
  static async clearHistory(): Promise<{ success: boolean; message: string }> {
    return await httpClient.delete<{ success: boolean; message: string }>('/api/search/history')
  }

  // 搜索建议
  static async getSuggestions(query: string, limit = 5): Promise<{ success: boolean; data: { suggestions: string[]; query: string; total: number } }> {
    return await httpClient.get<{ success: boolean; data: { suggestions: string[]; query: string; total: number } }>(`/api/search/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`)
  }
}

// Mock 数据服务
export class SearchServiceMock {
  private static mockResults: SearchResult[] = [
    {
      file_id: 1,
      file_name: '01课件-DeepSeek分享.pdf',
      file_path: 'test-dir\\文档\\01课件-DeepSeek分享.pdf',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.95,
      preview_text: 'DeepSeek AI技术分享课件，介绍大语言模型的原理、训练方法以及在各种任务中的应用实践。重点包含模型架构优化和推理加速技术。',
      highlight: 'DeepSeek <em>AI</em>技术分享课件，介绍大语言模型的原理、训练方法以及在各种任务中的应用实践。重点包含模型架构优化和推理加速技术。',
      created_at: '2024-01-15T10:30:00Z',
      modified_at: '2024-01-15T10:30:00Z',
      file_size: 3355443,
      match_type: 'hybrid'
    },
    {
      file_id: 2,
      file_name: '1、抖音PRD文档.docx',
      file_path: 'test-dir\\文档\\1、抖音PRD文档.docx',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.89,
      preview_text: '抖音产品需求文档，详细描述了短视频平台的核心功能设计、用户体验优化和AI推荐算法的应用场景。',
      highlight: '抖音产品需求文档，详细描述了短视频平台的核心功能设计、用户体验优化和<em>AI</em>推荐算法的应用场景。',
      created_at: '2024-01-12T09:20:00Z',
      modified_at: '2024-01-12T09:20:00Z',
      file_size: 2202009,
      match_type: 'fulltext'
    },
    {
      file_id: 3,
      file_name: '2、KeepPRD文档.docx',
      file_path: 'test-dir\\文档\\2、KeepPRD文档.docx',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.87,
      preview_text: 'Keep健身应用产品需求文档，详细说明AI驱动的个性化训练计划制定、运动数据分析反馈和智能健康管理系统。',
      highlight: 'Keep健身应用产品需求文档，详细说明<em>AI</em>驱动的个性化训练计划制定、运动数据分析反馈和智能健康管理系统。',
      created_at: '2024-01-11T14:15:00Z',
      modified_at: '2024-01-11T14:15:00Z',
      file_size: 1856722,
      match_type: 'fulltext'
    },
    {
      file_id: 4,
      file_name: '10_面试大保健_串讲.mp3',
      file_path: 'test-dir\\音频\\10_面试大保健_串讲.mp3',
      file_type: FileType.AUDIO,
      relevance_score: 0.86,
      preview_text: 'AI技术面试串讲音频，包含常见算法题解答、系统设计经验和机器学习概念讲解，帮助求职者快速准备AI岗位面试。',
      highlight: '<em>AI</em>技术面试串讲音频，包含常见算法题解答、系统设计经验和机器学习概念讲解，帮助求职者快速准备AI岗位面试。',
      created_at: '2024-01-10T14:20:00Z',
      modified_at: '2024-01-10T14:20:00Z',
      file_size: 29884775,
      match_type: 'semantic'
    },
    {
      file_id: 5,
      file_name: '推荐技能点.md',
      file_path: 'test-dir\\文档\\推荐技能点.md',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.91,
      preview_text: 'AI工程师推荐技能清单，整理了Python编程、深度学习框架、数据处理工具等必备技能和学习路径建议。',
      highlight: '<em>AI</em>工程师推荐技能清单，整理了Python编程、深度学习框架、数据处理工具等必备技能和学习路径建议。',
      created_at: '2024-01-08T11:30:00Z',
      modified_at: '2024-01-08T11:30:00Z',
      file_size: 163575,
      match_type: 'fulltext'
    },
    {
      file_id: 6,
      file_name: 'Sqoop一些常用命令及参数.md',
      file_path: 'test-dir\\文档\\Sqoop一些常用命令及参数.md',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.75,
      preview_text: '大数据处理工具Sqoop的使用指南，包含数据导入导出命令、性能优化技巧和与AI数据处理的集成方案。',
      highlight: '大数据处理工具Sqoop的使用指南，包含数据导入导出命令、性能优化技巧和与<em>AI</em>数据处理的集成方案。',
      created_at: '2024-01-07T16:45:00Z',
      modified_at: '2024-01-07T16:45:00Z',
      file_size: 89234,
      match_type: 'fulltext'
    },
    {
      file_id: 7,
      file_name: 'user_profile_manager.txt',
      file_path: 'test-dir\\文档\\user_profile_manager.txt',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.85,
      preview_text: 'AI用户画像管理系统代码，实现基于机器学习的用户行为分析、兴趣标签生成和个性化推荐策略管理。',
      highlight: '<em>AI</em>用户画像管理系统代码，实现基于机器学习的用户行为分析、兴趣标签生成和个性化推荐策略管理。',
      created_at: '2024-01-06T10:20:00Z',
      modified_at: '2024-01-06T10:20:00Z',
      file_size: 70254,
      match_type: 'fulltext'
    },
    {
      file_id: 8,
      file_name: '验证码---必看.txt',
      file_path: 'test-dir\\文档\\验证码---必看.txt',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.78,
      preview_text: 'AI验证码识别技术文档，介绍图像预处理、OCR识别、深度学习模型在验证码自动识别中的应用和实现方法。',
      highlight: '<em>AI</em>验证码识别技术文档，介绍图像预处理、OCR识别、深度学习模型在验证码自动识别中的应用和实现方法。',
      created_at: '2024-01-05T16:45:00Z',
      modified_at: '2024-01-05T16:45:00Z',
      file_size: 47185,
      match_type: 'semantic'
    },
    {
      file_id: 9,
      file_name: '50-泛娱乐内容行业核心demo实战1 - AI生成视频工作流.mp4',
      file_path: 'test-dir\\视频\\50-泛娱乐内容行业核心demo实战1 - AI生成视频工作流.mp4',
      file_type: FileType.VIDEO,
      relevance_score: 0.84,
      preview_text: 'AI生成视频工作流实战教程，演示从文本到视频的完整制作流程，包含脚本生成、图像合成和视频编辑等技术要点。',
      highlight: '<em>AI</em>生成视频工作流实战教程，演示从文本到视频的完整制作流程，包含脚本生成、图像合成和视频编辑等技术要点。',
      created_at: '2024-01-03T08:00:00Z',
      modified_at: '2024-01-03T08:00:00Z',
      file_size: 194615731,
      match_type: 'semantic'
    },
    {
      file_id: 10,
      file_name: '51-泛娱乐内容行业核心demo实战2 - AI证件照AI写真.mp4',
      file_path: 'test-dir\\视频\\51-泛娱乐内容行业核心demo实战2 - AI证件照AI写真.mp4',
      file_type: FileType.VIDEO,
      relevance_score: 0.82,
      preview_text: 'AI证件照和写真生成视频教程，详细讲解人脸识别、图像风格转换和高质量人像生成的AI技术实现。',
      highlight: '<em>AI</em>证件照和写真生成视频教程，详细讲解人脸识别、图像风格转换和高质量人像生成的<em>AI</em>技术实现。',
      created_at: '2024-01-02T09:30:00Z',
      modified_at: '2024-01-02T09:30:00Z',
      file_size: 156732890,
      match_type: 'semantic'
    },
    {
      file_id: 11,
      file_name: '潮犀科技-企业介绍.pptx',
      file_path: 'test-dir\\文档\\潮犀科技-企业介绍.pptx',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.88,
      preview_text: '潮犀科技公司介绍演示文稿，重点展示AI驱动的智能客服系统、数据分析平台和企业级解决方案的技术优势。',
      highlight: '潮犀科技公司介绍演示文稿，重点展示<em>AI</em>驱动的智能客服系统、数据分析平台和企业级解决方案的技术优势。',
      created_at: '2024-01-01T13:15:00Z',
      modified_at: '2024-01-01T13:15:00Z',
      file_size: 7130316,
      match_type: 'fulltext'
    },
    {
      file_id: 12,
      file_name: '第三组李毓鑫实时流程图.xls',
      file_path: 'test-dir\\文档\\第三组李毓鑫实时流程图.xls',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.79,
      preview_text: 'AI系统实时数据处理流程图Excel表格，展示数据采集、预处理、模型推理和结果输出的完整技术架构。',
      highlight: '<em>AI</em>系统实时数据处理流程图Excel表格，展示数据采集、预处理、模型推理和结果输出的完整技术架构。',
      created_at: '2023-12-30T11:20:00Z',
      modified_at: '2023-12-30T11:20:00Z',
      file_size: 524288,
      match_type: 'fulltext'
    },
    {
      file_id: 13,
      file_name: '商品销售明细表.xlsx',
      file_path: 'test-dir\\文档\\商品销售明细表.xlsx',
      file_type: FileType.DOCUMENT,
      relevance_score: 0.82,
      preview_text: 'AI智能销售数据分析表，包含商品销量预测模型、用户购买行为分析和个性化推荐算法的效果评估数据。',
      highlight: '<em>AI</em>智能销售数据分析表，包含商品销量预测模型、用户购买行为分析和个性化推荐算法的效果评估数据。',
      created_at: '2023-12-28T15:20:00Z',
      modified_at: '2023-12-28T15:20:00Z',
      file_size: 935329,
      match_type: 'hybrid'
    },
    {
      file_id: 14,
      file_name: '01 欢迎来到大模型 RAG 进阶实战营.jpg',
      file_path: 'test-dir\\图片\\01 欢迎来到大模型 RAG 进阶实战营.jpg',
      file_type: FileType.IMAGE,
      relevance_score: 0.80,
      preview_text: 'AI大模型RAG实战营欢迎海报，介绍检索增强生成技术的核心概念、学习内容和实战项目安排。',
      highlight: '<em>AI</em>大模型RAG实战营欢迎海报，介绍检索增强生成技术的核心概念、学习内容和实战项目安排。',
      created_at: '2023-12-25T10:45:00Z',
      modified_at: '2023-12-25T10:45:00Z',
      file_size: 1572864,
      match_type: 'semantic'
    },
    {
      file_id: 15,
      file_name: '03 学习群组与助教答疑.jpeg',
      file_path: 'test-dir\\图片\\03 学习群组与助教答疑.jpeg',
      file_type: FileType.IMAGE,
      relevance_score: 0.76,
      preview_text: 'AI学习社群指导截图，展示助教答疑场景、学员讨论氛围和AI技术交流的互动学习环境。',
      highlight: '<em>AI</em>学习社群指导截图，展示助教答疑场景、学员讨论氛围和<em>AI</em>技术交流的互动学习环境。',
      created_at: '2023-12-24T14:30:00Z',
      modified_at: '2023-12-24T14:30:00Z',
      file_size: 891289,
      match_type: 'semantic'
    },
    {
      file_id: 16,
      file_name: '04 毕业条件.png',
      file_path: 'test-dir\\图片\\04 毕业条件.png',
      file_type: FileType.IMAGE,
      relevance_score: 0.74,
      preview_text: 'AI训练营毕业要求说明图，详细列出项目完成标准、技能考核要求和AI应用实践评估指标。',
      highlight: '<em>AI</em>训练营毕业要求说明图，详细列出项目完成标准、技能考核要求和<em>AI</em>应用实践评估指标。',
      created_at: '2023-12-23T09:15:00Z',
      modified_at: '2023-12-23T09:15:00Z',
      file_size: 723456,
      match_type: 'semantic'
    },
    {
      file_id: 17,
      file_name: '课后练习.png',
      file_path: 'test-dir\\图片\\课后练习.png',
      file_type: FileType.IMAGE,
      relevance_score: 0.77,
      preview_text: 'AI课程练习题目示意图，包含编程作业、算法实现和模型调优的实践任务说明和示例代码。',
      highlight: '<em>AI</em>课程练习题目示意图，包含编程作业、算法实现和模型调优的实践任务说明和示例代码。',
      created_at: '2023-12-22T16:00:00Z',
      modified_at: '2023-12-22T16:00:00Z',
      file_size: 834567,
      match_type: 'semantic'
    },
    ]

  // 搜索建议库
  private static suggestionPool = [
    '人工智能',
    'AI技术',
    '机器学习',
    '深度学习',
    '神经网络',
    '自然语言处理',
    '计算机视觉',
    '数据分析',
    '算法优化',
    '模型训练',
    'TensorFlow',
    'PyTorch',
    'Python编程',
    '数据科学',
    '智能推荐',
    '图像识别',
    '语音识别',
    'ChatGPT',
    '大语言模型',
    '生成式AI',
    '强化学习',
    '数据挖掘',
    '云计算',
    '边缘计算',
    '物联网AI'
  ]

  static async search(params: SearchRequest): Promise<SearchResponse> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400))

    // 简单的模拟搜索逻辑
    let filteredResults = this.mockResults.filter(result =>
      result.file_name.toLowerCase().includes(params.query.toLowerCase()) ||
      result.preview_text.toLowerCase().includes(params.query.toLowerCase())
    )

    // 根据相关性排序
    filteredResults.sort((a, b) => b.relevance_score - a.relevance_score)

    // 应用文件类型过滤
    if (params.file_types && params.file_types.length > 0) {
      filteredResults = filteredResults.filter(result =>
        params.file_types!.includes(result.file_type as FileType)
      )
    }

    // 应用阈值过滤
    if (params.threshold) {
      filteredResults = filteredResults.filter(result =>
        result.relevance_score >= params.threshold!
      )
    }

    // 限制结果数量
    const limitedResults = filteredResults.slice(0, params.limit || 20)

    return {
      success: true,
      data: {
        results: limitedResults,
        total: filteredResults.length,
        search_time: 0.8 + Math.random() * 0.4,
        query_used: params.query,
        input_processed: false
      }
    }
  }

  static async multimodalSearch(inputType: InputType.VOICE | InputType.IMAGE, file: File): Promise<MultimodalResponse> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 500))

    const convertedText = inputType === InputType.VOICE
      ? '请帮我找一些关于人工智能的资料'
      : '搜索图片中的内容相关信息'

    // 根据输入类型选择不同的结果
    const results = inputType === InputType.VOICE
      ? this.mockResults.filter(r => r.file_type === FileType.AUDIO || r.file_type === FileType.DOCUMENT).slice(0, 3)
      : this.mockResults.filter(r => r.file_type === FileType.IMAGE || r.file_type === FileType.VIDEO).slice(0, 2)

    return {
      success: true,
      data: {
        converted_text: convertedText,
        confidence: 0.85 + Math.random() * 0.1,
        search_results: results,
        file_info: {
          filename: file.name,
          size: file.size,
          content_type: file.type
        }
      }
    }
  }

  static async getHistory(limit = 20, offset = 0): Promise<{ success: boolean; data: { history: SearchHistory[]; total: number } }> {
    await new Promise(resolve => setTimeout(resolve, 200))

    const mockHistory: SearchHistory[] = [
      {
        id: 1,
        search_query: '人工智能发展趋势',
        input_type: InputType.TEXT,
        search_type: SearchType.HYBRID,
        ai_model_used: 'bge-m3',
        result_count: 5,
        response_time: 0.15,
        created_at: '2024-01-20T14:30:00Z'
      },
      {
        id: 2,
        search_query: '机器学习算法',
        input_type: InputType.TEXT,
        search_type: SearchType.SEMANTIC,
        ai_model_used: 'bge-m3',
        result_count: 8,
        response_time: 0.22,
        created_at: '2024-01-19T16:45:00Z'
      },
      {
        id: 3,
        search_query: '深度学习框架对比',
        input_type: InputType.TEXT,
        search_type: SearchType.FULLTEXT,
        ai_model_used: 'bge-m3',
        result_count: 3,
        response_time: 0.18,
        created_at: '2024-01-18T10:20:00Z'
      },
      {
        id: 4,
        search_query: '数据分析最佳实践',
        input_type: InputType.VOICE,
        search_type: SearchType.HYBRID,
        ai_model_used: 'faster-whisper',
        result_count: 6,
        response_time: 1.2,
        created_at: '2024-01-17T09:15:00Z'
      },
      {
        id: 5,
        search_query: 'AI应用案例',
        input_type: InputType.IMAGE,
        search_type: SearchType.SEMANTIC,
        ai_model_used: 'cn-clip',
        result_count: 4,
        response_time: 0.95,
        created_at: '2024-01-16T13:30:00Z'
      }
    ]

    return {
      success: true,
      data: {
        history: mockHistory.slice(offset, offset + limit),
        total: mockHistory.length
      }
    }
  }

  static async deleteHistory(id: number): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 150))

    return {
      success: true,
      message: `搜索历史记录 ${id} 删除成功`
    }
  }

  static async clearHistory(): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 200))

    return {
      success: true,
      message: '所有搜索历史已清空'
    }
  }

  static async getSuggestions(query: string, limit = 5): Promise<{ success: boolean; data: { suggestions: string[]; query: string; total: number } }> {
    await new Promise(resolve => setTimeout(resolve, 100))

    // 如果查询为空，返回热门搜索
    if (!query.trim()) {
      const hotSearches = [
        '人工智能',
        '机器学习',
        '深度学习',
        'ChatGPT',
        'AI应用'
      ]

      return {
        success: true,
        data: {
          suggestions: hotSearches.slice(0, limit),
          query: '',
          total: hotSearches.length
        }
      }
    }

    // 根据查询词生成相关建议
    const queryLower = query.toLowerCase()
    const suggestions = this.suggestionPool
      .filter(suggestion =>
        suggestion.toLowerCase().includes(queryLower) ||
        suggestion.length <= query.length + 3 // 包含长度相近的建议
      )
      .sort((a, b) => {
        // 优先显示以查询词开头的建议
        const aStarts = a.toLowerCase().startsWith(queryLower)
        const bStarts = b.toLowerCase().startsWith(queryLower)
        if (aStarts && !bStarts) return -1
        if (!aStarts && bStarts) return 1
        // 然后按长度排序，短的建议优先
        return a.length - b.length
      })
      .slice(0, limit)

    // 如果没有匹配的建议，添加一些相关的智能建议
    if (suggestions.length === 0) {
      const aiSuggestions = [
        `${query} 教程`,
        `${query} 最佳实践`,
        `${query} 应用案例`,
        `${query} 开发工具`,
        `${query} 技术解析`
      ].slice(0, limit)

      return {
        success: true,
        data: {
          suggestions: aiSuggestions,
          query: query,
          total: aiSuggestions.length
        }
      }
    }

    return {
      success: true,
      data: {
        suggestions: suggestions,
        query: query,
        total: suggestions.length
      }
    }
  }
}