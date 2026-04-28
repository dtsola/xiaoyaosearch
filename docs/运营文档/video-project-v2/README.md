# 小遥搜索 v2.0.0 版本宣传片项目

## 项目概述

这是小遥搜索 v2.0.0 版本宣传片 Remotion 项目，基于 v1.0 版本宣传片项目创建。

**视频时长**：2 分 30 秒（4500帧 @ 30fps）  
**视频风格**：Notion 温暖明亮设计风格  
**发布日期**：2026年4月24日

## 项目结构

```
video-project-v2/
├── src/
│   ├── Composition.tsx          # 主组合
│   ├── Root.tsx                 # Remotion 根组件
│   ├── components/
│   │   └── animations.ts        # 动画工具函数
│   ├── scenes/
│   │   ├── Scene1Opening.tsx           # 场景1：开场引入 (15秒)
│   │   ├── Scene2VersionHistory.tsx    # 场景2：版本演进回顾 (35秒)
│   │   ├── Scene3UIUpgrade.tsx         # 场景3：UI升级展示 (80秒) 【重点】
│   │   ├── Scene4TechStack.tsx         # 场景4：技术架构回顾 (8秒)
│   │   └── Scene5Outro.tsx             # 场景5：结尾 (12秒)
│   └── types/
│       └── video.ts              # 类型定义和常量
├── public/
│   └── images/                   # 图片素材（已复制）
├── package.json
├── remotion.config.ts
└── tsconfig.json
```

## 场景说明

### 场景1：开场引入（0:00-0:15）
**时长**：15秒（450帧）  
**内容**：
- 前3秒：核心卖点（本地 AI 搜索，隐私完全由你掌控）
- 3-6秒：开发者标语（100% AI 辅助开发的开源项目）
- 6-13秒：产品介绍
- 最后2秒：版本发布提示

### 场景2：版本演进回顾（0:15-0:50）
**时长**：35秒（1050帧）  
**内容**：
- 展示 v1.1.0 到 v1.9.0 共9个版本
- 每个版本展示3-4秒
- 文字卡片动画形式

### 场景3：UI 升级展示（0:50-2:10）【重点】
**时长**：80秒（2400帧）  
**内容**：
- v2.0.0 UI 视觉升级介绍
- 7个页面依次展示（搜索、文本、语音、图片、索引、设置、术语库）
- 每个页面约10秒展示
- 总结部分展示所有页面缩略图

### 场景4：技术架构回顾（2:10-2:18）
**时长**：8秒（240帧）  
**内容**：
- 对用户：技术栈介绍
- 对开发者：Vibe Coding 实践案例

### 场景5：结尾（2:18-2:30）
**时长**：12秒（360帧）  
**内容**：
- 用户行动号召
- 开发者行动号召
- GitHub 链接
- 二维码展示
- Made with ❤️ by dtsola

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm start
```

访问 http://localhost:3000 查看预览

### 渲染视频

```bash
# 渲染默认质量
npx remotion render ProductPromoV2 --output=./output/video.mp4

# 渲染高质量
npx remotion render ProductPromoV2 --output=./output/video-pro.mp4 --codec=h265 --crf=15
```

## 设计系统

### Notion 温暖明亮设计风格

```typescript
// 颜色系统
COLORS = {
  bgPrimary: '#ffffff',          // 主背景
  bgSecondary: '#f6f5f4',        // 次级背景
  textPrimary: 'rgba(0,0,0,0.95)',
  textSecondary: 'rgba(0,0,0,0.65)',
  brandBlue: '#0075de',          // 品牌蓝色
  borderStandard: 'rgba(0,0,0,0.1)',
}

// 字体系统
FONTS = {
  title: 64,
  subtitle: 48,
  heading: 36,
  body: 28,
  caption: 24,
}
```

## 受众定位

| 受众类型 | 关注点 | 对应场景 |
|----------|--------|----------|
| 工具用户 | 功能、隐私、易用性 | 场景 1、3、4、5 |
| Vibe Coding 开发者 | AI 辅助开发、开源、技术实现 | 场景 1、4、5 |

## 已复制图片素材

✅ 以下图片已从 `docs/产品文档/产品截图/` 复制到 `public/images/`：

- 小遥搜索.png
- 搜索界面-主界面.png
- 搜索界面-文本搜索.png
- 搜索界面-语音搜索.png
- 搜索界面-图片搜索.png
- 索引管理界面.png
- 设置界面.png
- 术语库管理界面.png
- 系统架构.png
- 开发者交流群图.png
- 用户交流群图.png

## 参考

- 视频脚本：[产品开源发布视频脚本-v2.0版本.md](../产品开源发布宣传文档-2.0版本.md)
- 1.0 版本项目：[video-project](../video-project/)
- Remotion 官方文档：https://www.remotion.dev/

---

<p align="center">
  <a href="https://github.com/remotion-dev/logo">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-dark.apng">
      <img alt="Animated Remotion Logo" src="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-light.gif">
    </picture>
  </a>
</p>
