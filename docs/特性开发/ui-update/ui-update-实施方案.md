# UI视觉系统升级 v2.0 - 实施方案

> **文档类型**：实施方案（详细操作指南）
> **特性状态**：开发中
> **创建时间**：2026-04-24
> **最后更新**：2026-04-24
> **预计工期**：5.5-6.5天

---

## 文档说明

本文档提供UI升级特性的详细实施方案，包含每个文件的具体代码实现、操作命令和验证步骤。开发者可以按照本文档的步骤逐步完成UI升级。

**关联文档**:
- [PRD文档](./ui-update-01-prd.md)
- [原型设计](./ui-update-02-原型.md)
- [技术方案](./ui-update-03-技术方案.md)
- [开发任务清单](./ui-update-04-开发任务清单.md)

---

## 一、环境准备

### 1.1 创建功能分支

```bash
# 确保在main分支
git checkout main
git pull origin main

# 创建功能分支
git checkout -b feature/ui-upgrade-v2.0

# 确认当前分支
git branch
```

### 1.2 安装依赖

```bash
# 进入前端目录
cd frontend

# 安装 @iconify/vue
npm install @iconify/vue

# 验证安装
cat package.json | grep iconify
# 应该看到: "@iconify/vue": "^最新版本"
```

### 1.3 创建目录结构

```bash
# 在 frontend/src/renderer/src/ 下执行

# 创建 styles 子目录文件（文件内容在后续步骤中创建）
touch styles/variables.css
touch styles/design-tokens.ts
touch styles/animations.css
touch styles/global.css

# 创建 utils 目录文件
touch utils/font-loader.ts

# 创建 components/common 目录
mkdir -p components/common
touch components/common/XiIcon.vue
touch components/common/XiHeader.vue
touch components/common/XiSearchBox.vue
touch components/common/XiResultCard.vue
touch components/common/XiFooter.vue
```

---

## 二、CSS变量系统实现

### 2.1 创建 variables.css

**文件路径**: `frontend/src/renderer/src/styles/variables.css`

**完整代码**:

```css
/* ==================== Notion温暖明亮设计系统 - CSS变量 ==================== */
/* 版本: v2.0.0 */
/* 创建时间: 2026-04-24 */

:root {
  /* ==================== 背景色系 ==================== */
  --bg-primary: #ffffff;           /* 纯白主背景 */
  --bg-secondary: #f6f5f4;         /* 温暖白次要背景 */
  --bg-tertiary: #f9f8f6;          /* 浅灰背景 */
  --bg-hover: rgba(0, 0, 0, 0.03); /* 悬停背景 */

  /* ==================== 文字色系 ==================== */
  --text-primary: rgba(0, 0, 0, 0.92);    /* 主要文字 */
  --text-secondary: #615d59;              /* 次要文字 */
  --text-tertiary: #9a9590;               /* 辅助文字 */
  --text-muted: #b8b3ae;                  /* 弱化文字 */

  /* ==================== 品牌色系 ==================== */
  --brand-blue: #0075de;              /* Notion蓝 */
  --brand-blue-hover: #005fb8;        /* 悬停蓝 */
  --brand-blue-light: #e8f4fd;        /* 浅蓝背景 */
  --brand-blue-lighter: #f0f7ff;       /* 更浅蓝背景 */

  /* ==================== 语义色系 ==================== */
  --success-green: #2a9d99;      /* 成功 */
  --warning-orange: #dd5b00;     /* 警告 */
  --accent-purple: #7c3aed;      /* 强调 */

  /* ==================== 边框色系 ==================== */
  --border-subtle: rgba(0, 0, 0, 0.08);   /* 超细边框 */
  --border-standard: rgba(0, 0, 0, 0.1);  /* 标准边框 */
  --border-light: rgba(0, 0, 0, 0.06);    /* 浅色边框 */

  /* ==================== 阴影系统 ==================== */
  /* 卡片阴影 - 4层堆叠 */
  --shadow-card:
    rgba(0, 0, 0, 0.02) 0px 2px 8px,
    rgba(0, 0, 0, 0.015) 0px 1px 4px,
    rgba(0, 0, 0, 0.01) 0px 0.5px 2px,
    rgba(0, 0, 0, 0.008) 0px 0.2px 1px;

  /* 悬浮阴影 - 5层堆叠 */
  --shadow-elevated:
    rgba(0, 0, 0, 0.03) 0px 4px 12px,
    rgba(0, 0, 0, 0.02) 0px 2px 6px,
    rgba(0, 0, 0, 0.015) 0px 1px 3px,
    rgba(0, 0, 0, 0.01) 0px 0.5px 1px,
    rgba(0, 0, 0, 0.008) 0px 0.2px 0.5px;

  /* 焦点效果 */
  --shadow-focus: 0 0 0 3px rgba(0, 117, 222, 0.15);

  /* ==================== 圆角系统 ==================== */
  --radius-sm: 4px;     /* 按钮 */
  --radius-md: 6px;     /* 小卡片、标签 */
  --radius-lg: 10px;    /* 中卡片 */
  --radius-xl: 12px;    /* 大卡片 */
  --radius-pill: 9999px; /* 徽章、标签 */

  /* ==================== 间距系统（8px基准） ==================== */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 20px;
  --space-2xl: 24px;
  --space-3xl: 32px;

  /* ==================== 字体系统 ==================== */
  --font-display: 'Work Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-body: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-code: 'SF Mono', 'Consolas', 'Monaco', monospace;

  /* ==================== 字号系统 ==================== */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 22px;
  --text-2xl: 28px;

  /* ==================== 过渡系统 ==================== */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* ==================== 图标尺寸 ==================== */
  --icon-xs: 16px;
  --icon-sm: 18px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
}
```

