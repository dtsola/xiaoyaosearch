# 小遥搜索 v2.0 - 图标系统规范

> **文档类型**：UI设计规范 - 图标系统
> **适用版本**：v2.0.0
> **创建时间**：2026-04-24
> **设计风格**：Notion温暖明亮风格

---

## 1. 图标库选择

### 1.1 推荐方案：Lucide Icons

**选择理由**：

| 维度 | 评估 | 说明 |
|-----|------|------|
| **设计风格** | ⭐⭐⭐⭐⭐ | 清晰简洁的outline风格，与Notion温暖明亮风格完美契合 |
| **一致性** | ⭐⭐⭐⭐⭐ | 1000+图标高度一致，笔画粗细统一（2px stroke） |
| **可读性** | ⭐⭐⭐⭐⭐ | 24px标准网格，优化的视觉平衡，适合知识工作者长时间使用 |
| **现代感** | ⭐⭐⭐⭐⭐ | 基于Feather Icons改进，更加现代和专业 |
| **兼容性** | ⭐⭐⭐⭐⭐ | 支持Vue、React、Web Components等多种使用方式 |
| **生态支持** | ⭐⭐⭐⭐⭐ | 通过Iconify集成，CDN支持，社区活跃 |

### 1.2 备选方案

**Heroicons**：由Tailwind CSS团队制作，简洁优雅，但图标数量较少
**Phosphor Icons**：现代且一致性好，有outline和filled两种风格
**Tabler Icons**：开源免费，图标数量庞大（4000+），但风格稍显复杂

> **结论**：Lucide Icons是最佳选择，完美匹配Notion温暖明亮风格的专业、清晰、简洁特点。

---

## 2. 图标使用规范

### 2.1 尺寸规范

```css
/* 图标尺寸系统 */
--icon-xs: 16px   /* 紧凑空间，如按钮内图标 */
--icon-sm: 18px   /* 小尺寸，如列表项图标 */
--icon-md: 20px   /* 默认尺寸，如导航栏图标 */
--icon-lg: 24px   /* 大尺寸，如主功能图标 */
--icon-xl: 32px   /* 特大尺寸，如空状态插图 */
```

### 2.2 颜色规范

```css
/* 图标颜色系统 */
--icon-primary: var(--text-primary);      /* 主要图标：rgba(0, 0, 0, 0.92) */
--icon-secondary: var(--text-secondary);  /* 次要图标：#615d59 */
--icon-tertiary: var(--text-tertiary);    /* 辅助图标：#9a9590 */
--icon-brand: var(--brand-blue);          /* 品牌色图标：#0075de */
--icon-muted: var(--text-muted);          /* 弱化图标：#b8b3ae */
```

### 2.3 视觉权重

```css
/* 笔画粗细（Lucide默认为2px） */
stroke-width: 2;

/* 图标与文字的间距 */
gap: 6px;  /* 图标与文字相邻时 */
gap: 8px;  /* 图标作为独立元素时 */
```

### 2.4 交互状态

