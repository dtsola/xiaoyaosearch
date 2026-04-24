# UI视觉系统升级 v2.0 - 原型设计

> **文档类型**：原型设计说明
> **基础版本**：基于 [主原型文档](../../02-原型.md)
> **特性状态**：已完成
> **创建时间**：2026-04-24
> **最后更新**：2026-04-24

---

## 1. 设计理念

### 1.1 设计原则
- **温暖明亮专业**：借鉴Notion的设计语言，创造舒适且专业的视觉体验
- **克制而不失个性**：避免过度装饰，通过细节和一致性建立品质感
- **可读性优先**：适合知识工作者长时间使用的清晰视觉层次
- **品牌识别度**：通过独特的字体组合和精致细节建立品牌记忆点

### 1.2 设计风格
- **Notion温暖明亮风格**：#ffffff纯白背景 + #0075de品牌蓝 + 温暖中性灰
- **系统字体方案**：精心挑选的系统字体栈，模拟Notion风格（零网络依赖，最优性能）
- **精致阴影层次**：4-5层阴影堆叠，创造深度但不厚重
- **超细边框**：0.08-0.1透明度的whisper border，细腻精致
- **微妙动画**：fadeInUp进入动画，流畅的hover过渡

---

## 2. 设计系统规范

### 2.1 色彩系统

#### 背景色系
```css
--bg-primary: #ffffff           /* 纯白主背景 */
--bg-secondary: #f6f5f4         /* 温暖白次要背景 */
--bg-tertiary: #f9f8f6          /* 浅灰背景 */
--bg-hover: rgba(0, 0, 0, 0.03) /* 悬停背景 */
```

#### 文字色系
```css
--text-primary: rgba(0, 0, 0, 0.92)    /* 主要文字 */
--text-secondary: #615d59              /* 次要文字 */
--text-tertiary: #9a9590               /* 辅助文字 */
--text-muted: #b8b3ae                  /* 弱化文字 */
```

#### 品牌色系
```css
--brand-blue: #0075de              /* Notion蓝 */
--brand-blue-hover: #005fb8        /* 悬停蓝 */
--brand-blue-light: #e8f4fd        /* 浅蓝背景 */
--brand-blue-lighter: #f0f7ff       /* 更浅蓝背景 */
```

#### 语义色系
```css
--success-green: #2a9d99      /* 成功 */
--warning-orange: #dd5b00     /* 警告 */
--accent-purple: #7c3aed      /* 强调 */
```

#### 边框色系
```css
--border-subtle: 1px solid rgba(0, 0, 0, 0.08)   /* 超细边框 */
--border-standard: 1px solid rgba(0, 0, 0, 0.1) /* 标准边框 */
--border-light: rgba(0, 0, 0, 0.06)             /* 浅色边框 */
```

### 2.2 字体系统

#### 字体选择（系统字体优化方案）
| 用途 | 字体栈 | 字重 | 特点 |
|-----|--------|------|------|
| **标题** | -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif | 400, 500, 600, 700 | macOS: SF Pro Text（圆润、清晰），Windows: Segoe UI（现代、专业） |
| **正文** | -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif | 400, 500, 600, 700 | 与标题相同，保持视觉一致性 |
| **代码** | 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace | 400 | 等宽、清晰 |

#### 字体层次
```css
/* 标题 */
--font-display:
  -apple-system,
  BlinkMacSystemFont,
  'Segoe UI',
  'PingFang SC',
  'Microsoft YaHei',
  sans-serif;

/* 正文 */
--font-body:
  -apple-system,
  BlinkMacSystemFont,
  'Segoe UI',
  'PingFang SC',
  'Microsoft YaHei',
  sans-serif;

/* 代码 */
--font-code:
  'SF Mono',
  'Consolas',
  'Monaco',
  'Courier New',
  monospace;
```

#### 字体方案说明
- **零网络依赖**：使用系统字体，无需加载外部字体文件，显著提升性能
- **跨平台优化**：针对macOS、Windows、Linux提供最佳字体降级方案
- **Notion风格**：通过精心挑选的系统字体栈，模拟Notion温暖明亮的视觉效果
- **加载性能**：字体加载时间<10ms（系统原生字体）

#### 字号系统
```css
--text-xs: 12px    /* 小标签、辅助信息 */
--text-sm: 14px    /* 次要文字、说明 */
--text-base: 16px  /* 正文 */
--text-lg: 18px    /* 小标题 */
--text-xl: 22px    /* 大标题 */
--text-2xl: 28px   /* 特大标题 */
```

