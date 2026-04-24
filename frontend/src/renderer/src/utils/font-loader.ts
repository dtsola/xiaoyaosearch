/**
 * 字体加载器（系统字体方案）
 * 版本: v2.0.0
 * 说明: v2.0 使用系统字体，不再加载外部字体
 * 保留此工具类以备将来需要加载其他字体资源
 */

export interface FontLoadOptions {
  families: string[]
  timeout?: number
  onSuccess?: () => void
  onError?: () => void
}

/**
 * FontLoader 类
 * 使用单例模式
 * v2.0: 使用系统字体，保留接口以备扩展
 */
export class FontLoader {
  private static instance: FontLoader
  private loadedFonts = new Set<string>()

  private constructor() {}

  /**
   * 获取单例实例
   */
  static getInstance(): FontLoader {
    if (!FontLoader.instance) {
      FontLoader.instance = new FontLoader()
    }
    return FontLoader.instance
  }

  /**
   * 检查系统字体是否可用
   * @param fontFamily 字体名称
   */
  isSystemFontAvailable(fontFamily: string): boolean {
    if (!document.fonts || !document.fonts.check) {
      return true // 降级：假设系统字体可用
    }

    // 检查常见字重是否可用
    const weights = [400, 500, 600, 700]
    return weights.some(weight =>
      document.fonts.check(`${weight} 16px "${fontFamily}", "system-ui`)
    )
  }

  /**
   * 获取已加载字体列表
   */
  getLoadedFonts(): string[] {
    return Array.from(this.loadedFonts)
  }

  /**
   * 初始化系统字体
   * 检查常用系统字体是否可用
   */
  initSystemFonts(): void {
    const systemFonts = [
      'SF Pro Text',
      'SF Pro Display',
      'Segoe UI',
      'PingFang SC',
      'Microsoft YaHei'
    ]

    systemFonts.forEach(font => {
      if (this.isSystemFontAvailable(font)) {
        this.loadedFonts.add(font)
      }
    })

    console.log('系统字体初始化完成，可用字体:', this.getLoadedFonts())
  }
}

// 导出单例实例
export default FontLoader.getInstance()