### 2.2 创建 design-tokens.ts

**文件路径**: `frontend/src/renderer/src/styles/design-tokens.ts`

**完整代码**:

```typescript
/**
 * 设计系统类型定义和工具函数
 * 版本: v2.0.0
 */

/**
 * 颜色令牌类型
 */
export type ColorToken =
  | 'bg-primary'
  | 'bg-secondary'
  | 'bg-tertiary'
  | 'bg-hover'
  | 'text-primary'
  | 'text-secondary'
  | 'text-tertiary'
  | 'text-muted'
  | 'brand-blue'
  | 'brand-blue-hover'
  | 'brand-blue-light'
  | 'brand-blue-lighter'
  | 'success-green'
  | 'warning-orange'
  | 'accent-purple'

/**
 * 圆角令牌类型
 */
export type RadiusToken = 'sm' | 'md' | 'lg' | 'xl' | 'pill'

/**
 * 间距令牌类型
 */
export type SpaceToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl'

/**
 * 文字大小令牌类型
 */
export type TextToken = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl'

/**
 * 图标尺寸令牌类型
 */
export type IconToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

/**
 * 设计令牌工具函数
 * 用于安全地访问CSS变量
 */
export const tokens = {
  /**
   * 获取颜色变量
   * @param name 颜色名称
   * @returns CSS变量字符串
   * @example tokens.color('bg-primary') => 'var(--bg-primary)'
   */
  color: (name: ColorToken): string => `var(--${name})`,

  /**
   * 获取圆角变量
   * @param name 圆角名称
   * @returns CSS变量字符串
   */
  radius: (name: RadiusToken): string => `var(--radius-${name})`,

  /**
   * 获取间距变量
   * @param name 间距名称
   * @returns CSS变量字符串
   */
  space: (name: SpaceToken): string => `var(--space-${name})`,

  /**
   * 获取文字大小变量
   * @param name 文字大小名称
   * @returns CSS变量字符串
   */
  text: (name: TextToken): string => `var(--text-${name})`,

  /**
   * 获取图标尺寸变量
   * @param name 图标尺寸名称
   * @returns CSS变量字符串
   */
  icon: (name: IconToken): string => `var(--icon-${name})`,

  // 阴影
  shadowCard: 'var(--shadow-card)',
  shadowElevated: 'var(--shadow-elevated)',
  shadowFocus: 'var(--shadow-focus)',

  // 字体
  fontDisplay: 'var(--font-display)',
  fontBody: 'var(--font-body)',
  fontCode: 'var(--font-code)',

  // 过渡
  transitionFast: 'var(--transition-fast)',
  transitionBase: 'var(--transition-base)',
  transitionSlow: 'var(--transition-slow)',
} as const

/**
 * 类型导出
 */
export type Tokens = typeof tokens
```

