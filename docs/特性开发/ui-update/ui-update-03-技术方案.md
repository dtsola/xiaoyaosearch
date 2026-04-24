# UI视觉系统升级 v2.0 - 技术方案

> **文档类型**：技术方案设计文档
> **特性名称**：UI视觉系统升级
> **设计状态**：开发中
> **创建时间**：2026-04-24
> **最后更新**：2026-04-24
> **关联文档**：[UI升级PRD](./ui-update-01-prd.md) | [UI升级原型](./ui-update-02-原型.md) | [图标系统](./ui-update-图标系统.md)

---

## 1. 技术概述

### 1.1 技术目标

为小遥搜索v2.0里程碑版本实现全面的UI视觉系统升级，采用Notion温暖明亮设计风格，建立完整的设计系统规范，提升产品品质和用户体验。

### 1.2 技术范围

- **前端**：Vue 3 + TypeScript + Ant Design Vue样式覆盖
- **设计系统**：CSS Variables + Design Tokens
- **字体系统**：Google Fonts（Nunito + Work Sans）
- **图标系统**：Lucide Icons + Iconify集成
- **动画系统**：CSS3 Animations + Transitions
- **响应式**：断点系统 + 移动端适配

### 1.3 技术约束

- **纯前端升级**：不涉及后端API变更
- **向后兼容**：不破坏现有功能逻辑
- **性能优先**：字体加载<500ms，首屏渲染<2s
- **渐进增强**：支持字体加载失败时的优雅降级

---

## 2. 技术选型

### 2.1 核心技术栈

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| **Vue 3** | 前端框架 | 项目已使用，保持技术栈一致 | - |
| **TypeScript** | 类型安全 | 项目已使用 | - |
| **Ant Design Vue** | UI组件库 | 项目已使用，覆盖基础组件 | - |
| **CSS Variables** | 设计系统实现 | 原生支持，易于维护，运行时可动态修改 | CSS-in-JS |
| **Google Fonts** | 字体托管 | 免费且稳定，CDN加速，全球节点 | 本地字体文件 |
| **Iconify** | 图标系统 | 支持100+图标库，按需加载 | 本地SVG文件 |
| **PostCSS** | CSS处理 | 项目已配置，支持现代CSS特性 | Sass/Less |

### 2.2 字体系统选型

| 字体 | 用途 | 字重 | 文件大小 | 选择理由 |
|-----|------|------|---------|---------|
| **Nunito** | 正文 | 400-800 | ~50KB | 圆润友好，高可读性，适合长时间阅读 |
| **Work Sans** | 标题 | 400-700 | ~40KB | 现代几何感，负字间距，品牌识别度高 |
| **SF Mono** | 代码 | 400 | 系统字体 | 等宽清晰，Apple系统自带 |

### 2.3 图标库选型

| 图标库 | 图标数 | 风格 | 选择理由 | 弃用方案 |
|-------|-------|------|---------|---------|
| **Lucide** | 1000+ | outline | 与Notion风格完美契合，2px stroke统一 | Feather Icons |
| Heroicons | 292 | outline | Tailwind团队制作，但数量较少 | - |
| Phosphor | 7000+ | outline/filled | 图标多，但风格稍显复杂 | - |

---

## 3. 架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            表现层 (Presentation Layer)                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   主页面      │  │   设置页面    │  │   索引页面    │  │   帮助页面  │ │
│  │  Home.vue    │  │ Settings.vue │  │  Index.vue   │  │  Help.vue  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬─────┘ │
│         │                  │                  │                  │       │
└─────────┼──────────────────┼──────────────────┼──────────────────┼───────┘
          │                  │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────────┼───────┐
│         ↓                  ↓                  ↓                  ↓       │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                        组件层 (Component Layer)                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │ XiHeader   │  │ XiSearchBox│  │ XiResultCard│  │ XiIcon    │ │  │
│  │  │ 组件        │  │ 组件        │  │ 组件         │  │ 组件       │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘ │  │
│  └────────┼───────────────┼───────────────┼───────────────┼──────────┘  │
└───────────┼───────────────┼───────────────┼───────────────┼─────────────┘
            │               │               │               │