```css
/* 悬停状态 */
.icon:hover {
  color: var(--brand-blue);
  opacity: 0.8;
}

/* 激活状态 */
.icon.active {
  color: var(--brand-blue);
}

/* 禁用状态 */
.icon.disabled {
  color: var(--icon-tertiary);
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## 3. 完整图标映射表

### 3.1 导航图标

| 功能 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 首页 | `lucide:home` | 20px | secondary | 顶部导航 |
| 设置 | `lucide:settings` | 20px | secondary | 顶部导航 |
| 索引 | `lucide:list` | 20px | secondary | 顶部导航 |
| 帮助 | `lucide:help-circle` | 20px | secondary | 顶部导航 |

**预览**：
- 首页：🏠 `lucide:home`
- 设置：⚙️ `lucide:settings`
- 索引：📋 `lucide:list`
- 帮助：❓ `lucide:help-circle`

### 3.2 多模态输入图标

| 功能 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 语音输入 | `lucide:mic` | 24px | brand | 搜索框模式选择器 |
| 文本输入 | `lucide:keyboard` | 24px | brand | 搜索框模式选择器 |
| 图像输入 | `lucide:image` | 24px | tertiary（禁用状态） | 搜索框模式选择器 |
| AI智能 | `lucide:sparkles` | 18px | brand | AI增强按钮 |

**预览**：
- 语音：🎙️ `lucide:mic`
- 文本：⌨️ `lucide:keyboard`
- 图像：🖼️ `lucide:image`
- AI智能：✨ `lucide:sparkles`

### 3.3 功能操作图标

| 功能 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 搜索 | `lucide:search` | 18px | brand | 搜索按钮 |
| AI增强 | `lucide:bar-chart-3` | 18px | secondary | AI分析按钮 |
| 选择目录 | `lucide:folder-open` | 18px | secondary | 目录选择按钮 |
| 计时器 | `lucide:clock` | 14px | tertiary | 搜索倒计时 |

**预览**：
- 搜索：🔍 `lucide:search`
- AI增强：📊 `lucide:bar-chart-3`
- 选择目录：📂 `lucide:folder-open`
- 计时器：⏱️ `lucide:clock`

### 3.4 结果操作图标

| 功能 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 预览 | `lucide:eye` | 16px | secondary | 结果卡片操作栏 |
| 打开位置 | `lucide:external-link` | 16px | secondary | 结果卡片操作栏 |
| 收藏 | `lucide:star` | 16px | secondary | 结果卡片操作栏 |
| 复制 | `lucide:copy` | 16px | secondary | 结果卡片操作栏 |
| 删除 | `lucide:trash-2` | 16px | warning | 结果卡片操作栏 |

**预览**：
- 预览：👁️ `lucide:eye`
- 打开位置：🔗 `lucide:external-link`
- 收藏：⭐ `lucide:star`
- 复制：📋 `lucide:copy`
- 删除：🗑️ `lucide:trash-2`

### 3.5 文件类型图标

| 文件类型 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|---------|--------|------|------|---------|
| 音频文件 | `lucide:music` | 24px | brand | 结果卡片文件图标 |
| 文档文件 | `lucide:file-text` | 24px | brand | 结果卡片文件图标 |
| 视频文件 | `lucide:film` | 24px | brand | 结果卡片文件图标 |
| 图片文件 | `lucide:image` | 24px | brand | 结果卡片文件图标 |
| 代码文件 | `lucide:code-2` | 24px | brand | 结果卡片文件图标 |
| 压缩文件 | `lucide:archive` | 24px | brand | 结果卡片文件图标 |

**预览**：
- 音频：🎵 `lucide:music`
- 文档：📄 `lucide:file-text`
- 视频：🎬 `lucide:film`
- 图片：🖼️ `lucide:image`
- 代码：💻 `lucide:code-2`
- 压缩：📦 `lucide:archive`

### 3.6 状态指示图标

| 功能 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 语言切换 | `lucide:globe` | 16px | secondary | 顶部导航栏 |
| 通知 | `lucide:bell` | 16px | secondary | 顶部导航栏 |
| 主题切换 | `lucide:moon` | 16px | secondary | 顶部导航栏（预留） |
| 用户头像 | `lucide:user` | 16px | secondary | 顶部导航栏 |

**预览**：
- 语言：🌐 `lucide:globe`
- 通知：🔔 `lucide:bell`
- 主题：🌙 `lucide:moon`
- 用户：👤 `lucide:user`

### 3.7 状态/反馈图标

| 状态 | 图标ID | 尺寸 | 颜色 | 使用位置 |
|-----|--------|------|------|---------|
| 成功 | `lucide:check-circle-2` | 20px | success | 操作成功提示 |
| 错误 | `lucide:x-circle` | 20px | warning | 错误提示 |
| 警告 | `lucide:alert-triangle` | 20px | warning | 警告提示 |
| 信息 | `lucide:info` | 20px | brand | 信息提示 |
| 加载中 | `lucide:loader-2` | 20px | brand | 加载状态 |

---

## 4. 技术实现

### 4.1 安装依赖

**方案1：使用 @iconify/vue（推荐）**
```bash
npm install @iconify/vue
```

**方案2：使用 lucide-vue-next**
```bash
npm install lucide-vue-next
```

### 4.2 Vue 组件封装

```vue
<!-- components/XiIcon.vue -->
<template>
  <Icon :icon="icon" :width="size" :height="size" :color="color" />
</template>

<script setup>
import { Icon } from '@iconify/vue';

const props = defineProps({
  icon: {
    type: String,
    required: true,
    validator: (value) => value.startsWith('lucide:')
  },
  size: {
    type: [String, Number],
    default: 20
  },
  color: {
    type: String,
    default: 'currentColor'
  }
});
</script>
```

### 4.3 使用示例

```vue
<template>
  <!-- 导航图标 -->
  <XiIcon icon="lucide:home" :size="20" class="nav-icon" />

  <!-- 品牌色图标 -->
  <XiIcon icon="lucide:search" :size="18" color="#0075de" />

  <!-- 带文字的图标按钮 -->
  <button class="btn-icon">
    <XiIcon icon="lucide:star" :size="16" />
    <span>收藏</span>
  </button>
</template>
```

### 4.4 CSS 样式

```css
/* 图标基础样式 */
.xi-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color var(--transition-base), opacity var(--transition-base);
}

/* 导航图标 */
.nav-icon {
  color: var(--icon-secondary);
}

.nav-icon:hover,
.nav-icon.active {
  color: var(--icon-brand);
}

/* 按钮内图标 */
.btn-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
}

