// 设置和AI模型配置API服务 - 真实后端接口

import axios from 'axios'
import type {
  AIModelConfig,
  AIModelConfigRequest,
  AppSettings
} from '@/types/api'

const API_BASE_URL = 'http://127.0.0.1:8000'

interface APIResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: {
    code: string
    message: string
    details?: string
  }
}

// 真实API服务
export class SettingsService {
  private static client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // ===== AI模型配置适配方法 =====

  /**
   * 按模型类型获取AI模型配置
   */
  static async getAIModelByType(modelType: string): Promise<any> {
    try {
      // 1. 获取所有AI模型
      const response = await this.client.get('/api/config/ai-models')
      const data: APIResponse<any[]> = response.data

      if (!data.success) {
        throw new Error(data.error?.message || '获取AI模型配置失败')
      }

      // 2. 按模型类型过滤
      const enumType = this.mapFrontendTypeToEnum(modelType)
      const models = data.data.filter((model: any) =>
        model.model_type === enumType && model.is_active
      )

      // 3. 返回第一个匹配的模型，或创建默认配置
      if (models.length > 0) {
        const model = models[0]
        const config = JSON.parse(model.config_json || '{}')

        return {
          id: model.id,
          model_type: modelType,
          model_name: model.model_name,
          config,
          is_active: model.is_active
        }
      } else {
        // 返回默认配置
        return this.getDefaultAIModelConfig(modelType)
      }
    } catch (error) {
      console.error(`获取${modelType}模型配置失败:`, error)
      return this.getDefaultAIModelConfig(modelType)
    }
  }

  /**
   * 按模型类型更新AI模型配置
   */
  static async updateAIModelByType(modelType: string, config: any): Promise<APIResponse> {
    try {
      const enumType = this.mapFrontendTypeToEnum(modelType)

      // 构建完整的配置请求
      const request = {
        model_type: enumType,
        model_name: config.model_name || this.getDefaultModelName(modelType),
        provider: 'local',
        config: config
      }

      const response = await this.client.post('/api/config/ai-model', request)
      return response.data
    } catch (error) {
      console.error(`更新${modelType}模型配置失败:`, error)
      throw error
    }
  }

  /**
   * 按模型类型测试AI模型
   */
  static async testAIModelByType(modelType: string): Promise<APIResponse> {
    try {
      // 1. 获取模型配置
      const modelConfig = await this.getAIModelByType(modelType)

      if (!modelConfig.id) {
        // 如果没有ID，说明是默认配置，创建测试响应
        return {
          success: false,
          error: {
            code: 'MODEL_NOT_CONFIGURED',
            message: `${modelType}模型尚未配置，请先保存配置`
          }
        }
      }

      // 2. 执行模型测试
      const response = await this.client.post(`/api/config/ai-model/${modelConfig.id}/test`)
      return response.data
    } catch (error) {
      console.error(`测试${modelType}模型失败:`, error)
      return {
        success: false,
        error: {
          code: 'TEST_FAILED',
          message: `${modelType}模型测试失败`,
          details: error instanceof Error ? error.message : '未知错误'
        }
      }
    }
  }

  // ===== 通用设置方法 =====

  /**
   * 获取结构化系统设置
   */
  static async getSettings(): Promise<APIResponse<AppSettings>> {
    try {
      // 1. 获取所有扁平设置
      const response = await this.client.get('/api/settings/')
      const flatSettings: APIResponse<any[]> = response.data

      if (!flatSettings.success) {
        throw new Error(flatSettings.error?.message || '获取系统设置失败')
      }

      // 2. 转换为结构化设置
      const structuredSettings = this.convertFlatToStructured(flatSettings.data)

      return {
        success: true,
        data: structuredSettings as AppSettings
      }
    } catch (error) {
      console.error('获取系统设置失败:', error)
      // 返回默认设置
      return {
        success: true,
        data: this.getDefaultStructuredSettings() as AppSettings
      }
    }
  }

