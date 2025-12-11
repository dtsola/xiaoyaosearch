// 系统状态API服务

import type { SystemHealth } from '@/types/api'
import { httpClient } from '@/utils/http'

// 系统状态服务
export class SystemService {
  // 获取系统健康状态
  static async getHealth() {
    return await httpClient.get('/api/system/health')
  }

  // 获取系统状态汇总（为底部状态栏设计）
  static async getStatus() {
    return await httpClient.get('/api/system/running-status')
  }
}

// Mock 数据服务
export class SystemServiceMock {
  static async getHealth(): Promise<SystemHealth> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 100))

    return {
      status: 'healthy',
      database: {
        status: 'connected',
        response_time: 0.02
      },
      ai_models: {
        'BGE-M3': {
          status: 'loaded',
          memory_usage: '2.1GB'
        },
        'FasterWhisper': {
          status: 'loaded',
          memory_usage: '1.8GB'
        },
        'CN-CLIP': {
          status: 'loaded',
          memory_usage: '1.5GB'
        },
        'Ollama': {
          status: 'available'
        }
      },
      indexes: {
        'faiss': {
          status: 'ready',
          document_count: 1234
        },
        'whoosh': {
          status: 'ready',
          document_count: 1234
        }
      },
      timestamp: new Date().toISOString()
    }
  }

  static async getStatus() {
    await new Promise(resolve => setTimeout(resolve, 100))

    return {
      success: true,
      data: {
        index_status: '正常',
        data_count: 1234,
        today_searches: 89,
        system_status: '系统正常',
        last_update: new Date().toISOString()
      }
    }
  }
}