┌───────────┼───────────────┼───────────────┼───────────────┼─────────────┐
│           ↓               ↓               ↓               ↓             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      设计系统层 (Design System Layer)               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │ CSS Variables│  │ Design Tokens│  │ Global Mixins│            │ │
│  │  │ (设计令牌)    │  │ (设计规范)    │  │ (全局样式)    │            │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│  └─────────┼──────────────────┼───────────────┼──────────────────────┘ │
└────────────┼──────────────────┼───────────────┼──────────────────────────┘
             │                  │               │
┌────────────┼──────────────────┼───────────────┼──────────────────────────┐
│            ↓                  ↓               ↓                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      资源层 (Asset Layer)                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │ Google Fonts │  │ Iconify CDN  │  │ SVG Icons    │            │ │
│  │  │ (字体文件)    │  │ (图标服务)    │  │ (备用图标)    │            │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

### 3.2 前端目录结构

```
frontend/src/renderer/src/
├── assets/                      # 静态资源
│   ├── fonts/                   # 字体文件（备用）
│   │   ├── nunito/              # Nunito字体
│   │   └── work-sans/           # Work Sans字体
│   └── icons/                   # 图标文件（备用）
│       └── lucide/              # Lucide SVG图标
├── components/                  # 组件
│   ├── common/                  # 通用组件
│   │   ├── XiHeader.vue         # 顶部导航栏
│   │   ├── XiSearchBox.vue      # 搜索框组件
│   │   ├── XiResultCard.vue     # 结果卡片组件
│   │   ├── XiFooter.vue         # 底部状态栏
│   │   └── XiIcon.vue           # 图标组件
│   └── ...
├── styles/                      # 样式文件
│   ├── design-tokens.ts         # 设计令牌
│   ├── global.css               # 全局样式
│   ├── variables.css            # CSS变量
│   ├── mixins.css               # CSS混入
│   └── animations.css           # 动画定义
├── views/                       # 页面视图
│   ├── Home.vue                 # 主页
│   ├── Settings.vue             # 设置页
│   ├── Index.vue                # 索引页
│   └── Help.vue                 # 帮助页
├── utils/                       # 工具函数
│   ├── font-loader.ts           # 字体加载器
│   ├── icon-resolver.ts         # 图标解析器
│   └── theme-detector.ts        # 主题检测器
└── App.vue                      # 根组件
```

---

## 4. 核心技术实现

### 4.1 CSS变量系统（Design Tokens）

#### 4.1.1 变量定义文件 ([styles/variables.css](../../frontend/src/renderer/src/styles/variables.css))

```css
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
  --border-light: rgba(0, 0, 0, 0.06);     /* 浅色边框 */

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
}

/* ==================== 图标尺寸 ==================== */
:root {
  --icon-xs: 16px;
  --icon-sm: 18px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
}
```

#### 4.1.2 TypeScript类型定义 ([styles/design-tokens.ts](../../frontend/src/renderer/src/styles/design-tokens.ts))

```typescript
/**
 * 设计系统类型定义
 */

export type ColorToken =
  | 'bg-primary' | 'bg-secondary' | 'bg-tertiary' | 'bg-hover'
  | 'text-primary' | 'text-secondary' | 'text-tertiary' | 'text-muted'
  | 'brand-blue' | 'brand-blue-hover' | 'brand-blue-light' | 'brand-blue-lighter'
  | 'success-green' | 'warning-orange' | 'accent-purple'

export type RadiusToken = 'sm' | 'md' | 'lg' | 'xl' | 'pill'
export type SpaceToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl'
export type TextToken = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl'
export type IconToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

/**
 * 设计令牌工具函数
 */
export const tokens = {
  color: (name: ColorToken): string => `var(--${name})`,
  radius: (name: RadiusToken): string => `var(--radius-${name})`,
  space: (name: SpaceToken): string => `var(--space-${name})`,
  text: (name: TextToken): string => `var(--text-${name})`,
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
```

