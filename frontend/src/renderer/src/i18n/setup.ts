/**
 * Ant Design Vue 和 Day.js 语言包集成
 * XiaoyaoSearch - 小遥搜索
 */

import zhCN from 'ant-design-vue/es/locale/zh_CN'
import enUS from 'ant-design-vue/es/locale/en_US'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import 'dayjs/locale/en'

/**
 * Ant Design Vue 语言包映射
 */
export const antdLocales = {
  'zh-CN': zhCN,
  'en-US': enUS
}

/**
 * Day.js 语言包映射
 */
export const dayjsLocales = {
  'zh-CN': 'zh-cn',
  'en-US': 'en'
}

/**
 * 设置 Ant Design 和 Day.js 的语言
 * @param locale 语言代码
 * @returns Ant Design 语言配置对象
 */
export function setLocale(locale: string) {
  const antdLocale = antdLocales[locale as keyof typeof antdLocales] || zhCN
  const dayjsLocale = dayjsLocales[locale as keyof typeof dayjsLocales] || 'zh-cn'

  // 设置 dayjs 语言
  dayjs.locale(dayjsLocale)

  return antdLocale
}

/**
 * 获取所有支持的语言列表
 */
export function getSupportedLocales() {
  return [
    {
      label: '简体中文',
      value: 'zh-CN',
      icon: '🇨🇳'
    },
    {
      label: 'English',
      value: 'en-US',
      icon: '🇺🇸'
    }
  ]
}