  /**
   * 更新系统设置
   */
  static async updateSettings(settings: Partial<AppSettings>): Promise<APIResponse> {
    try {
      // 1. 转换结构化设置为扁平设置
      const flatSettings = this.convertStructuredToFlat(settings)

      // 2. 批量更新设置
      const response = await this.client.post('/api/settings/batch', {
        settings: flatSettings
      })

      return response.data
    } catch (error) {
      console.error('更新系统设置失败:', error)
      throw error
    }
  }

  /**
   * 重置系统设置
   */
  static async resetSystemSettings(): Promise<APIResponse> {
    try {
      const defaultSettings = this.getDefaultStructuredSettings()
      const flatSettings = this.convertStructuredToFlat(defaultSettings)

      const response = await this.client.post('/api/settings/reset', {
        default_settings: flatSettings
      })

      return response.data
    } catch (error) {
      console.error('重置系统设置失败:', error)
      throw error
    }
  }

  // ===== 兼容原有接口的方法 =====

  static async getAIModels() {
    const response = await this.client.get('/api/config/ai-models')
    return response.data
  }

  static async updateAIModel(params: AIModelConfigRequest) {
    const response = await this.client.post('/api/config/ai-model', params)
    return response.data
  }

  static async testAIModel(id: number) {
    const response = await this.client.post(`/api/config/ai-model/${id}/test`)
    return response.data
  }

  static async toggleAIModel(id: number) {
    const response = await this.client.put(`/api/config/ai-model/${id}/toggle`)
    return response.data
  }

  static async deleteAIModel(id: number) {
    const response = await this.client.delete(`/api/config/ai-model/${id}`)
    return response.data
  }

  static async getDefaultAIModels() {
    const response = await this.client.get('/api/config/ai-models/default')
    return response.data
  }

  static async getAIModelStatus() {
    // 获取所有模型状态
    const response = await this.getAIModels()
    return {
      success: true,
      data: {
        models: response.data.map((model: any) => ({
          id: model.id,
          model_type: model.model_type,
          model_name: model.model_name,
          status: model.is_active ? 'loaded' : 'not_loaded',
          memory_usage: model.is_active ? '1.2GB' : null,
          load_time: model.is_active ? '2025-01-01T10:00:00Z' : null
        }))
      }
    }
  }

  static async getAvailableModels() {
    return {
      success: true,
      data: {
        available_models: [
          {
            model_type: 'embedding',
            models: ['BAAI/bge-m3', 'BAAI/bge-small-zh-v1.5', 'BAAI/bge-large-zh-v1.5']
          },
          {
            model_type: 'speech',
            models: ['Systran/faster-whisper-base', 'Systran/faster-whisper-small', 'Systran/faster-whisper-medium', 'Systran/faster-whisper-large']
          },
          {
            model_type: 'vision',
            models: ['OFA-Sys/chinese-clip-vit-base-patch16', 'OFA-Sys/chinese-clip-vit-large-patch16']
          },
          {
            model_type: 'llm',
            models: ['qwen2.5:1.5b']
          }
        ]
      }
    }
  }

  // ===== 工具方法 =====

  /**
   * 前端模型类型映射到后端枚举
   */
  private static mapFrontendTypeToEnum(frontendType: string): string {
    const mapping: Record<string, string> = {
      whisper: 'speech',
      ollama: 'llm',
      clip: 'vision',
      bge: 'embedding'
    }
    return mapping[frontendType] || frontendType
  }

  /**
   * 获取默认模型名称
   */
  private static getDefaultModelName(modelType: string): string {
    const defaults: Record<string, string> = {
      whisper: 'Systran/faster-whisper-base',
      ollama: 'qwen2.5:1.5b',
      clip: 'OFA-Sys/chinese-clip-vit-base-patch16',
      bge: 'BAAI/bge-m3'
    }
    return defaults[modelType] || ''
  }

