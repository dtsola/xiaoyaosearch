// HTTP 客户端工具
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosRequestConfig } from 'axios'
import { message } from 'ant-design-vue'
import i18n from '@/i18n/config'

// 获取翻译函数的辅助方法
const t = (key: string, params?: Record<string, any>): string => {
  return i18n.global.t(key, params)
}

// 后端 API 地址
// 可通过项目根目录的 .env 文件中的 VITE_API_BASE_URL 覆盖（需与后端 .env 的 API_PORT 保持一致），
// 未配置时回退到默认地址；固定使用 IPv4 避免 localhost 解析到 IPv6 导致连接失败
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

if (import.meta.env.DEV) {
  console.log('[http] 后端 API 地址:', API_BASE_URL)
}

// 创建 axios 实例
const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10分钟超时
  headers: {
    'Content-Type': 'application/json',
  },
  // Electron特殊配置
  withCredentials: false,
  // 禁用代理确保直连
  proxy: false,
})

// 请求拦截器
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加认证 token 等
    // console.log('发送请求:', config)
    return config
  },
  (error) => {
    console.error(t('http.requestError'), error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    // console.log('收到响应:', response)
    return response
  },
  (error) => {
    console.error(t('http.responseError'), error)

    // 处理不同类型的错误
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response

      switch (status) {
        case 400:
          message.error(data.detail || t('http.badRequest'))
          break
        case 401:
          message.error(t('http.unauthorized'))
          break
        case 403:
          message.error(t('http.forbidden'))
          break
        case 404:
          message.error(t('http.notFound'))
          break
        case 422:
          message.error(data.detail || t('http.validationFailed'))
          break
        case 500:
          message.error(t('http.internalServerError'))
          break
        default:
          message.error(`${t('http.requestFailed')}: ${status}`)
      }
    } else if (error.request) {
      // 网络错误
      message.error(t('http.networkError'))
    } else {
      // 其他错误
      message.error(t('http.configError'))
    }

    return Promise.reject(error)
  }
)

// 测试网络连接
export const testConnection = async (): Promise<boolean> => {
  try {
    console.log('测试网络连接到后端...')
    const response = await axios.get(`${API_BASE_URL}/`, {
      timeout: 5000,
      proxy: false
    })
    console.log('网络连接测试成功:', response.status)
    return true
  } catch (error) {
    console.error('网络连接测试失败:', error)
    return false
  }
}

// 封装常用的 HTTP 方法
export const httpClient = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return http.get(url, config).then(res => res.data)
  },

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return http.post(url, data, config).then(res => res.data)
  },

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return http.put(url, data, config).then(res => res.data)
  },

  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return http.delete(url, config).then(res => res.data)
  },

  // 用于文件上传
  postFormData: <T = any>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<T> => {
    return http.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
    }).then(res => res.data)
  }
}

export default http