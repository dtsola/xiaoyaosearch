import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles/index.css'

// 国际化支持
import i18n from './i18n/config'

// 系统字体加载器
import fontLoader from './utils/font-loader'

// 初始化系统字体
fontLoader.initSystemFonts()

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)
app.use(i18n)

app.mount('#app')