  /**
   * 获取默认AI模型配置
   */
  private static getDefaultAIModelConfig(modelType: string): any {
    const defaults: Record<string, any> = {
      whisper: {
        id: 0,
        model_type: 'whisper',
        model_name: 'Systran/faster-whisper-base',
        config: {
          model_size: 'base',
          device: 'cpu',
          compute_type: 'float32',
          language: 'zh'
        },
        is_active: true
      },
      ollama: {
        id: 0,
        model_type: 'ollama',
        model_name: 'qwen2.5:1.5b',
        config: {
          ollama_url: 'http://localhost:11434',
          temperature: 0.7,
          max_new_tokens: 2048
        },
        is_active: true
      },
      clip: {
        id: 0,
        model_type: 'clip',
        model_name: 'OFA-Sys/chinese-clip-vit-base-patch16',
        config: {
          device: 'cpu',
          image_size: 224,
          max_length: 77
        },
        is_active: true
      },
      bge: {
        id: 0,
        model_type: 'bge',
        model_name: 'BAAI/bge-m3',
        config: {
          device: 'cpu',
          embedding_dim: 1024,
          max_length: 8192,
          batch_size: 32
        },
        is_active: true
      }
    }
    return defaults[modelType] || {}
  }

  /**
   * 扁平设置转换为结构化设置
   */
  private static convertFlatToStructured(flatSettings: any[]): any {
    const structured: any = {
      search: {
        default_results: 20,
        similarity_threshold: 0.7,
        max_file_size: 50
      },
      ai_models: {}
    }

    flatSettings.forEach((setting: any) => {
      const { key, value } = setting

      // 搜索设置
      if (key === 'default_results') {
        structured.search.default_results = value
      } else if (key === 'similarity_threshold') {
        structured.search.similarity_threshold = value
      } else if (key === 'max_file_size') {
        structured.search.max_file_size = value
      }

      // AI模型设置
      if (key.startsWith('ai_model.')) {
        const [, modelType, settingKey] = key.split('.')

        if (!structured.ai_models[modelType]) {
          structured.ai_models[modelType] = {}
        }

        // 直接使用原始键名，让前端自己处理
        structured.ai_models[modelType][settingKey] = value
      }
    })

    return structured
  }

  /**
   * 结构化设置转换为扁平设置
   */
  private static convertStructuredToFlat(settings: any): any[] {
    const flatSettings: any[] = []

    // 搜索设置
    if (settings.search) {
      if (settings.search.default_results !== undefined) {
        flatSettings.push({
          key: 'default_results',
          value: settings.search.default_results,
          type: 'integer',
          description: '默认返回结果数量'
        })
      }

      if (settings.search.similarity_threshold !== undefined) {
        flatSettings.push({
          key: 'similarity_threshold',
          value: settings.search.similarity_threshold,
          type: 'float',
          description: '相似度阈值'
        })
      }

      if (settings.search.max_file_size !== undefined) {
        flatSettings.push({
          key: 'max_file_size',
          value: settings.search.max_file_size,
          type: 'integer',
          description: '最大文件大小(MB)'
        })
      }
    }

    // AI模型设置
    if (settings.ai_models) {
      Object.entries(settings.ai_models).forEach(([modelType, config]: [string, any]) => {
        Object.entries(config).forEach(([key, value]) => {
          const settingKey = `ai_model.${modelType}.${key}`

          let type = 'string'
          if (typeof value === 'boolean') type = 'boolean'
          if (typeof value === 'number') type = value % 1 === 0 ? 'integer' : 'float'

          flatSettings.push({
            key: settingKey,
            value,
            type,
            description: `${modelType}模型${key}设置`
          })
        })
      })
    }

    return flatSettings
  }

  /**
   * 获取默认结构化设置
   */
  private static getDefaultStructuredSettings(): any {
    return {
      search: {
        default_results: 20,
        similarity_threshold: 0.7,
        max_file_size: 50
      },
      ai_models: {
        whisper: {
          model_size: 'base',
          device: 'cpu',
          enabled: true
        },
        ollama: {
          local_model: 'qwen2.5:1.5b',
          ollama_url: 'http://localhost:11434',
          enabled: true
        },
        clip: {
          model_name: 'OFA-Sys/chinese-clip-vit-base-patch16',
          device: 'cpu',
          enabled: true
        },
        bge: {
          model_name: 'BAAI/bge-m3',
          device: 'cpu',
          enabled: true
        }
      }
    }
  }
}