### 4.2 字体加载方案

#### 4.2.1 字体加载器 ([utils/font-loader.ts](../../frontend/src/renderer/src/utils/font-loader.ts))

```typescript
/**
 * 字体加载器
 * 负责加载Google Fonts并提供优雅降级
 */

export interface FontLoadOptions {
  families: string[]
  timeout?: number
  onSuccess?: () => void
  onError?: () => void
}

export class FontLoader {
  private static instance: FontLoader
  private loadedFonts = new Set<string>()
  private loadingPromises = new Map<string, Promise<void>>()

  static getInstance(): FontLoader {
    if (!FontLoader.instance) {
      FontLoader.instance = new FontLoader()
    }
    return FontLoader.instance
  }

  /**
   * 加载字体
   */
  async loadFont(fontFamily: string, timeout = 5000): Promise<void> {
    // 已加载则直接返回
    if (this.loadedFonts.has(fontFamily)) {
      return Promise.resolve()
    }

    // 正在加载中则返回现有Promise
    if (this.loadingPromises.has(fontFamily)) {
      return this.loadingPromises.get(fontFamily)!
    }

    const promise = new Promise<void>((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = `https://fonts.googleapis.com/css2?family=${fontFamily.replace(' ', '+')}:wght@400;500;600;700;800&display=swap`

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
   */
  async loadFonts(options: FontLoadOptions): Promise<void> {
    const { families, timeout = 5000, onSuccess, onError } = options

    try {
      await Promise.all(
        families.map(font => this.loadFont(font, timeout))
      )
      onSuccess?.()
    } catch (error) {
      console.error('Font loading failed:', error)
      onError?.()
    }
  }

  /**
   * 检查字体是否可用
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

export default FontLoader.getInstance()
```

#### 4.2.2 字体预加载（index.html）

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

  <!-- 备用本地字体（可选） -->
  <style>
    /* 字体加载失败的优雅降级 */
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

### 4.3 图标集成方案

#### 4.3.1 Iconify集成

```bash
npm install @iconify/vue
```

#### 4.3.2 XiIcon组件封装 ([components/common/XiIcon.vue](../../frontend/src/renderer/src/components/common/XiIcon.vue))

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
import type { IconifyIcon } from '@iconify/vue'

interface Props {
  icon: string
  size?: number | string
  color?: string
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
}
</style>
```

#### 4.3.3 图标使用规范

```vue
<template>
  <!-- 基础用法 -->
  <XiIcon icon="lucide:home" :size="20" />

  <!-- 品牌色图标 -->
  <XiIcon icon="lucide:search" :size="24" color="#0075de" />

  <!-- 使用CSS变量 -->
  <XiIcon
    icon="lucide:star"
    :size="16"
    :color="tokens.color('text-secondary')"
  />

  <!-- 图标+文字 -->
  <button class="btn-icon">
    <XiIcon icon="lucide:star" :size="16" />
    <span>收藏</span>
  </button>
</template>

<script setup lang="ts">
import XiIcon from '@/components/common/XiIcon.vue'
import tokens from '@/styles/design-tokens'
</script>

<style scoped>
.btn-icon {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm, 6px);
  padding: var(--space-sm, 8px) var(--space-md, 12px);
}
</style>
```

### 4.4 组件样式更新

#### 4.4.1 顶部导航栏组件 ([components/common/XiHeader.vue](../../frontend/src/renderer/src/components/common/XiHeader.vue))

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
        {{ item.label }}
      </router-link>
    </nav>

    <!-- 右侧操作 -->
    <div class="header-actions">
      <a-button type="text" class="action-btn">
        <XiIcon icon="lucide:globe" :size="16" />
        <span>中文</span>
      </a-button>
      <a-button type="text" class="action-btn">
        <XiIcon icon="lucide:bell" :size="16" />
      </a-button>
      <a-button type="text" class="action-btn">
        <XiIcon icon="lucide:user" :size="16" />
        <span>admin</span>
      </a-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import XiIcon from './XiIcon.vue'

interface NavItem {
  path: string
  label: string
}

const navItems = ref<NavItem[]>([
  { path: '/', label: '首页' },
  { path: '/settings', label: '设置' },
  { path: '/index', label: '索引' },
  { path: '/help', label: '帮助' },
])

const route = useRoute()

const isActive = (path: string): boolean => {
  return route.path === path
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
  gap: var(--space-sm, 8px);
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
  gap: var(--space-2xl, 24px);
}

.nav-link {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  text-decoration: none;
  padding: var(--space-sm, 8px) 0;
  position: relative;
  transition: color var(--transition-base);
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
  gap: var(--space-sm, 8px);
}

.action-btn {
  color: var(--text-secondary);
  font-size: 14px;
}

.action-btn:hover {
  color: var(--brand-blue);
}
</style>
```