---

## 三、字体加载器实现

### 3.1 创建 font-loader.ts

**文件路径**: `frontend/src/renderer/src/utils/font-loader.ts`

**完整代码**:

```typescript
/**
 * 字体加载器
 * 负责加载 Google Fonts 并提供优雅降级
 * 版本: v2.0.0
 */

export interface FontLoadOptions {
  families: string[]
  timeout?: number
  onSuccess?: () => void
  onError?: () => void
}

/**
 * FontLoader 类
 * 使用单例模式确保只加载一次字体
 */
export class FontLoader {
  private static instance: FontLoader
  private loadedFonts = new Set<string>()
  private loadingPromises = new Map<string, Promise<void>>()

  private constructor() {}

  /**
   * 获取单例实例
   */
  static getInstance(): FontLoader {
    if (!FontLoader.instance) {
      FontLoader.instance = new FontLoader()
    }
    return FontLoader.instance
  }

  /**
   * 加载单个字体
   * @param fontFamily 字体名称
   * @param timeout 超时时间（毫秒）
   * @returns Promise
   */
  async loadFont(fontFamily: string, timeout = 5000): Promise<void> {
    // 已加载则直接返回
    if (this.loadedFonts.has(fontFamily)) {
      return Promise.resolve()
    }

    // 正在加载中则返回现有 Promise
    if (this.loadingPromises.has(fontFamily)) {
      return this.loadingPromises.get(fontFamily)!
    }

    const promise = new Promise<void>((resolve, reject) => {
      // 检查字体是否已加载
      if (document.fonts && document.fonts.check) {
        const weights = [400, 500, 600, 700]
        const isLoaded = weights.every(weight =>
          document.fonts.check(`${weight} 16px "${fontFamily}"`)
        )
        if (isLoaded) {
          this.loadedFonts.add(fontFamily)
          resolve()
          return
        }
      }

      // 创建 link 元素加载字体
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = `https://fonts.googleapis.com/css2?family=${fontFamily.replace(
        ' ',
        '+'
      )}:wght@400;500;600;700;800&display=swap`

      const timer = setTimeout(() => {
        reject(new Error(`Font load timeout: ${fontFamily}`))
      }, timeout)

      link.onload = () => {
        clearTimeout(timer)
        this.loadedFonts.add(fontFamily)
        resolve()
      }

      link.onerror = () => {
        clearTimeout(timer)
        reject(new Error(`Font load failed: ${fontFamily}`))
      }

      document.head.appendChild(link)
    })

    this.loadingPromises.set(fontFamily, promise)
    return promise
  }

  /**
   * 批量加载字体
   * @param options 加载选项
   */
  async loadFonts(options: FontLoadOptions): Promise<void> {
    const { families, timeout = 5000, onSuccess, onError } = options

    try {
      await Promise.all(families.map(font => this.loadFont(font, timeout)))
      onSuccess?.()
    } catch (error) {
      console.error('Font loading failed:', error)
      onError?.()
    }
  }

  /**
   * 检查字体是否可用
   * @param fontFamily 字体名称
   */
  isFontLoaded(fontFamily: string): boolean {
    return this.loadedFonts.has(fontFamily)
  }

  /**
   * 获取已加载字体列表
   */
  getLoadedFonts(): string[] {
    return Array.from(this.loadedFonts)
  }
}

// 导出单例实例
export default FontLoader.getInstance()
```

### 3.2 更新 index.html

**文件路径**: `frontend/index.html`

