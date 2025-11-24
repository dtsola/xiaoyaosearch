<template>
  <header class="app-header">
    <!-- 应用标题区域 -->
    <div class="header-title">
      <div class="app-logo">
        <span class="logo-text">◤小遥搜索◢</span>
        <span class="version-badge">v2.0</span>
      </div>
    </div>

    <!-- 主导航菜单 -->
    <nav class="main-nav">
      <div class="nav-items">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'active': isActiveRoute(item.path) }"
        >
          <SimpleIcon :type="item.icon" class="nav-icon" />
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 右侧工具栏 -->
    <div class="header-actions">
      <!-- 通知图标 -->
      <div class="action-item notification" @click="handleNotificationClick">
        <Badge :count="notificationCount" :offset="[0, 4]">
          <SimpleIcon type="bell" class="action-icon" />
        </Badge>
      </div>

      <!-- 主题切换 -->
      <div class="action-item theme-toggle" @click="handleThemeToggle">
        <SimpleIcon :type="isDarkTheme ? 'sun' : 'moon'" class="action-icon" />
      </div>

      <!-- 用户菜单 -->
      <a-dropdown placement="bottomRight" :trigger="['click']">
        <div class="action-item user-menu">
          <Avatar class="user-avatar" :size="32">
            <SimpleIcon type="user" />
          </Avatar>
          <span class="user-name">admin</span>
          <SimpleIcon type="down" class="dropdown-icon" />
        </div>
        <template #overlay>
          <a-menu class="user-dropdown-menu">
            <a-menu-item key="profile" @click="handleProfile">
              <SimpleIcon type="user" />
              个人资料
            </a-menu-item>
            <a-menu-item key="settings" @click="handleSettings">
              <SimpleIcon type="settings" />
              设置
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="help" @click="handleHelp">
              <SimpleIcon type="question" />
              帮助
            </a-menu-item>
            <a-menu-item key="about" @click="handleAbout">
              <SimpleIcon type="info-circle" />
              关于
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="logout" @click="handleLogout">
              <SimpleIcon type="logout" />
              退出
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <!-- 装饰性背景元素 -->
    <div class="header-decoration">
      <div class="decoration-gradient"></div>
      <div class="decoration-particles">
        <div class="particle" v-for="i in 20" :key="i" :style="getParticleStyle(i)"></div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import { Badge, Avatar, message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const notificationCount = ref(2)
const isDarkTheme = computed(() => appStore.theme === 'dark')

// 导航菜单项
const navItems = [
  {
    name: '首页',
    path: '/',
    icon: 'search'
  },
  {
    name: '设置',
    path: '/settings',
    icon: 'settings'
  },
  {
    name: '索引',
    path: '/index',
    icon: 'database'
  },
  {
    name: '帮助',
    path: '/help',
    icon: 'help'
  }
]

// 判断当前路由是否活跃
const isActiveRoute = (path: string): boolean => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 处理通知点击
const handleNotificationClick = () => {
  message.info('暂无新通知')
  notificationCount.value = 0
}

// 处理主题切换
const handleThemeToggle = () => {
  appStore.toggleTheme()
}

// 用户菜单处理
const handleProfile = () => {
  message.info('个人资料功能开发中')
}

const handleSettings = () => {
  router.push('/settings')
}

const handleHelp = () => {
  router.push('/help')
}

const handleAbout = () => {
  message.info('关于小遥搜索 v2.0')
}

const handleLogout = () => {
  message.warning('退出功能开发中')
}

// 生成粒子样式
const getParticleStyle = (index: number) => {
  const delay = (index * 0.1) % 3
  const duration = 3 + (index % 2) * 2
  const size = 2 + Math.random() * 2
  const opacity = 0.1 + Math.random() * 0.2

  return {
    left: `${Math.random() * 100}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    width: `${size}px`,
    height: `${size}px`,
    opacity
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  position: relative;
  height: var(--nav-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-light);
  z-index: var(--z-fixed);
  overflow: hidden;

  @include glass-morphism;
}

// 应用标题
.header-title {
  flex-shrink: 0;
  z-index: 2;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-text {
  font-size: var(--text-2xl);
  font-weight: 900;
  font-family: var(--font-artistic);
  @include gradient-text;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(0, 229, 255, 0.3);
}

.version-badge {
  font-size: var(--text-xs);
  padding: 2px 6px;
  background: rgba(0, 229, 255, 0.2);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-full);
  font-weight: 600;
  font-family: var(--font-mono);
}

// 主导航
.main-nav {
  flex: 1;
  display: flex;
  justify-content: center;
  z-index: 2;
}

.nav-items {
  display: flex;
  gap: var(--space-2);
  background: rgba(37, 43, 78, 0.6);
  padding: var(--space-1);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-light);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s var(--ease-out-cubic);
  position: relative;
  font-weight: 500;
  min-width: 80px;
  justify-content: center;

  &:hover {
    background: rgba(0, 229, 255, 0.1);
    color: var(--accent-cyan);
    transform: translateY(-1px);
  }

  &.active {
    background: rgba(0, 229, 255, 0.15);
    color: var(--accent-cyan);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 20px;
      height: 3px;
      background: var(--accent-cyan);
      border-radius: var(--radius-full);
      animation: slide-up 0.3s var(--ease-out-cubic);
    }
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.nav-icon {
  font-size: 16px;
}

.nav-text {
  font-size: var(--text-sm);
  white-space: nowrap;
}

// 右侧工具栏
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  z-index: 2;
}

.action-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.3s var(--ease-out-cubic);
  position: relative;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
}

.action-icon {
  font-size: 16px;
  color: var(--text-secondary);
  transition: color 0.3s var(--ease-out-cubic);
}

.action-item:hover .action-icon {
  color: var(--accent-cyan);
}

// 通知特殊样式
.notification {
  .action-icon {
    transition: transform 0.3s var(--ease-out-cubic);
  }

  &:hover {
    .action-icon {
      animation: bell-ring 0.5s ease-in-out;
    }
  }
}

@keyframes bell-ring {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

// 用户菜单
.user-menu {
  width: auto;
  padding: 0 var(--space-2);
  gap: var(--space-2);
  background: rgba(255, 255, 255, 0.05);
}

.user-avatar {
  background: var(--primary-gradient);
  border: 2px solid rgba(0, 229, 255, 0.3);
  transition: all 0.3s var(--ease-out-cubic);

  .action-item:hover & {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.4);
  }
}

.user-name {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-tertiary);
  transition: transform 0.3s var(--ease-out-cubic);
}

.action-item:hover .dropdown-icon {
  transform: translateY(2px);
}

// 用户下拉菜单
.user-dropdown-menu {
  background: var(--surface-tertiary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(20px);
  min-width: 160px;

  :deep(.ant-dropdown-menu-item) {
    color: var(--text-secondary);
    transition: all 0.2s var(--ease-out-cubic);

    &:hover {
      background: rgba(0, 229, 255, 0.1);
      color: var(--accent-cyan);
    }
  }

  :deep(.ant-dropdown-menu-item-icon) {
    color: inherit;
  }
}

// 装饰性背景
.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.decoration-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--accent-cyan) 20%,
    var(--accent-magenta) 50%,
    var(--accent-cyan) 80%,
    transparent 100%
  );
  opacity: 0.6;
  animation: gradient-slide 3s ease-in-out infinite;
}

@keyframes gradient-slide {
  0%, 100% { transform: translateX(-10%); }
  50% { transform: translateX(10%); }
}

.decoration-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: var(--accent-cyan);
  border-radius: 50%;
  animation: float-particle linear infinite;
}

@keyframes float-particle {
  from {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  to {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .app-header {
    padding: 0 var(--space-4);
  }

  .logo-text {
    font-size: var(--text-xl);
  }

  .nav-items {
    gap: var(--space-1);
    padding: var(--space-1);
  }

  .nav-item {
    padding: var(--space-2) var(--space-3);
    min-width: 70px;
  }

  .nav-text {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 var(--space-3);
  }

  .logo-text {
    font-size: var(--text-lg);
  }

  .version-badge {
    display: none;
  }

  .header-actions {
    gap: var(--space-2);
  }

  .action-item {
    width: 36px;
    height: 36px;
  }

  .user-menu .user-name {
    display: none;
  }

  .decoration-particles {
    display: none;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 0 var(--space-2);
  }

  .main-nav {
    flex: 1;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .nav-items {
    gap: var(--space-1);
  }

  .nav-item {
    padding: var(--space-2);
    min-width: 60px;
  }
}

// 无障碍
@media (prefers-reduced-motion: reduce) {
  .nav-item,
  .action-item,
  .particle,
  .decoration-gradient {
    animation: none;
    transition: none;
  }

  .nav-item:hover,
  .action-item:hover {
    transform: none;
  }

  .action-item:hover .action-icon {
    animation: none;
  }
}

// 高对比度模式
@media (prefers-contrast: high) {
  .app-header {
    background: var(--surface-primary);
    border-bottom: 2px solid var(--border-heavy);
  }

  .nav-item {
    border: 1px solid var(--border-medium);

    &:hover {
      border-color: var(--accent-cyan);
    }
  }

  .action-item {
    border: 1px solid var(--border-medium);
  }
}
</style>