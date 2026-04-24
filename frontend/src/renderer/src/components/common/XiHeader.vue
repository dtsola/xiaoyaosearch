<template>
  <header class="xi-header">
    <!-- Logo区域 -->
    <div class="logo-section">
      <span class="logo-icon">◤</span>
      <span class="logo-text">小遥搜索</span>
      <span class="logo-version">v2.0</span>
    </div>

    <!-- 导航链接 -->
    <nav class="nav-links">
      <router-link to="/" class="nav-link">
        <XiIcon icon="lucide:home" :size="18" />
        <span>首页</span>
      </router-link>
      <router-link to="/settings" class="nav-link">
        <XiIcon icon="lucide:settings" :size="18" />
        <span>设置</span>
      </router-link>
      <router-link to="/index" class="nav-link">
        <XiIcon icon="lucide:list" :size="18" />
        <span>索引</span>
      </router-link>
      <router-link to="/glossary/collections" class="nav-link">
        <XiIcon icon="lucide:book" :size="18" />
        <span>术语库</span>
      </router-link>
      <router-link to="/help" class="nav-link">
        <XiIcon icon="lucide:help-circle" :size="18" />
        <span>帮助</span>
      </router-link>
    </nav>

    <!-- 右侧操作 -->
    <div class="header-actions">
      <!-- 语言切换 -->
      <a-dropdown>
        <a-button type="text" class="action-btn">
          <XiIcon icon="lucide:globe" :size="16" />
          <span class="btn-text">{{ locale === 'zh-CN' ? '中文' : 'English' }}</span>
        </a-button>
        <template #overlay>
          <a-menu @click="({ key }) => handleLanguageChange(key)">
            <a-menu-item key="zh-CN">
              <span>中文</span>
            </a-menu-item>
            <a-menu-item key="en-US">
              <span>English</span>
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>

      <!-- 关于作者 -->
      <a-button type="text" class="action-btn" @click="goToAbout">
        <XiIcon icon="lucide:info" :size="16" />
        <span class="btn-text">{{ t('user.aboutAuthor') }}</span>
      </a-button>

      <!-- 用户信息 -->
      <a-button type="text" class="action-btn user-btn">
        <XiIcon icon="lucide:user" :size="16" />
        <span class="user-name">{{ t('user.name') }}</span>
      </a-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import XiIcon from './XiIcon.vue'

const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()

/**
 * 检查路由是否激活
 */
const isActive = (path: string): boolean => {
  const currentPath = route.path || '/'
  // glossary 路由需要特殊处理（包含 /glossary 的所有路径）
  if (path === '/glossary/collections') {
    return currentPath.startsWith('/glossary')
  }
  return currentPath === path
}

/**
 * 语言切换处理
 */
const handleLanguageChange = (lang: string) => {
  locale.value = lang
  message.success(t('common.languageChanged'))
}

/**
 * 跳转到关于作者页面
 */
const goToAbout = () => {
  router.push('/about')
}
</script>

<style scoped>
.xi-header {
  height: 56px;
  background: var(--bg-primary);
  border-bottom: var(--border-standard);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.logo-icon {
  font-size: 24px;
  color: var(--brand-blue);
}

.logo-text {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.25px;
  color: var(--text-primary);
}

.logo-version {
  font-size: 12px;
  color: var(--text-tertiary);
}

.nav-links {
  display: flex;
  gap: var(--space-2xl);
}

.nav-link {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  text-decoration: none;
  padding: var(--space-sm) 0;
  position: relative;
  transition: color var(--transition-base);
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-link:hover,
.nav-link.active {
  color: var(--brand-blue);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--brand-blue);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

.action-btn {
  color: var(--text-secondary);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn:hover {
  color: var(--brand-blue);
}

.user-btn {
  color: var(--text-primary);
}

.btn-text {
  margin-left: 4px;
}

.user-name {
  margin-left: 4px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
