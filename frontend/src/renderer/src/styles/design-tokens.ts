/**
 * 设计系统类型定义和工具函数
 * 版本: v2.0.0
 * 设计风格: Notion温暖明亮风格
 */

/**
 * 颜色令牌类型
 */
export type ColorToken =
  | 'bg-primary'
  | 'bg-secondary'
  | 'bg-tertiary'
  | 'bg-hover'
  | 'text-primary'
  | 'text-secondary'
  | 'text-tertiary'
  | 'text-muted'
  | 'brand-blue'
  | 'brand-blue-hover'
  | 'brand-blue-light'
  | 'brand-blue-lighter'
  | 'success-green'
  | 'warning-orange'
  | 'accent-purple'

/**
 * 圆角令牌类型
 */
export type RadiusToken = 'sm' | 'md' | 'lg' | 'xl' | 'pill'

/**
 * 间距令牌类型
 */
export type SpaceToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl'

/**
 * 文字大小令牌类型
 */
export type TextToken = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl'

/**
 * 图标尺寸令牌类型
 */
export type IconToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

/**
 * 设计令牌工具函数
 * 用于安全地访问CSS变量
 *
 * @example
 * ```ts
 * import { tokens } from '@/styles/design-tokens'
 *
 * const color = tokens.color('bg-primary')
 * const radius = tokens.radius('xl')
 * ```
 */
export const tokens = {
  /**
   * 获取颜色变量
   * @param name 颜色名称
   * @returns CSS变量字符串
   * @example tokens.color('bg-primary') => 'var(--bg-primary)'
   */
  color: (name: ColorToken): string => `var(--${name})`,

  /**
   * 获取圆角变量
   * @param name 圆角名称
   * @returns CSS变量字符串
   */
  radius: (name: RadiusToken): string => `var(--radius-${name})`,

  /**
   * 获取间距变量
   * @param name 间距名称
   * @returns CSS变量字符串
   */
  space: (name: SpaceToken): string => `var(--space-${name})`,

  /**
   * 获取文字大小变量
   * @param name 文字大小名称
   * @returns CSS变量字符串
   */
  text: (name: TextToken): string => `var(--text-${name})`,

  /**
   * 获取图标尺寸变量
   * @param name 图标尺寸名称
   * @returns CSS变量字符串
   */
  icon: (name: IconToken): string => `var(--icon-${name})`,

  // 阴影
  shadowCard: 'var(--shadow-card)',
  shadowElevated: 'var(--shadow-elevated)',
  shadowFocus: 'var(--shadow-focus)',

  // 字体
  fontDisplay: 'var(--font-display)',
  fontBody: 'var(--font-body)',
  fontCode: 'var(--font-code)',

  // 过渡
  transitionFast: 'var(--transition-fast)',
  transitionBase: 'var(--transition-base)',
  transitionSlow: 'var(--transition-slow)',
} as const

/**
 * 类型导出
 */
export type Tokens = typeof tokens
