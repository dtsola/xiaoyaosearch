import axios from 'axios'

// API 配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)

    // 统一错误处理
    const errorMessage = error.response?.data?.error?.message || error.message || '请求失败'

    // 根据状态码进行特殊处理
    if (error.response?.status === 401) {
      // 未授权处理
    } else if (error.response?.status === 403) {
      // 禁止访问处理
    } else if (error.response?.status === 500) {
      // 服务器错误处理
    }

    return Promise.reject(new Error(errorMessage))
  }
)

export default api