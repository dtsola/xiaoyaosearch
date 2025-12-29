import { createRouter, createMemoryHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: {
        titleKey: 'app.title'
      }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: {
        titleKey: 'settings.title'
      }
    },
    {
      path: '/index',
      name: 'Index',
      component: () => import('@/views/Index.vue'),
      meta: {
        titleKey: 'index.title'
      }
    },
    {
      path: '/help',
      name: 'Help',
      component: () => import('@/views/Help.vue'),
      meta: {
        titleKey: 'help.title'
      }
    },
    {
      path: '/about',
      name: 'About',
      component: () => import('@/views/About.vue'),
      meta: {
        titleKey: 'about.title'
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  // 注意：由于路由守卫在i18n初始化之前执行，这里暂时使用硬编码
  // 实际标题更新会在i18n初始化后通过watch监听路由变化来更新
  next()
})

export default router