/* 结果卡片操作图标 */
.action-icon {
  color: var(--icon-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}

.action-icon:hover {
  color: var(--icon-brand);
  background: var(--bg-hover);
}

/* 危险操作图标 */
.action-icon.danger:hover {
  color: var(--warning-orange);
}
```

---

## 5. 图标动画

### 5.1 加载动画

```vue
<template>
  <Icon icon="lucide:loader-2" :width="24" :height="24" class="spin" />
</template>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
```

### 5.2 悬停效果

```css
/* 图标轻微放大 */
.icon-hover:hover {
  transform: scale(1.1);
}

/* 图标颜色渐变 */
.icon-gradient {
  transition: color var(--transition-base);
}

.icon-gradient:hover {
  color: var(--brand-blue);
}
```

### 5.3 状态切换动画

```vue
<template>
  <Transition name="icon-fade" mode="out-in">
    <Icon :key="state" :icon="currentIcon" />
  </Transition>
</template>

<style>
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.2s ease;
}

.icon-fade-enter-from,
.icon-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
```

---

## 6. 无障碍支持

### 6.1 ARIA 属性

```vue
<template>
  <!-- 带语义的图标 -->
  <button aria-label="搜索">
    <Icon icon="lucide:search" aria-hidden="true" />
  </button>

  <!-- 装饰性图标 -->
  <span class="text-with-icon">
    <Icon icon="lucide:star" aria-hidden="true" />
    收藏
  </span>
</template>
```

### 6.2 键盘导航

```css
/* 图标按钮焦点样式 */
.icon-button:focus-visible {
  outline: 2px solid var(--brand-blue);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

---

## 7. 性能优化

### 7.1 按需加载

使用 Iconify 的按需加载机制，只加载实际使用的图标：

```javascript
// vite.config.js
import { createIconsPlugin } from 'vite-plugin-icons'

export default {
  plugins: [
    createIconsPlugin({
      // 配置按需加载
    })
  ]
}
```

### 7.2 图标预加载

对于关键图标，可以预先加载：

```html
<link rel="preload" href="/icons/lucide/search.svg" as="image" />
```

---

## 8. 完整图标清单

### 8.1 按功能分类

#### 导航类（4个）
- lucide:home - 首页
- lucide:settings - 设置
- lucide:list - 索引
- lucide:help-circle - 帮助

#### 输入类（4个）
- lucide:mic - 语音输入
- lucide:keyboard - 文本输入
- lucide:image - 图像输入
- lucide:search - 搜索

#### 功能类（5个）
- lucide:sparkles - AI智能
- lucide:bar-chart-3 - AI增强
- lucide:folder-open - 选择目录
- lucide:clock - 计时器
- lucide:filter - 筛选

#### 操作类（5个）
- lucide:eye - 预览
- lucide:external-link - 打开位置
- lucide:star - 收藏
- lucide:copy - 复制
- lucide:trash-2 - 删除

#### 文件类型类（8个）
- lucide:music - 音频文件
- lucide:file-text - 文档文件
- lucide:film - 视频文件
- lucide:image - 图片文件
- lucide:code-2 - 代码文件
- lucide:archive - 压缩文件
- lucide:file-code - 代码文件
- lucide:file-json - JSON文件

#### 状态类（6个）
- lucide:globe - 语言
- lucide:bell - 通知
- lucide:moon - 主题
- lucide:user - 用户
- lucide:check-circle-2 - 成功
- lucide:x-circle - 错误
- lucide:alert-triangle - 警告
- lucide:info - 信息
- lucide:loader-2 - 加载中

**总计：约35个核心图标**

---

## 9. 设计资源

### 9.1 官方资源

- **Lucide Icons官网**：https://lucide.dev/
- **Iconify搜索**：https://icon-sets.iconify.design/lucide/
- **GitHub仓库**：https://github.com/lucide-icons/lucide

### 9.2 设计文件

所有图标的SVG源文件和预览已保存至：
- `docs/视觉设计/icons-preview.html`（待创建）

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v1.0 | 2026-04-24 | 初始版本，确定Lucide Icons为v2.0图标库 |

---

## 11. FAQ

**Q1: 为什么选择Lucide而不是其他图标库？**
A: Lucide的outline风格与Notion温暖明亮风格完美契合，笔画粗细（2px）和设计哲学都非常接近，能够保持设计的一致性。

**Q2: 如何确保图标加载性能？**
A: 使用Iconify的按需加载机制，只加载实际使用的图标，且SVG文件大小通常<1KB，对性能影响极小。

**Q3: 可以自定义图标的颜色吗？**
A: 可以。Lucide图标使用currentColor，可以通过CSS的color属性或组件的color prop来自定义颜色。

**Q4: 图标的圆角和Notion一致吗？**
A: Lucide图标的圆角处理较为克制，与Notion的风格相近。如需更圆润的效果，可以通过CSS微调。

**Q5: 是否支持暗色模式？**
A: 是的，图标使用currentColor，会自动适配暗色模式的文字颜色。v2.0.0暂不支持暗色模式，但图标系统已为未来做准备。

---

**文档结束**

> **维护说明**：
> 1. 本文档为小遥搜索v2.0的图标系统规范
> 2. 所有图标均来自Lucide Icons库
> 3. 使用时请遵守Lucide的ISC许可证
> 4. 如需新增图标，请优先在Lucide库中搜索，保持风格一致
