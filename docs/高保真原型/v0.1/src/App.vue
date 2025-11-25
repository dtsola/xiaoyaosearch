<template>
  <a-layout class="app-layout">
    <!-- 顶部导航 -->
    <a-layout-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-text">◤小遥搜索◢</span>
          <span class="version">v2.0</span>
        </div>

        <a-menu
          v-model:selectedKeys="currentRoute"
          mode="horizontal"
          class="nav-menu"
          @click="handleMenuClick"
        >
          <a-menu-item key="home">
            <HomeOutlined />
            首页
          </a-menu-item>
          <a-menu-item key="settings">
            <SettingOutlined />
            设置
          </a-menu-item>
          <a-menu-item key="index">
            <DatabaseOutlined />
            索引
          </a-menu-item>
          <a-menu-item key="help">
            <QuestionCircleOutlined />
            帮助
          </a-menu-item>
        </a-menu>

        <div class="header-actions">
          <!-- 关于作者 -->
          <a-button type="text" class="header-btn" @click="goToAbout">
            <InfoCircleOutlined />
            <span class="btn-text">关于作者</span>
          </a-button>

          <!-- 用户信息 -->
          <a-button type="text" class="header-btn user-btn">
            <UserOutlined />
            <span class="user-name">小遥用户</span>
          </a-button>
        </div>
      </div>
    </a-layout-header>

    <!-- 主内容区 -->
    <a-layout-content class="app-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </a-layout-content>

    <!-- 底部状态栏 -->
    <a-layout-footer class="app-footer">
      <div class="footer-content">
        <div class="status-info">
          <span class="status-item">
            <DatabaseOutlined />
            索引: {{ indexCount.toLocaleString() }}文件
          </span>
          <span class="status-item">
            <HddOutlined />
            数据: {{ formatFileSize(dataSize) }}
          </span>
          <span class="status-item">
            <SearchOutlined />
            今日: {{ searchCount }}次搜索
          </span>
        </div>
        <div class="system-status">
          <a-tag color="green" class="status-tag">
            <CheckCircleOutlined />
            系统正常
          </a-tag>
          <span class="last-update">
            最后更新: {{ formatTime(lastUpdate) }}
          </span>
        </div>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  HomeOutlined,
  SettingOutlined,
  DatabaseOutlined,
  QuestionCircleOutlined,
  InfoCircleOutlined,
  UserOutlined,
  CheckCircleOutlined,
  HddOutlined,
  SearchOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()

// 响应式数据
const indexCount = ref(1234)
const dataSize = ref(8700000000) // 8.7GB
const searchCount = ref(15)
const lastUpdate = ref(new Date())

// 当前路由
const currentRoute = computed(() => {
  const path = route.path
  if (path === '/' || path === '/home') return ['home']
  if (path === '/settings') return ['settings']
  if (path === '/index') return ['index']
  if (path === '/help') return ['help']
  if (path === '/about') return ['about']
  return []
})

// 菜单点击处理
const handleMenuClick = ({ key }: { key: string }) => {
  const routeMap: Record<string, string> = {
    home: '/',
    settings: '/settings',
    index: '/index',
    help: '/help'
  }

  if (routeMap[key]) {
    router.push(routeMap[key])
  }
}

// 跳转到关于作者页面
const goToAbout = () => {
  router.push('/about')
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (date: Date): string => {
  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载
onMounted(() => {
  // 模拟实时数据更新
  setInterval(() => {
    lastUpdate.value = new Date()
  }, 60000)
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: var(--surface-01);
  border-bottom: 1px solid var(--border-light);
  padding: 0;
  height: 64px;
  line-height: 64px;
  box-shadow: var(--shadow-sm);
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 var(--space-6);
}

.logo {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--primary-600);
}

.logo-text {
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.version {
  margin-left: var(--space-2);
  font-size: 0.75rem;
  color: var(--text-tertiary);
  background: var(--primary-100);
  padding: 2px 6px;
  border-radius: var(--radius-base);
}

.nav-menu {
  flex: 1;
  margin-left: var(--space-8);
  border-bottom: none;
  background: transparent;
}

.nav-menu .ant-menu-item {
  border-bottom: none;
  margin: 0 var(--space-2);
}

.nav-menu .ant-menu-item:hover {
  color: var(--primary-600);
}

.nav-menu .ant-menu-item-selected {
  color: var(--primary-600);
  background: var(--primary-50);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
  height: 36px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  transition: all var(--transition-base);
  font-size: 14px;
  gap: var(--space-1);
}

.header-btn:hover {
  background: var(--surface-02);
  color: var(--text-primary);
}

.btn-text {
  margin-left: var(--space-1);
  white-space: nowrap;
}

.user-btn {
  min-width: 120px;
  background: var(--primary-50);
  color: var(--primary-600);
  border: 1px solid var(--primary-200);
}

.user-btn:hover {
  background: var(--primary-100);
  color: var(--primary-700);
}

.user-name {
  margin-left: var(--space-1);
  font-weight: 500;
}

.app-content {
  flex: 1;
  overflow: hidden;
  background: var(--bg-secondary);
}

.content-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-6);
}

.app-footer {
  background: var(--surface-01);
  border-top: 1px solid var(--border-light);
  padding: var(--space-3) 0;
  height: auto;
  line-height: normal;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
}

.status-info {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.system-status {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.status-tag {
  font-size: 0.75rem;
}

.last-update {
  color: var(--text-tertiary);
  font-size: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 var(--space-4);
  }

  .nav-menu {
    margin-left: var(--space-4);
  }

  .user-name {
    display: none;
  }

  .footer-content {
    flex-direction: column;
    gap: var(--space-2);
    text-align: center;
  }

  .status-info {
    gap: var(--space-4);
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>