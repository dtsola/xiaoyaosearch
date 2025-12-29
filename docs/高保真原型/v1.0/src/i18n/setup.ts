import zhCN from 'ant-design-vue/es/locale/zh_CN'
import enUS from 'ant-design-vue/es/locale/en_US'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import 'dayjs/locale/en'

/**
 * 设置语言环境
 * @param locale 语言代码 ('zh-CN' | 'en-US')
 * @returns Ant Design locale 对象
 */
export const setLocale = (locale: string) => {
  // 设置 Ant Design locale
  const antdLocale = locale === 'zh-CN' ? zhCN : enUS

  // 设置 Day.js locale
  const dayjsLocale = locale === 'zh-CN' ? 'zh-cn' : 'en'
  dayjs.locale(dayjsLocale)

  return antdLocale
}