#### 4.4.2 搜索结果卡片组件 ([components/common/XiResultCard.vue](../../frontend/src/renderer/src/components/common/XiResultCard.vue))

```vue
<template>
  <div class="result-card" :class="{ hover: isHovered }" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
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

const fileIcon = computed(() => {
  const iconMap = {
    audio: 'lucide:music',
    document: 'lucide:file-text',
    video: 'lucide:film',
    image: 'lucide:image',
    other: 'lucide:file',
  }
  return iconMap[props.result.type] || iconMap.other
})
</script>

<style scoped>
.result-card {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl, 12px);
  padding: var(--space-xl, 20px);
  box-shadow: var(--shadow-card);
  transition: all var(--transition-base);
}

.result-card.hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md, 12px);
  margin-bottom: var(--space-md, 12px);
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
  font-size: var(--text-xl, 22px);
  line-height: 1.27;
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin: 0 0 var(--space-sm, 6px) 0;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 8px);
}

.badge {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  border-radius: var(--radius-pill, 9999px);
  font-size: var(--text-xs, 12px);
  font-weight: 600;
  padding: 4px var(--space-sm, 8px);
}

.result-size {
  font-size: var(--text-sm, 14px);
  color: var(--text-tertiary);
}

.result-preview {
  margin-bottom: var(--space-md, 12px);
}

.preview-text {
  font-family: var(--font-body);
  font-size: var(--text-base, 16px);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-xs, 4px) 0;
}

.preview-path {
  font-size: var(--text-sm, 14px);
  color: var(--text-tertiary);
  margin: 0;
}

.result-actions {
  display: flex;
  gap: var(--space-xs, 4px);
  padding-top: var(--space-md, 12px);
  border-top: var(--border-standard);
}

.action-link {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: var(--text-sm, 14px);
  font-weight: 500;
  cursor: pointer;
  padding: var(--space-xs, 4px) var(--space-sm, 8px);
  border-radius: var(--radius-sm, 4px);
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

### 4.5 全局样式文件 ([styles/global.css](../../frontend/src/renderer/src/styles/global.css))

```css
/* ==================== 全局样式重置 ==================== */
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
  border-radius: var(--radius-md, 6px);
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

/* ==================== 动画类 ==================== */
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}

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

/* ==================== 工具类 ==================== */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.gap-sm { gap: var(--space-sm, 8px); }
.gap-md { gap: var(--space-md, 12px); }
.gap-lg { gap: var(--space-lg, 16px); }

.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary { color: var(--text-tertiary); }

.font-display { font-family: var(--font-display); }
.font-body { font-family: var(--font-body); }
```

---

## 5. 性能优化方案

### 5.1 字体加载优化

#### 5.1.1 字体子集化

```javascript
// vite.config.ts
import VitePluginFontMin from 'vite-plugin-font-min'

export default {
  plugins: [
    VitePluginFontMin({
      // 仅加载需要的字重和字符
      subsets: ['latin', 'latin-ext'],
      weights: [400, 500, 600, 700],
    })
  ]
}
```

#### 5.1.2 字体显示策略

```css
/* 字体加载策略 */
@font-face {
  font-family: 'Nunito';
  font-display: swap; /* 立即使用备用字体，加载后切换 */
  src: local('Nunito'),
       url('https://fonts.gstatic.com/s/nunito/v20/XRXV3I6Li01BKofIMeaB.woff2') format('woff2');
}
```

### 5.2 图标加载优化

#### 5.2.1 按需加载

```vue
<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { Icon } from '@iconify/vue'