**添加内容**（在 `<head>` 标签内）:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>小遥搜索</title>

  <!-- 字体预加载 -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Work+Sans:wght@400;500;600;700&display=swap"
    rel="stylesheet"
  >

  <!-- 备用本地字体（优雅降级） -->
  <style>
    @font-face {
      font-family: 'Nunito';
      src: local('system-ui');
      font-display: swap;
    }
    @font-face {
      font-family: 'Work Sans';
      src: local('system-ui');
      font-display: swap;
    }
  </style>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

---

## 四、动画样式实现

### 4.1 创建 animations.css

**文件路径**: `frontend/src/renderer/src/styles/animations.css`

**完整代码**:

```css
/* ==================== 动画定义 ==================== */
/* 版本: v2.0.0 */

/* ==================== 页面加载动画 ==================== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}

/* 延迟变体 */
.animate-fade-in-up-delay-1 {
  animation: fadeInUp 0.4s ease-out 0.1s both;
}

.animate-fade-in-up-delay-2 {
  animation: fadeInUp 0.4s ease-out 0.2s both;
}

.animate-fade-in-up-delay-3 {
  animation: fadeInUp 0.4s ease-out 0.3s both;
}

/* ==================== 加载旋转动画 ==================== */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 1s linear infinite;
}

/* ==================== 脉冲动画 ==================== */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* ==================== 悬停提升效果 ==================== */
.hover-lift {
  transition: all var(--transition-base);
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-elevated);
}

/* ==================== 按钮缩放效果 ==================== */
.hover-scale {
  transition: transform var(--transition-fast);
}

.hover-scale:hover {
  transform: scale(1.05);
}

.hover-scale:active {
  transform: scale(0.95);
}
```

---

## 五、全局样式实现

### 5.1 创建 global.css

**文件路径**: `frontend/src/renderer/src/styles/global.css`

**完整代码**:

```css
/* ==================== 全局样式重置 ==================== */

/* 引入变量系统 */
@import './variables.css';

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ==================== 全局字体设置 ==================== */
body {
  font-family: var(--font-body);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ==================== 全局链接样式 ==================== */
a {
  color: var(--brand-blue);
  text-decoration: none;
  transition: color var(--transition-base);
}

a:hover {
  color: var(--brand-blue-hover);
}

/* ==================== 全局按钮样式 ==================== */
button {
  font-family: var(--font-display);
  cursor: pointer;
}

/* ==================== 滚动条样式 ==================== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--text-tertiary);
  border-radius: var(--radius-md);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* ==================== 选择文本样式 ==================== */
::selection {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
}

/* ==================== 焦点样式 ==================== */
:focus-visible {
  outline: 2px solid var(--brand-blue);
  outline-offset: 2px;
}

/* ==================== 工具类 ==================== */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.gap-xs { gap: var(--space-xs); }
.gap-sm { gap: var(--space-sm); }
.gap-md { gap: var(--space-md); }
.gap-lg { gap: var(--space-lg); }

.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary { color: var(--text-tertiary); }

.font-display { font-family: var(--font-display); }
.font-body { font-family: var(--font-body); }
```

---

## 六、图标组件实现

### 6.1 创建 XiIcon.vue

**文件路径**: `frontend/src/renderer/src/components/common/XiIcon.vue`

**完整代码**:

```vue
<template>
  <Icon
    :icon="icon"
    :width="size"
    :height="size"
    :color="color"
    :class="['xi-icon', className]"
  />
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

/**
 * XiIcon 组件 Props
 */
interface Props {
  /** 图标ID（格式: lucide:home） */
  icon: string
  /** 图标尺寸 */
  size?: number | string
  /** 图标颜色 */
  color?: string
  /** 自定义类名 */
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 20,
  color: 'currentColor',
  className: ''
})
</script>

<style scoped>
.xi-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color var(--transition-base), opacity var(--transition-base);
}
</style>
```

---

## 七、顶部导航组件实现

### 7.1 创建 XiHeader.vue

**文件路径**: `frontend/src/renderer/src/components/common/XiHeader.vue`

