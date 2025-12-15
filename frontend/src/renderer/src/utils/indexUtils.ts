/**
 * 索引管理工具函数
 * 处理文件类型转换、数据格式适配等功能
 */

// 文件类型映射配置
export const FILE_TYPE_MAPPING = {
  document: [
    '.txt', '.md', '.markdown', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.ppt', '.pptx', '.rtf', '.odt'
  ],
  audio: [
    '.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a', '.wma'
  ],
  video: [
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'
  ],
  image: [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'
  ]
}

// 反向映射：从扩展名到文件类型
export const EXTENSION_TO_TYPE = Object.entries(FILE_TYPE_MAPPING).reduce(
  (acc, [type, extensions]) => {
    extensions.forEach(ext => {
      acc[ext.toLowerCase()] = type as keyof typeof FILE_TYPE_MAPPING
    })
    return acc
  },
  {} as Record<string, keyof typeof FILE_TYPE_MAPPING>
)

/**
 * 将前端文件类型转换为后端扩展名列表
 * @param fileTypes 前端文件类型数组
 * @returns 后端扩展名数组
 */
export function convertFileTypesToExtensions(fileTypes: string[]): string[] {
  const extensions: string[] = []

  fileTypes.forEach(type => {
    if (type in FILE_TYPE_MAPPING) {
      extensions.push(...FILE_TYPE_MAPPING[type as keyof typeof FILE_TYPE_MAPPING])
    }
  })

  // 去重并排序
  return [...new Set(extensions)].sort()
}

/**
 * 将后端扩展名转换为前端文件类型
 * @param extensions 后端扩展名数组
 * @returns 前端文件类型数组
 */
export function convertExtensionsToFileTypes(extensions: string[]): string[] {
  const fileTypes = new Set<string>()

  extensions.forEach(ext => {
    const normalizedExt = ext.toLowerCase()
    if (!normalizedExt.startsWith('.')) {
      ext = '.' + normalizedExt
    }

    const fileType = EXTENSION_TO_TYPE[normalizedExt]
    if (fileType) {
      fileTypes.add(fileType)
    }
  })

  return Array.from(fileTypes)
}

/**
 * 根据文件扩展名获取文件类型
 * @param filename 文件名
 * @returns 文件类型
 */
export function getFileType(filename: string): keyof typeof FILE_TYPE_MAPPING {
  const ext = filename.toLowerCase().split('.').pop()
  if (!ext) return 'document' // 默认类型

  const fileType = EXTENSION_TO_TYPE['.' + ext]
  return fileType || 'document'
}

/**
 * 获取文件类型的显示名称
 * @param type 文件类型
 * @returns 显示名称
 */
export function getFileTypeDisplayName(type: string): string {
  const displayNames: Record<string, string> = {
    document: '文档',
    audio: '音频',
    video: '视频',
    image: '图片'
  }
  return displayNames[type] || type
}

/**
 * 计算索引大小（从字节转换为GB）
 * @param bytes 字节数
 * @returns GB数
 */
export function calculateIndexSizeInGB(bytes: number): number {
  return bytes / (1024 * 1024 * 1024)
}

/**
 * 格式化索引大小为合适的单位
 * @param bytes 字节数
 * @returns 格式化后的对象 {value, unit}
 */
export function formatIndexSize(bytes: number): { value: number; unit: string } {
  if (bytes === 0) {
    return { value: 0, unit: 'B' }
  }

  const gb = bytes / (1024 * 1024 * 1024)
  const mb = bytes / (1024 * 1024)
  const kb = bytes / 1024

  if (gb >= 1) {
    return { value: gb, unit: 'GB' }
  } else if (mb >= 1) {
    return { value: mb, unit: 'MB' }
  } else if (kb >= 1) {
    return { value: kb, unit: 'KB' }
  } else {
    return { value: bytes, unit: 'B' }
  }
}

/**
 * 计算成功率
 * @param processed 已处理数
 * @param total 总数
 * @returns 成功率百分比
 */
export function calculateSuccessRate(processed: number, total: number): number {
  if (total === 0) return 0
  return Number(((processed / total) * 100).toFixed(1))
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化的文件大小字符串
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 索引状态映射
 */
export const INDEX_STATUS_MAPPING = {
  pending: { label: '等待中', color: 'default', antdColor: 'default' },
  processing: { label: '处理中', color: 'processing', antdColor: 'processing' },
  completed: { label: '已完成', color: 'success', antdColor: 'success' },
  failed: { label: '失败', color: 'error', antdColor: 'error' }
}

/**
 * 获取索引状态信息
 * @param status 状态值
 * @returns 状态信息
 */
export function getIndexStatusInfo(status: string) {
  return INDEX_STATUS_MAPPING[status as keyof typeof INDEX_STATUS_MAPPING] || {
    label: status,
    color: 'default',
    antdColor: 'default'
  }
}