// 仅在需要时加载图标
const XiIcon = defineAsyncComponent(() =>
  import('./XiIcon.vue')
)
</script>
```

#### 5.2.2 图标预加载

```javascript
// 预加载核心图标
const criticalIcons = [
  'lucide:home',
  'lucide:search',
  'lucide:settings',
  'lucide:music',
  'lucide:file-text',
]

// 在应用初始化时预加载
export function preloadIcons() {
  criticalIcons.forEach(icon => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'image'
    link.href = `https://api.iconify.design/${icon}.svg`
    document.head.appendChild(link)
  })
}
```

### 5.3 CSS优化

#### 5.3.1 CSS压缩

```javascript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    cssMinify: 'lightning', // 使用lightning-css压缩
  }
})
```

#### 5.3.2 CSS代码分割

```vue
<style scoped>
/* 使用scoped避免样式污染 */
.component-specific {
  /* 组件特定样式 */
}
</style>
```

### 5.4 渲染性能优化

#### 5.4.1 虚拟滚动

```vue
<!-- 搜索结果列表使用虚拟滚动 -->
<template>
  <RecycleScroller
    :items="results"
    :item-size="120"
    key-field="id"
    v-slot="{ item }"
  >
    <XiResultCard :result="item" />
  </RecycleScroller>
</template>

<script setup lang="ts">
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import XiResultCard from './XiResultCard.vue'
</script>
```

#### 5.4.2 防抖和节流

```typescript
// utils/performance.ts
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
```

---

## 6. 兼容性处理

### 6.1 浏览器兼容性

| 浏览器 | 最低版本 | CSS变量 | Grid | Flexbox | 说明 |
|-------|---------|---------|------|---------|------|
| Chrome | 88+ | ✅ | ✅ | ✅ | Electron内置 |
| Edge | 88+ | ✅ | ✅ | ✅ | Chromium内核 |
| Firefox | 85+ | ✅ | ✅ | ✅ | - |

### 6.2 优雅降级

#### 6.2.1 字体加载失败

```css
/* 备用字体栈 */
:root {
  --font-display: 'Work Sans', -apple-system, system-ui, 'Segoe UI', sans-serif;
  --font-body: 'Nunito', -apple-system, system-ui, 'Segoe UI', sans-serif;
}
```

#### 6.2.2 CSS变量不支持

```css
/* 为不支持CSS变量的浏览器提供备用值 */
.component {
  background: #ffffff; /* 备用值 */
  background: var(--bg-primary, #ffffff); /* CSS变量 + 备用值 */
}
```

### 6.3 移动端适配

```css
/* 响应式断点 */
@media (max-width: 768px) {
  .nav-links { display: none; }
  .action-buttons { flex-direction: column; }
  .search-box { padding: var(--space-md, 12px); }
  .result-card { padding: var(--space-md, 12px); }
}
```

---

## 7. 测试方案

### 7.1 视觉回归测试

#### 7.1.1 测试工具

```bash
npm install -D @playwright/test
```

#### 7.1.2 测试脚本

```typescript
// tests/visual/home-page.spec.ts
import { test, expect } from '@playwright/test'

test('homepage visual regression', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await expect(page).toHaveScreenshot('home-page.png', {
    fullPage: true,
    maxDiffPixels: 100,
  })
})
```

### 7.2 组件单元测试

```typescript
// tests/components/XiHeader.spec.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import XiHeader from '@/components/common/XiHeader.vue'