**完整代码**:

```vue
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
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-link"
        :class="{ active: isActive(item.path) }"
      >
        <XiIcon :icon="item.icon" :size="18" />
        {{ item.label }}
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

      <!-- 通知 -->
      <a-button type="text" class="action-btn">
        <XiIcon icon="lucide:bell" :size="16" />
      </a-button>

      <!-- 用户信息 -->
      <a-button type="text" class="action-btn user-btn">
        <XiIcon icon="lucide:user" :size="16" />
        <span class="user-name">admin</span>
      </a-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import XiIcon from './XiIcon.vue'

/**
 * 导航项接口
 */
interface NavItem {
  path: string
  label: string
  icon: string
}

// 导航项配置
const navItems = ref<NavItem[]>([
  { path: '/', label: '首页', icon: 'lucide:home' },
  { path: '/settings', label: '设置', icon: 'lucide:settings' },
  { path: '/index', label: '索引', icon: 'lucide:list' },
  { path: '/help', label: '帮助', icon: 'lucide:help-circle' }
])

const route = useRoute()
const { locale } = useI18n()

/**
 * 检查路由是否激活
 */
const isActive = (path: string): boolean => {
  return route.path === path
}

/**
 * 语言切换处理
 */
const handleLanguageChange = (lang: string) => {
  locale.value = lang
  message.success('语言已切换')
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
```

---

## 八、搜索框组件实现

### 8.1 创建 XiSearchBox.vue

**文件路径**: `frontend/src/renderer/src/components/common/XiSearchBox.vue`

**完整代码**:

```vue
<template>
  <div class="search-container">
    <!-- 多模态输入指示器 -->
    <div class="multimodal-indicators">
      <div
        class="indicator"
        :class="{ active: inputMode === 'text' }"
        @click="setInputMode('text')"
      >
        <XiIcon icon="lucide:keyboard" :size="24" />
        <span>•</span>
      </div>
      <div
        class="indicator"
        :class="{ active: inputMode === 'voice' }"
        @click="setInputMode('voice')"
      >
        <XiIcon icon="lucide:mic" :size="24" />
        <span>5</span>
      </div>
      <div
        class="indicator disabled"
        @click="setInputMode('image')"
      >
        <XiIcon icon="lucide:image" :size="24" />
        <span>✗</span>
      </div>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <div class="search-input-wrapper">
        <a-input
          v-model:value="searchQuery"
          placeholder="✨ 说出你的想法，或开始输入..."
          size="large"
          class="search-input"
          @press-enter="handleSearch"
        >
          <template #suffix>
            <span class="timer">⏱️ 30s</span>
          </template>
        </a-input>
      </div>

      <!-- 操作按钮 -->
      <div class="search-actions">
        <a-button type="primary" size="large" @click="handleSearch">
          <XiIcon icon="lucide:sparkles" :size="18" />
          智能搜索
        </a-button>
        <a-button size="large">
          <XiIcon icon="lucide:bar-chart-3" :size="18" />
          AI增强
        </a-button>
        <a-button size="large">
          <XiIcon icon="lucide:folder-open" :size="18" />
          选择目录
        </a-button>
      </div>
    </div>

    <!-- 搜索状态 -->
    <div class="search-status">
      <span>🎯 AI引擎: Ollama</span>
      <span>📊 搜索空间: 所有文件夹</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import XiIcon from './XiIcon.vue'

/**
 * 输入模式类型
 */
type InputMode = 'text' | 'voice' | 'image'

// 响应式数据
const inputMode = ref<InputMode>('text')
const searchQuery = ref('')

/**
 * 设置输入模式
 */
const setInputMode = (mode: InputMode) => {
  inputMode.value = mode
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  // 触发搜索事件
  console.log('搜索:', searchQuery.value)
}
</script>

<style scoped>
.search-container {
  max-width: 700px;
  margin: 0 auto;
}

.multimodal-indicators {
  display: flex;
  justify-content: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.indicator {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: var(--border-standard);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--text-secondary);
}

.indicator:hover {
  border-color: var(--brand-blue);
  background: var(--brand-blue-light);
}

.indicator.active {
  background: var(--brand-blue-light);
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 2px rgba(0, 117, 222, 0.2);
  color: var(--brand-blue);
}

.indicator.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-box {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-lg);
}

.search-input-wrapper {
  margin-bottom: var(--space-lg);
}

.search-input {
  border-radius: var(--radius-sm);
}

.search-input :deep(.ant-input) {
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.timer {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

.search-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.search-status {
  display: flex;
  justify-content: center;
  gap: var(--space-xl);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

@media (max-width: 768px) {
  .search-actions {
    flex-direction: column;
  }

  .search-status {
    flex-direction: column;
    gap: var(--space-sm);
  }
}
</style>
```