### 2.3 间距系统（8px基准）

```css
--space-xs: 4px    /* 元素内紧凑间距 */
--space-sm: 8px    /* 小间距 */
--space-md: 12px   /* 中等间距 */
--space-lg: 16px   /* 标准间距 */
--space-xl: 20px   /* 卡片内边距 */
--space-2xl: 24px  /* 区块间距 */
--space-3xl: 32px  /* 大区块间距 */
```

### 2.4 圆角系统

```css
--radius-sm: 4px     /* 按钮 */
--radius-md: 6px     /* 小卡片、标签 */
--radius-lg: 10px    /* 中卡片 */
--radius-xl: 12px    /* 大卡片 */
--radius-pill: 9999px /* 徽章、标签 */
```

### 2.5 阴影系统

#### 卡片阴影（4层堆叠）
```css
--shadow-card:
  rgba(0, 0, 0, 0.02) 0px 2px 8px,
  rgba(0, 0, 0, 0.015) 0px 1px 4px,
  rgba(0, 0, 0, 0.01) 0px 0.5px 2px,
  rgba(0, 0, 0, 0.008) 0px 0.2px 1px;
```

#### 悬浮阴影（5层堆叠）
```css
--shadow-elevated:
  rgba(0, 0, 0, 0.03) 0px 4px 12px,
  rgba(0, 0, 0, 0.02) 0px 2px 6px,
  rgba(0, 0, 0, 0.015) 0px 1px 3px,
  rgba(0, 0, 0, 0.01) 0px 0.5px 1px,
  rgba(0, 0, 0, 0.008) 0px 0.2px 0.5px;
```

#### 焦点效果
```css
--shadow-focus: 0 0 0 3px rgba(0, 117, 222, 0.15);
```

### 2.6 动画系统

```css
/* 过渡时长 */
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

/* 页面加载动画 */
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
```

---

## 3. 图标系统

### 3.1 图标库选择：Lucide Icons

#### 选择理由
| 维度 | 评估 | 说明 |
|-----|------|------|
| 设计风格 | ⭐⭐⭐⭐⭐ | 清晰简洁的outline风格，与Notion温暖明亮风格完美契合 |
| 一致性 | ⭐⭐⭐⭐⭐ | 1000+图标高度一致，笔画粗细统一（2px stroke） |
| 可读性 | ⭐⭐⭐⭐⭐ | 24px标准网格，优化的视觉平衡 |
| 现代感 | ⭐⭐⭐⭐⭐ | 基于Feather Icons改进，更加专业 |

#### 图标尺寸
```css
--icon-xs: 16px   /* 紧凑空间 */
--icon-sm: 18px   /* 小尺寸 */
--icon-md: 20px   /* 默认尺寸 */
--icon-lg: 24px   /* 大尺寸 */
--icon-xl: 32px   /* 特大尺寸 */
```

#### 图标颜色
```css
--icon-primary: var(--text-primary);      /* 主要图标 */
--icon-secondary: var(--text-secondary);  /* 次要图标 */
--icon-tertiary: var(--text-tertiary);    /* 辅助图标 */
--icon-brand: var(--brand-blue);          /* 品牌色图标 */
--icon-muted: var(--text-muted);          /* 弱化图标 */
```

### 3.2 核心图标清单（35个）

#### 导航类（4个）
```
首页:    lucide:home
设置:    lucide:settings
索引:    lucide:list
帮助:    lucide:help-circle
```

#### 多模态输入（4个）
```
语音:    lucide:mic
文本:    lucide:keyboard
图像:    lucide:image
AI智能:  lucide:sparkles
```

#### 功能操作（5个）
```
搜索:    lucide:search
AI增强:  lucide:bar-chart-3
选择目录: lucide:folder-open
计时器:  lucide:clock
筛选:    lucide:filter
```

#### 结果操作（5个）
```
预览:    lucide:eye
打开位置: lucide:external-link
收藏:    lucide:star
复制:    lucide:copy
删除:    lucide:trash-2
```

#### 文件类型（6个）
```
音频:    lucide:music
文档:    lucide:file-text
视频:    lucide:film
图片:    lucide:image
代码:    lucide:code-2
压缩:    lucide:archive
```

#### 状态指示（8个）
```
语言:    lucide:globe
通知:    lucide:bell
主题:    lucide:moon
用户:    lucide:user
成功:    lucide:check-circle-2
错误:    lucide:x-circle
警告:    lucide:alert-triangle
加载中:  lucide:loader-2
```

