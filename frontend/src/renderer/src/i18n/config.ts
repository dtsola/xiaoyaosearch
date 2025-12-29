/**
 * Vue I18n 配置
 * XiaoyaoSearch - 小遥搜索
 */

import { createI18n } from 'vue-i18n'
import messages from '@/locales'

/**
 * 获取默认语言
 * 优先级：localStorage > 浏览器语言 > 默认中文
 */
function getDefaultLocale(): string {
  // 从localStorage读取已保存的语言设置
  const savedLocale = localStorage.getItem('locale')
  if (savedLocale && messages[savedLocale as keyof typeof messages]) {
    return savedLocale
  }

  // 检查浏览器语言
  const browserLang = navigator.language
  if (browserLang.startsWith('zh')) {
    return 'zh-CN'
  } else if (browserLang.startsWith('en')) {
    return 'en-US'
  }

  // 默认返回中文
  return 'zh-CN'
}

/**
 * 创建i18n实例
 */
const i18n = createI18n({
  // 使用组合式API模式
  legacy: false,

  // 当前语言
  locale: getDefaultLocale(),

  // 回退语言
  fallbackLocale: 'zh-CN',

  // 语言包
  messages,

  // 全局注入 $t 函数
  globalInjection: true,

  // 缺失翻译时的处理
  missing: (locale, key) => {
    // 开发环境警告缺失的翻译
    if (import.meta.env.DEV) {
      console.warn(`[i18n] Missing translation: ${key} for locale: ${locale}`)
    }
    return key
  },

  // 日志
  silentTranslationWarn: false, // 开发环境显示警告
  silentFallbackWarn: true, // 隐藏回退警告
  fallbackWarn: false,
  warnHtmlMessage: false // 允许HTML消息
})

export default i18n