describe('XiHeader', () => {
  it('renders logo correctly', () => {
    const wrapper = mount(XiHeader)
    expect(wrapper.find('.logo-text').text()).toBe('小遥搜索')
  })

  it('has correct navigation links', () => {
    const wrapper = mount(XiHeader)
    const links = wrapper.findAll('.nav-link')
    expect(links).toHaveLength(4)
  })

  it('applies active class to current route', async () => {
    const wrapper = mount(XiHeader, {
      global: {
        mocks: {
          $route: { path: '/' }
        }
      }
    })
    const homeLink = wrapper.find('.nav-link')
    expect(homeLink.classes()).toContain('active')
  })
})
```

### 7.3 性能测试

```typescript
// tests/performance/font-load.spec.ts
import { test, expect } from '@playwright/test'

test('fonts load within 500ms', async ({ page }) => {
  const startTime = Date.now()
  await page.goto('http://localhost:5173')

  // 等待字体加载完成
  await page.waitForFunction(() => {
    return document.fonts.check('700 20px "Work Sans"') &&
           document.fonts.check('600 16px "Nunito"')
  })

  const loadTime = Date.now() - startTime
  expect(loadTime).toBeLessThan(500)
})
```

---

## 8. 部署方案

### 8.1 构建配置

```javascript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    target: 'es2020',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router'],
          'ui': ['ant-design-vue'],
          'icons': ['@iconify/vue'],
        }
      }
    }
  }
})
```

### 8.2 环境变量

```bash
# .env.production
VITE_APP_TITLE=小遥搜索
VITE_APP_VERSION=2.0.0
VITE_FONT_LOADER_TIMEOUT=5000
VITE_ICON_CDN=https://api.iconify.design
```

### 8.3 部署步骤

```bash
# 1. 安装依赖
npm install

# 2. 构建生产版本
npm run build

# 3. 验证构建产物
ls -la dist/

# 4. 启动应用
npm run electron:build

# 5. 测试验证
# - 检查字体是否正确加载
# - 检查图标是否正常显示
# - 检查所有页面样式是否正确
# - 检查响应式布局
```

---

## 9. 风险与应对

### 9.1 技术风险

| 风险项 | 风险等级 | 应对措施 | 负责人 |
|-------|---------|---------|-------|
| Google Fonts被墙 | 中 | 提供本地字体备份方案 | 前端开发 |
| Iconify服务不稳定 | 低 | 关键图标本地SVG备份 | 前端开发 |
| CSS变量兼容性 | 低 | 提供备用值和降级方案 | 前端开发 |
| 字体加载性能 | 中 | 子集化 + 预加载 + display:swap | 前端开发 |

### 9.2 回滚方案

```bash
# 如果出现问题，快速回滚到v1.9版本
git checkout v1.9.0
npm install
npm run build
npm run electron:build
```

---

## 10. 成功指标

### 10.1 性能指标

| 指标 | 目标值 | 测量方式 |
|-----|-------|---------|
| 字体加载时间 | <500ms | Chrome DevTools Network |
| 首屏渲染时间 | <2s | Chrome DevTools Performance |
| 页面交互响应 | <100ms | Chrome DevTools Performance |
| 内存占用 | 不增加10% | 任务管理器 |

### 10.2 质量指标

| 指标 | 目标值 | 测量方式 |
|-----|-------|---------|
| 视觉回归测试通过率 | 100% | Playwright截图对比 |
| 组件单元测试覆盖率 | >80% | Vitest |
| CSS一致性 | 100% | 设计系统验证 |

---

## 11. 后续优化

### 11.1 短期优化（v2.0.x）
- 收集用户反馈，微调设计细节
- 优化字体加载策略
- 完善动画性能

### 11.2 中期规划（v2.1+）
- 添加暗色模式支持
- 支持自定义主题
- 建立完整的设计资产库

### 11.3 长期愿景（v3.0+）
- 支持动态主题切换
- 探索更多创新交互
- 建立设计规范网站

---

**文档结束**

> **维护说明**：
> 1. 本文档为UI升级特性的完整技术方案
> 2. 所有技术实现均基于Vue 3 + TypeScript
> 3. 设计系统通过CSS Variables实现
> 4. 字体和图标均采用CDN加载，提供本地备份方案