---

## 4. 页面视觉设计

### 4.1 顶部导航栏

```
┌────────────────────────────────────────────────────────────────────┐
│  ◤ 小遥搜索 ◢ v2.0                                          [─][□][×] │
├────────────────────────────────────────────────────────────────────┤
│  ●首页 ◇设置 ◇索引 ◇帮助    [🌐 中文] [🔔] [👤 admin]              │
└────────────────────────────────────────────────────────────────────┘
```

**设计要点**：
- **高度**：56px
- **Logo**：◤ 符号 + "小遥搜索" 文字（Work Sans 700 18px） + "v2.0" 版本号（12px）
- **导航项**：圆点（●）表示当前页面，菱形（◇）表示其他页面
- **右侧操作**：语言切换、通知、用户头像

**样式规范**：
```css
.header {
  height: 56px;
  background: var(--bg-primary);
  border-bottom: var(--border-standard);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-text {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.25px;
}

.nav-link {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  padding: 8px 0;
  position: relative;
}

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
```

### 4.2 搜索主页面

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│    ●          ●          ●                                       │
│  🎙️         ✏️         🖼️                                       │
│  语音        文本        图像                                       │
│                                                                    │
│  ╔══════════════════════════════════════════════════════════════╗  │
│  ║  ╭─────────────────────────────────────────────────────────╮ ║  │
│  ║  │  ✨  说出你的想法，或开始输入...                          │ ║  │
│  ║  │  ⏱️ 30s                                                  │ ║  │
│  ║  ╰─────────────────────────────────────────────────────────╯ ║  │
│  ║                                                              ║  │
│  ║  [⚡ 智能搜索]  [📈 AI增强]  [📂 选择目录]                     ║  │
│  ╚══════════════════════════════════════════════════════════════╝  │
│                                                                    │
│  ● AI引擎: Ollama  ● 搜索空间: 所有文件夹                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**设计要点**：
- **多模态指示器**：三个圆形指示器，当前选中状态为蓝色填充
- **搜索框**：最大宽度700px，圆角16px，多层阴影
- **输入框**：圆角4px，焦点时显示蓝色光晕
- **按钮**：圆角4px，悬停时scale(1.05)

**样式规范**：
```css
.search-box {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-card);
  max-width: 700px;
  margin: 0 auto;
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
  transition: all 0.2s;
}

.indicator.active {
  background: var(--brand-blue-light);
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 2px rgba(0, 117, 222, 0.2);
}

.search-input {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 4px;
  font-family: var(--font-body);
  font-size: 16px;
  padding: 12px 16px;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: var(--brand-blue);
  box-shadow: var(--shadow-focus);
}

.btn {
  height: 44px;
  border-radius: 4px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--brand-blue);
  color: #ffffff;
}

.btn-primary:hover {
  background: var(--brand-blue-hover);
  transform: scale(1.05);
}
```

### 4.3 搜索结果卡片

```
╔══════════════════════════════════════════════════════════════════╗
║  🎵                                                              ║
║  AI讨论_2024-11-15.mp3                                           ║
║                                                                  ║
║  ┌────────────────────────────────────────────────────────────┐  ║
║  │  🎯 匹配度: 95%  │  📊 大小: 2.3MB                         │  ║
║  │  💬 "技术会议录音，深入讨论AI发展趋势、机器学习..."          │  ║
║  │  📍 D:\Work\Audio\AI_2024.mp3                              │  ║
║  └────────────────────────────────────────────────────────────┘  ║
║                                                                  ║
║  [👁️ 预览]  [📂 打开]  [⭐ 收藏]  [🔗 复制]  [🗑️ 删除]              ║
╚══════════════════════════════════════════════════════════════════╝
```

**设计要点**：
- **卡片圆角**：12px
- **内边距**：20px
- **阴影**：4层堆叠
- **悬停效果**：阴影加深，轻微上移
- **图标大小**：24px（文件类型），16px（操作按钮）

**样式规范**：
```css
.result-card {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-card);
  transition: all 0.2s;
}

.result-card:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.result-icon {
  font-size: 24px;
  color: var(--brand-blue);
}

.result-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 22px;
  line-height: 1.27;
  letter-spacing: -0.25px;
  color: var(--text-primary);
}

.result-badge {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
}

.action-link {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-link:hover {
  color: var(--brand-blue);
}
```

