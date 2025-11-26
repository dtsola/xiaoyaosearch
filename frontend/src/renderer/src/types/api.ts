// API 接口类型定义

// 输入类型枚举
export enum InputType {
  TEXT = 'text',
  VOICE = 'voice',
  IMAGE = 'image'
}

// 搜索类型枚举
export enum SearchType {
  SEMANTIC = 'semantic',
  FULLTEXT = 'fulltext',
  HYBRID = 'hybrid'
}

// 文件类型枚举
export enum FileType {
  VIDEO = 'video',
  AUDIO = 'audio',
  DOCUMENT = 'document',
  IMAGE = 'image'
}

// 搜索请求
export interface SearchRequest {
  query: string;
  input_type?: InputType;
  search_type?: SearchType;
  limit?: number;
  threshold?: number;
  file_types?: FileType[];
}

// 多模态请求
export interface MultimodalRequest {
  input_data: string;
  input_type: InputType;
  duration?: number;
}

// 索引创建请求
export interface IndexCreateRequest {
  folder_path: string;
  file_types?: string[];
  recursive?: boolean;
}

// AI模型配置请求
export interface AIModelConfigRequest {
  model_type: string;
  provider: string;
  model_name: string;
  config: Record<string, any>;
}

// 搜索结果
export interface SearchResult {
  file_id: number;
  file_name: string;
  file_path: string;
  file_type: FileType;
  relevance_score: number;
  preview_text: string;
  highlight: string;
  created_at: string;
  modified_at: string;
  file_size: number;
  match_type: string;
}

// 统一响应格式
export interface SearchResponse {
  success: boolean;
  data: {
    results: SearchResult[];
    total: number;
    search_time: number;
    query_used: string;
    input_processed: boolean;
  };
  message?: string;
}

// 多模态响应
export interface MultimodalResponse {
  success: boolean;
  data: {
    converted_text: string;
    confidence: number;
    search_results: SearchResult[];
    file_info: {
      filename: string;
      size: number;
      content_type: string;
    };
  };
  message?: string;
}

// 搜索历史
export interface SearchHistory {
  id: number;
  search_query: string;
  input_type: InputType;
  search_type: SearchType;
  ai_model_used: string;
  result_count: number;
  response_time: number;
  created_at: string;
}

// 索引状态
export interface IndexStatus {
  index_id: number;
  folder_path: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total_files?: number;
  processed_files?: number;
  error_count?: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

// AI模型配置
export interface AIModelConfig {
  id: number;
  model_type: string;
  provider: string;
  model_name: string;
  config_json: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 应用设置
export interface AppSettings {
  app_name: string;
  version: string;
  search: {
    default_limit: number;
    default_threshold: number;
    max_file_size: number;
  };
  indexing: {
    max_concurrent_jobs: number;
    supported_formats: string[];
    auto_rebuild: boolean;
  };
  ui: {
    theme: string;
    language: string;
  };
}

// 系统健康状态
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database: {
    status: string;
    response_time: number;
  };
  ai_models: Record<string, {
    status: string;
    memory_usage?: string;
    error?: string;
  }>;
  indexes: Record<string, {
    status: string;
    document_count: number;
  }>;
  timestamp: string;
}