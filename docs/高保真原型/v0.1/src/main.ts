import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'

// 导入全局样式
import './styles/global.scss'

// 导入 Ant Design Vue 样式
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)
const pinia = createPinia()

// 配置 Ant Design Vue
app.use(Antd)
app.use(pinia)

// 全局配置
app.config.globalProperties.$ELEMENT_SIZE = 'default'

// 挂载应用
app.mount('#app')