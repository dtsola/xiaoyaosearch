import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: {
        title: '小遥搜索 XiaoyaoSearch'
      }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: {
        title: '设置 - 小遥搜索'
      }
    },
    {
      path: '/index',
      name: 'Index',
      component: () => import('@/views/Index.vue'),
      meta: {
        title: '索引管理 - 小遥搜索'
      }
    },
    {
      path: '/help',
      name: 'Help',
      component: () => import('@/views/Help.vue'),
      meta: {
        title: '帮助 - 小遥搜索'
      }
    },
    {
      path: '/about',
      name: 'About',
      component: () => import('@/views/About.vue'),
      meta: {
        title: '关于作者 - 小遥搜索'
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router