### 4.4 底部状态栏

```
┌────────────────────────────────────────────────────────────────────┐
│  📊 索引: 1,234文件  │  🔍 今日: 15次搜索  │  💾 数据: 8.7GB        │
└────────────────────────────────────────────────────────────────────┘
```

**设计要点**：
- **高度**：40px
- **背景**：与主背景相同
- **上边框**：超细边框
- **文字**：12px，浅灰色

**样式规范**：
```css
.footer {
  background: var(--bg-primary);
  border-top: var(--border-standard);
  padding: 12px 24px;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 500;
}
```

---

## 5. 组件设计规范

### 5.1 按钮组件

#### 主要按钮
```css
.btn-primary {
  background: var(--brand-blue);
  color: #ffffff;
  border: none;
  border-radius: 4px;
  height: 44px;
  padding: 0 20px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--brand-blue-hover);
  transform: scale(1.05);
}

.btn-primary:active {
  transform: scale(0.95);
}
```

#### 次要按钮
```css
.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
  border-radius: 4px;
  height: 44px;
  padding: 0 20px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--bg-hover);
  transform: scale(1.05);
}
```

### 5.2 输入框组件

```css
.input {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 4px;
  padding: 12px 16px;
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.2s;
}

.input:focus {
  border-color: var(--brand-blue);
  box-shadow: var(--shadow-focus);
}

.input::placeholder {
  color: var(--text-tertiary);
}
```

### 5.3 徽章组件

```css
.badge {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge.success {
  background: #e8f5e9;
  color: #2a9d99;
}

.badge.warning {
  background: #fff3e0;
  color: #dd5b00;
}
```

---

## 6. 响应式设计

### 6.1 断点系统

```css
/* 紧凑模式 */
@media (max-width: 800px) {
  .search-container { padding: 16px; }
  .action-buttons { flex-direction: column; }
}

/* 标准模式 */
@media (min-width: 801px) and (max-width: 1200px) {
  .content { max-width: 100%; }
}

/* 沉浸模式 */
@media (min-width: 1201px) {
  .content { max-width: 1200px; margin: 0 auto; }
}
```

### 6.2 移动端适配

```css
@media (max-width: 768px) {
  .nav-links { display: none; }
  .search-box { padding: 16px; }
  .result-card { padding: 16px; }
  .action-buttons { flex-direction: column; gap: 8px; }
}
```

---

## 7. 动画与交互

### 7.1 页面加载动画

```css
.animate-fade-in {
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
```

### 7.2 悬停效果

```css
.hover-lift {
  transition: all 0.2s;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-elevated);
}
```

### 7.3 状态切换

```css
.mode-transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 8. 设计资产

### 8.1 视觉设计文件

**路径**：`docs/视觉设计/`

| 文件名 | 说明 | 状态 |
|-------|------|------|
| notion-warm-v1.html | Notion温暖明亮风格 v1（推荐） | ✅ 已完成 |
| notion-warm-v2.html | Notion温暖明亮风格 v2（备选） | ✅ 已完成 |
| notion-warm-v3.html | Notion温暖明亮风格 v3（备选） | ✅ 已完成 |
| icons-preview.html | Lucide图标库预览 | ✅ 已完成 |
| README.md | 视觉设计说明文档 | ✅ 已完成 |

### 8.2 图标系统文档

**路径**：`docs/特性开发/ui-update/ui-update-图标系统.md`

包含：
- 图标库选择理由
- 完整图标映射表（35个核心图标）
- 使用规范和技术实现
- Vue组件封装示例

---

## 9. 实现指南

### 9.1 字体加载

```html
<!-- 系统字体方案，无需加载外部字体 -->
<!-- v2.0已优化为系统字体，零网络依赖 -->
```

```typescript
// 字体加载器（系统字体方案）
// frontend/src/renderer/src/utils/font-loader.ts
// 说明: v2.0使用系统字体，不再加载外部字体
// 保留此工具类以备将来需要加载其他字体资源
```

### 9.2 CSS变量定义

```css
/* 在全局样式文件中定义 */
:root {
  /* 背景色系 */
  --bg-primary: #ffffff;
  --bg-secondary: #f6f5f4;
  --bg-tertiary: #f9f8f6;
  --bg-hover: rgba(0, 0, 0, 0.03);

  /* 文字色系 */
  --text-primary: rgba(0, 0, 0, 0.92);
  --text-secondary: #615d59;
  --text-tertiary: #9a9590;
  --text-muted: #b8b3ae;

  /* 品牌色系 */
  --brand-blue: #0075de;
  --brand-blue-hover: #005fb8;
  --brand-blue-light: #e8f4fd;

  /* 字体系统（系统字体优化方案） */
  --font-display:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'PingFang SC',
    'Microsoft YaHei',
    sans-serif;

  --font-body:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'PingFang SC',
    'Microsoft YaHei',
    sans-serif;

  --font-code:
    'SF Mono',
    'Consolas',
    'Monaco',
    'Courier New',
    monospace;

  /* ... 其他变量 */
}
```

### 9.3 图标组件使用

```vue
<template>
  <!-- 使用Iconify图标 -->
  <iconify-icon icon="lucide:home" :width="20" :height="20" />

  <!-- 或使用封装的XiIcon组件 -->
  <XiIcon icon="lucide:search" :size="24" color="#0075de" />