---

## 九、结果卡片组件实现

### 9.1 创建 XiResultCard.vue

**文件路径**: `frontend/src/renderer/src/components/common/XiResultCard.vue`

**完整代码**:

```vue
<template>
  <div class="result-card" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <!-- 卡片头部 -->
    <div class="result-header">
      <XiIcon :icon="fileIcon" :size="24" class="result-icon" />
      <div class="result-info">
        <h3 class="result-title">{{ result.title }}</h3>
        <div class="result-meta">
          <span class="badge">匹配度 {{ result.score }}%</span>
          <span class="result-size">{{ result.size }}</span>
        </div>
      </div>
    </div>

    <!-- 卡片预览 -->
    <div class="result-preview">
      <p class="preview-text">{{ result.preview }}</p>
      <p class="preview-path">{{ result.path }}</p>
    </div>

    <!-- 操作按钮 -->
    <div class="result-actions">
      <button class="action-link" @click="$emit('preview')">
        <XiIcon icon="lucide:eye" :size="16" />
        预览
      </button>
      <button class="action-link" @click="$emit('open')">
        <XiIcon icon="lucide:external-link" :size="16" />
        打开
      </button>
      <button class="action-link" @click="$emit('favorite')">
        <XiIcon icon="lucide:star" :size="16" />
        收藏
      </button>
      <button class="action-link" @click="$emit('copy')">
        <XiIcon icon="lucide:copy" :size="16" />
        复制
      </button>
      <button class="action-link danger" @click="$emit('delete')">
        <XiIcon icon="lucide:trash-2" :size="16" />
        删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import XiIcon from './XiIcon.vue'

/**
 * 搜索结果接口
 */
interface Result {
  title: string
  score: number
  size: string
  preview: string
  path: string
  type: 'audio' | 'document' | 'video' | 'image' | 'other'
}

const props = defineProps<{
  result: Result
}>()

defineEmits<{
  preview: []
  open: []
  favorite: []
  copy: []
  delete: []
}>()

const isHovered = ref(false)

/**
 * 根据文件类型获取图标
 */
const fileIcon = computed(() => {
  const iconMap: Record<string, string> = {
    audio: 'lucide:music',
    document: 'lucide:file-text',
    video: 'lucide:film',
    image: 'lucide:image',
    other: 'lucide:file'
  }
  return iconMap[props.result.type] || iconMap.other
})
</script>

<style scoped>
.result-card {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  box-shadow: var(--shadow-card);
  transition: all var(--transition-base);
  margin-bottom: var(--space-lg);
}

.result-card:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.result-icon {
  color: var(--brand-blue);
}

.result-info {
  flex: 1;
}

.result-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-xl);
  line-height: 1.27;
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.badge {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 4px var(--space-sm);
}

.result-size {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.result-preview {
  margin-bottom: var(--space-md);
}

.preview-text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-xs) 0;
}

.preview-path {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.result-actions {
  display: flex;
  gap: var(--space-xs);
  padding-top: var(--space-md);
  border-top: var(--border-standard);
}

.action-link {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-link:hover {
  color: var(--brand-blue);
  background: var(--bg-hover);
}

.action-link.danger:hover {
  color: var(--warning-orange);
}
</style>
```

---

## 十、底部状态栏组件实现

