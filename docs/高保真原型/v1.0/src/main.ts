import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import i18n from './i18n/config'
import { setLocale } from './i18n/setup'
import 'ant-design-vue/dist/reset.css'
import 'dayjs/locale/zh-cn'
import 'dayjs/locale/en'
import './styles/index.css'

// 初始化 Day.js 语言
setLocale(i18n.global.locale.value)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)
app.use(i18n)

app.mount('#app')