</template>

<script setup>
import { Icon } from '@iconify/vue';
// 或
import XiIcon from '@/components/XiIcon.vue';
</script>
```

---

## 10. 对比分析

### 10.1 v1.9 vs v2.0 视觉对比

| 维度 | v1.9 | v2.0 | 改进点 |
|-----|------|------|-------|
| **字体** | Inter / 系统字体 | 精心挑选的系统字体栈 | 零网络依赖，性能最优 |
| **色彩** | 通用配色 | Notion温暖明亮 | 更专业统一 |
| **阴影** | 简单阴影 | 4-5层堆叠 | 更精致有深度 |
| **边框** | 1px实线 | 超细whisper边框 | 更细腻精致 |
| **图标** | Emoji | Lucide Icons | 更一致专业 |
| **动画** | 无/简单 | fadeInUp + 流畅过渡 | 更生动流畅 |
| **圆角** | 混乱不统一 | 4/6/10/12px系统 | 更一致规范 |

### 10.2 用户体验提升

| 指标 | v1.9 | v2.0 | 提升 |
|-----|------|------|------|
| 视觉舒适度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| 品牌识别度 | ⭐⭐ | ⭐⭐⭐⭐ | +100% |
| 信息可读性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| 专业度感知 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |

---

## 11. 设计交付清单

### 11.1 设计文档
- [x] PRD文档（ui-update-01-prd.md）
- [x] 原型设计文档（ui-update-02-原型.md）✅ 本文档
- [ ] 技术方案文档（ui-update-03-技术方案.md）
- [ ] 开发任务清单（ui-update-04-开发任务清单.md）

### 11.2 视觉设计文件
- [x] notion-warm-v1.html（推荐方案）
- [x] notion-warm-v2.html（备选方案）
- [x] notion-warm-v3.html（备选方案）
- [x] icons-preview.html（图标预览）
- [x] README.md（设计说明）

### 11.3 图标系统
- [x] 图标系统文档（ui-update-图标系统.md）
- [x] 35个核心图标选择
- [x] Vue组件封装示例

---

## 12. 后续规划

### 12.1 短期优化（v2.0.x）
- 收集用户反馈，微调细节
- 已采用系统字体方案，性能最优
- 完善动画性能

### 12.2 中期规划（v2.1+）
- 考虑添加暗色模式
- 支持自定义主题
- 建立完整的设计资产库

### 12.3 长期愿景（v3.0+）
- 支持动态主题切换
- 探索更多创新交互
- 建立设计规范网站

---

## 13. 参考资源

### 13.1 设计参考
- [Notion官网](https://notion.so) - 设计灵感来源
- [Notion设计系统](../../base/design-md/notion/DESIGN.md) - 详细设计规范
- [Linear设计](../../base/design-md/linear.app/DESIGN.md) - 暗色设计参考

### 13.2 字体资源
- **系统字体方案**：使用系统原生字体，无需外部资源
- **参考**：Notion系统字体栈实现

### 13.3 图标资源
- [Lucide Icons官网](https://lucide.dev/)
- [图标预览页面](../../视觉设计/icons-preview.html)
- [图标系统文档](./ui-update-图标系统.md)

---

**文档结束**

> **维护说明**：
> 1. 本文档为UI升级特性的完整原型设计说明
> 2. 所有设计决策基于Notion温暖明亮风格
> 3. v2.0已采用系统字体方案，零网络依赖
> 4. 视觉设计文件已保存在 `docs/视觉设计/` 目录
> 5. 图标系统详见 `ui-update-图标系统.md`