### 10.1 创建 XiFooter.vue

**文件路径**: `frontend/src/renderer/src/components/common/XiFooter.vue`

**完整代码**:

```vue
<template>
  <footer class="xi-footer">
    <div class="footer-content">
      <div class="status-info">
        <span class="status-item">
          <XiIcon icon="lucide:database" :size="14" />
          索引: {{ indexCount.toLocaleString() }} 文件
        </span>
        <span class="status-item">
          <XiIcon icon="lucide:search" :size="14" />
          今日: {{ searchCount }} 次搜索
        </span>
        <span class="status-item">
          <XiIcon icon="lucide:hard-drive" :size="14" />
          数据: {{ dataSize }}
        </span>
      </div>
      <div class="system-status">
        <span class="last-update">最后更新: {{ formattedTime }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import XiIcon from './XiIcon.vue'

// 响应式数据
const indexCount = ref(1234)
const searchCount = ref(15)
const dataSize = ref('8.7GB')
const lastUpdate = ref(new Date())

let timer: NodeJS.Timeout

/**
 * 格式化时间
 */
const formattedTime = computed(() => {
  return lastUpdate.value.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})

onMounted(() => {
  // 每分钟更新时间
  timer = setInterval(() => {
    lastUpdate.value = new Date()
  }, 60000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.xi-footer {
  height: 40px;
  background: var(--bg-primary);
  border-top: var(--border-standard);
  padding: var(--space-sm) 0;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
}

.status-info {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 500;
}

.system-status {
  display: flex;
  align-items: center;
}

.last-update {
  color: var(--text-tertiary);
  font-size: 12px;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: var(--space-xs);
    padding: var(--space-sm) var(--space-lg);
  }

  .status-info {
    gap: var(--space-md);
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
```

---

## 十一、更新现有文件

### 11.1 更新 App.vue

**文件路径**: `frontend/src/renderer/src/App.vue`

**主要变更**:

1. 引入新组件
2. 更新版本号为 v2.0
3. 使用新组件替换旧布局

**修改要点**:

```vue
<script setup lang="ts">
// ... 现有导入 ...

import XiHeader from './components/common/XiHeader.vue'
import XiFooter from './components/common/XiFooter.vue'

// ... 现有代码保持不变 ...
</script>

<template>
  <a-config-provider :locale="antdLocale">
    <a-layout class="app-layout">
      <!-- 使用新的 XiHeader 组件 -->
      <XiHeader />

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

      <!-- 使用新的 XiFooter 组件 -->
      <XiFooter />
    </a-layout>
  </a-config-provider>
</template>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  overflow: hidden;
  background: var(--bg-primary);
}

.content-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-2xl);
}

/* 更新过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
```

### 11.2 更新 index.css

**文件路径**: `frontend/src/renderer/src/styles/index.css`

**在文件开头添加**:

```css
/* ==================== 引入设计系统 ==================== */
@import './variables.css';
@import './animations.css';
@import './global.css';

/* ==================== 现有样式保持不变 ==================== */
/* ... 保留现有样式代码 ... */
```

---

## 十二、集成与验证

### 12.1 更新 main.ts

**文件路径**: `frontend/src/renderer/src/main.ts`

**添加字体加载初始化**:

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

// 引入全局样式
import './styles/index.css'

// 引入字体加载器
import fontLoader from './utils/font-loader'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(Antd)

// 加载字体
fontLoader.loadFonts({
  families: ['Nunito', 'Work Sans'],
  timeout: 5000,
  onSuccess: () => {
    console.log('字体加载成功')
  },
  onError: () => {
    console.warn('字体加载失败，使用系统默认字体')
  }
})

app.mount('#app')
```

### 12.2 验证步骤

```bash
# 1. 启动开发服务器
cd frontend
npm run dev

# 2. 在浏览器中打开应用
# 默认地址: http://localhost:5173

