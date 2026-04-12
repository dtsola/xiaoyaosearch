// 术语库API服务
import { httpClient } from '@/utils/http'

// 术语库数据类型
export interface GlossaryCollection {
  id: number
  name: string
  description?: string
  icon?: string
  color?: string
  is_enabled: boolean
  term_count: number
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface GlossaryCollectionCreate {
  name: string
  description?: string
  icon?: string
  color?: string
}

export interface GlossaryCollectionUpdate {
  name?: string
  description?: string
  icon?: string
  color?: string
  is_enabled?: boolean
}

export interface GlossaryCollectionListResponse {
  items: GlossaryCollection[]
  total: number
  page: number
  page_size: number
}

// 术语数据类型
export interface GlossaryTerm {
  id: number
  collection_id: number
  term: string
  synonyms: string[]
  description?: string
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface GlossaryTermCreate {
  term: string
  synonyms: string[]
  description?: string
}

export interface GlossaryTermUpdate {
  term?: string
  synonyms?: string[]
  description?: string
  is_enabled?: boolean
}

export interface GlossaryTermListResponse {
  collection_id: number
  collection_name: string
  items: GlossaryTerm[]
  total: number
  page: number
  page_size: number
}

// 查询扩展相关类型
export interface MatchedTerm {
  id: number
  term: string
  synonyms: string[]
  collection_id: number
  collection_name: string
}

export interface GlossaryExpandRequest {
  query: string
  collection_ids?: number[]
}

export interface GlossaryExpandResponse {
  original_query: string
  matched_terms: MatchedTerm[]
  expanded_queries: string[]
  used_collections: string[]
}

// CSV导入响应
export interface GlossaryImportResponse {
  imported_count: number
  failed_count: number
  errors: Array<{
    row: number
    term: string
    error: string
  }>
}

// 术语扩展配置
export interface GlossaryExpansionConfig {
  enable: boolean
  collection_ids?: number[] | null
  max_expansion_terms?: number
}

export interface GlossaryExpansionConfigData {
  enable: boolean
  collection_ids?: number[] | null
  max_expansion_terms: number
  available_collections: Array<{
    id: number
    name: string
    description?: string
    icon?: string
    color?: string
    term_count: number
  }>
}

export interface GlossaryExpansionConfigResponse {
  success: boolean
  data: GlossaryExpansionConfigData
}

// 术语库服务
export class GlossaryService {
  // ========== 术语库管理 ==========

  // 获取术语库列表
  static async getCollections(page = 1, pageSize = 20, isEnabled?: boolean) {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    if (isEnabled !== undefined) {
      params.append('is_enabled', isEnabled.toString())
    }

    return await httpClient.get(`/api/glossary/collections/?${params}`)
  }

  // 获取单个术语库
  static async getCollection(id: number) {
    return await httpClient.get(`/api/glossary/collections/${id}`)
  }

  // 创建术语库
  static async createCollection(data: GlossaryCollectionCreate) {
    return await httpClient.post('/api/glossary/collections/', data)
  }

  // 更新术语库
  static async updateCollection(id: number, data: GlossaryCollectionUpdate) {
    return await httpClient.put(`/api/glossary/collections/${id}`, data)
  }

  // 删除术语库
  static async deleteCollection(id: number) {
    return await httpClient.delete(`/api/glossary/collections/${id}`)
  }

  // 获取启用的术语库
  static async getEnabledCollections() {
    return await httpClient.get('/api/glossary/collections/enabled/list')
  }

  // ========== 术语管理 ==========

  // 获取术语列表
  static async getTerms(collectionId: number, page = 1, pageSize = 20, isEnabled?: boolean) {
    const params = new URLSearchParams()
    params.append('collection_id', collectionId.toString())
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    if (isEnabled !== undefined) {
      params.append('is_enabled', isEnabled.toString())
    }

    return await httpClient.get(`/api/glossary/terms/?${params}`)
  }

  // 获取单个术语
  static async getTerm(id: number) {
    return await httpClient.get(`/api/glossary/terms/${id}`)
  }

  // 创建术语
  static async createTerm(collectionId: number, data: GlossaryTermCreate) {
    const params = new URLSearchParams()
    params.append('collection_id', collectionId.toString())

    return await httpClient.post(`/api/glossary/terms/?${params}`, data)
  }

  // 更新术语
  static async updateTerm(collectionId: number, id: number, data: GlossaryTermUpdate) {
    const params = new URLSearchParams()
    params.append('collection_id', collectionId.toString())

    return await httpClient.put(`/api/glossary/terms/${id}?${params}`, data)
  }

  // 删除术语
  static async deleteTerm(collectionId: number, id: number) {
    const params = new URLSearchParams()
    params.append('collection_id', collectionId.toString())

    return await httpClient.delete(`/api/glossary/terms/${id}?${params}`)
  }

  // CSV导入
  static async importFromCSV(collectionId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('collection_id', collectionId.toString())

    return await httpClient.post(`/api/glossary/terms/import?collection_id=${collectionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  // CSV导出
  static async exportToCSV(collectionId: number, locale: string = 'zh-CN') {
    const response = await httpClient.get(`/api/glossary/terms/export/${collectionId}`, {
      responseType: 'blob',
      headers: {
        'Accept-Language': locale
      }
    })

    // 创建下载链接
    const blob = new Blob([response as any], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `glossary_${collectionId}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return response
  }

  // ========== 查询扩展 ==========

  // 扩展查询词
  static async expandQuery(query: string, collectionIds?: number[]) {
    return await httpClient.post('/api/glossary/expand', {
      query,
      collection_ids: collectionIds
    })
  }

  // ========== 术语扩展设置 ==========

  // 获取术语扩展配置
  static async getExpansionConfig(): Promise<GlossaryExpansionConfigResponse> {
    return await httpClient.get('/api/glossary/settings/')
  }

  // 更新术语扩展配置
  static async updateExpansionConfig(config: GlossaryExpansionConfig) {
    return await httpClient.post('/api/glossary/settings/', config)
  }
}
