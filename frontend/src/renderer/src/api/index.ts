// 索引管理API服务

import type {
  IndexCreateRequest,
  IndexStatus
} from '@/types/api'
import { httpClient } from '@/utils/http'
import {
  convertFileTypesToExtensions,
  calculateIndexSizeInGB,
  formatIndexSize,
  calculateSuccessRate,
  getIndexStatusInfo
} from '@/utils/indexUtils'

// 索引管理服务
export class IndexService {
  // 创建索引
  static async createIndex(params: IndexCreateRequest) {
    const formData = new FormData()
    formData.append('folder_path', params.folder_path)
    formData.append('recursive', (params.recursive ?? true).toString())

    // 转换文件类型为扩展名列表
    if (params.file_types && params.file_types.length > 0) {
      const extensions = convertFileTypesToExtensions(params.file_types)
      extensions.forEach(ext => {
        formData.append('file_types', ext)
      })
    }

    return await httpClient.postFormData('/api/index/create', formData)
  }

  // 查询索引状态
  static async getIndexStatus(id: number) {
    return await httpClient.get(`/api/index/status/${id}`)
  }

  // 索引列表
  static async getIndexList(status?: string, limit = 10, offset = 0) {
    const params = new URLSearchParams()
    if (status && status !== 'all') {
      params.append('status', status)
    }
    params.append('limit', limit.toString())
    params.append('offset', offset.toString())

    return await httpClient.get(`/api/index/list?${params}`)
  }

  // 删除索引
  static async deleteIndex(id: number) {
    return await httpClient.delete(`/api/index/${id}`)
  }

  // 停止索引
  static async stopIndex(id: number) {
    return await httpClient.post(`/api/index/${id}/stop`)
  }

  // 更新索引
  static async updateIndex(params: IndexCreateRequest) {
    const formData = new FormData()
    formData.append('folder_path', params.folder_path)
    formData.append('recursive', (params.recursive ?? true).toString())

    // 转换文件类型为扩展名列表
    if (params.file_types && params.file_types.length > 0) {
      const extensions = convertFileTypesToExtensions(params.file_types)
      extensions.forEach(ext => {
        formData.append('file_types', ext)
      })
    }

    return await httpClient.postFormData('/api/index/update', formData)
  }

  // 备份索引
  static async backupIndex(backupName?: string) {
    const params = backupName ? `?backup_name=${encodeURIComponent(backupName)}` : ''
    return await httpClient.post(`/api/index/backup${params}`)
  }

  // 获取已索引文件列表
  static async getIndexedFiles(folderPath?: string, fileType?: string, indexStatus?: string, limit = 20, offset = 0) {
    const params = new URLSearchParams()
    if (folderPath) params.append('folder_path', folderPath)
    if (fileType) params.append('file_type', fileType)
    if (indexStatus) params.append('index_status', indexStatus)
    params.append('limit', limit.toString())
    params.append('offset', offset.toString())

    return await httpClient.get(`/api/index/files?${params}`)
  }

  // 删除文件索引
  static async deleteFileIndex(fileId: number) {
    return await httpClient.delete(`/api/index/files/${fileId}`)
  }

  // 获取系统索引状态
  static async getSystemStatus() {
    const response = await httpClient.get('/api/index/status')

    // 适配后端数据格式为前端需要的格式
    const { data } = response
    const indexSizeBytes = data.index_stats?.index_size_bytes || 0
    const adaptedData = {
      totalFiles: data.database_stats?.indexed_files || 0,
      indexSizeBytes, // 保留原始字节数，让前端组件自己格式化
      indexSize: calculateIndexSizeInGB(indexSizeBytes), // 保持兼容性
      activeTasks: data.job_stats?.processing_jobs || 0,
      successRate: calculateSuccessRate(
        data.database_stats?.indexed_files || 0,
        (data.database_stats?.indexed_files || 0) + (data.database_stats?.failed_files || 0)
      )
    }

    return {
      success: true,
      data: adaptedData,
      message: response.message
    }
  }
}