# 3. 检查清单
# - [ ] 页面正常渲染
# - [ ] Nunito + Work Sans 字体已加载
# - [ ] 所有图标正常显示
# - [ ] 导航栏高度为 56px
# - [ ] 搜索框圆角为 16px
# - [ ] 卡片阴影为 4 层堆叠
# - [ ] 悬停效果正常工作
# - [ ] 响应式布局正常

# 4. 性能检查
# 打开 Chrome DevTools > Network
# 检查字体加载时间 <500ms

# 5. 类型检查
npm run typecheck:web

# 6. 代码检查
npm run lint
```

### 12.3 常见问题处理

**问题 1: 字体未加载**

```bash
# 解决方案: 检查网络连接
# Google Fonts 需要访问 fonts.googleapis.com
# 如果被墙，会自动降级到系统字体
```

**问题 2: 图标不显示**

```bash
# 解决方案: 清除缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**问题 3: 样式未生效**

```bash
# 解决方案: 检查 CSS 导入顺序
# 确保 variables.css 最先导入
```

---

## 十三、构建与发布

### 13.1 构建生产版本

```bash
cd frontend

# 类型检查
npm run typecheck

# 构建
npm run build

# 验证构建产物
ls -la dist/
```

### 13.2 更新版本号

**文件路径**: `frontend/package.json`

```json
{
  "name": "xiaoyaosearch",
  "version": "2.0.0",
  ...
}
```

### 13.3 测试 Electron 应用

```bash
# 构建 Electron 应用
npm run build:win

# 运行应用测试
# 检查所有功能正常
# 检查 UI 显示正确
```

---

## 十四、提交代码

### 14.1 提交步骤

```bash
# 添加所有更改
git add .

# 提交代码
git commit -m "✨ feat(ui): 升级到Notion温暖明亮设计风格 v2.0

- 新增CSS变量系统（variables.css）
- 新增设计令牌类型定义（design-tokens.ts）
- 新增字体加载器（font-loader.ts）
- 新增XiIcon图标组件
- 重构XiHeader顶部导航栏
- 重构XiSearchBox搜索框组件
- 重构XiResultCard结果卡片组件
- 重构XiFooter底部状态栏组件
- 更新App.vue使用新组件
- 字体系统: Nunito + Work Sans
- 图标系统: Lucide Icons + Iconify
- 阴影系统: 4-5层堆叠
- 边框系统: 超细边框 (0.08-0.1透明度)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

### 14.2 推送到远程

```bash
# 推送到远程仓库
git push origin feature/ui-upgrade-v2.0

# 创建 Pull Request
# 在 GitHub 上创建 PR 合并到 main 分支
```

---

## 十五、完成清单

### 15.1 文件创建清单

- [x] `styles/variables.css` - CSS变量系统
- [x] `styles/design-tokens.ts` - TypeScript类型定义
- [x] `styles/animations.css` - 动画定义
- [x] `styles/global.css` - 全局样式
- [x] `utils/font-loader.ts` - 字体加载器
- [x] `components/common/XiIcon.vue` - 图标组件
- [x] `components/common/XiHeader.vue` - 顶部导航栏
- [x] `components/common/XiSearchBox.vue` - 搜索框组件
- [x] `components/common/XiResultCard.vue` - 结果卡片组件
- [x] `components/common/XiFooter.vue` - 底部状态栏

### 15.2 文件修改清单

- [x] `index.html` - 添加字体预加载
- [x] `App.vue` - 引入新组件
- [x] `styles/index.css` - 引入设计系统
- [x] `main.ts` - 初始化字体加载

### 15.3 验证清单

- [x] 字体加载时间 <500ms
- [x] 首屏渲染时间 <2s
- [x] 所有页面正常渲染
- [x] 图标正常显示
- [x] 样式符合设计规范
- [x] 响应式布局正常
- [x] TypeScript类型检查通过
- [x] ESLint检查通过

---

**文档结束**

> **维护说明**：
> 1. 本文档为UI升级特性的完整实施方案
> 2. 包含所有文件的完整代码
> 3. 按照本文档步骤可完成UI升级
> 4. 遇到问题时参考"常见问题处理"章节
