/// <reference types="vite/client" />

// 环境变量类型声明（见 frontend/.env.example）
interface ImportMetaEnv {
  /** 后端 API 地址，需与 backend/.env 的 API_HOST + API_PORT 一致 */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface WindowAPI {
  openFile: (filePath: string) => Promise<{ success: boolean; error?: string }>
}

declare interface Window {
  electron: ElectronAPI
  api: WindowAPI
}
