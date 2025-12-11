// HTTP 客户端工具
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'ant-design-vue'

// 创建 axios 实例
const http: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 后端 API 地址
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
http.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 可以在这里添加认证 token 等
    // console.log('发送请求:', config)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
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
    console.error('响应错误:', error)

    // 处理不同类型的错误
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response

      switch (status) {
        case 400:
          message.error(data.detail || '请求参数错误')
          break
        case 401:
          message.error('未授权访问')
          break
        case 403:
          message.error('禁止访问')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 422:
          message.error(data.detail || '数据验证失败')
          break
        case 500:
          message.error('服务器内部错误')
          break
        default:
          message.error(`请求失败: ${status}`)
      }
    } else if (error.request) {
      // 网络错误
      message.error('网络连接失败，请检查后端服务是否运行')
    } else {
      // 其他错误
      message.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

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