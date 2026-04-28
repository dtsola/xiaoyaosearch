/**
 * v2.0 视频类型定义
 * Notion 温暖明亮设计风格
 */

// 视频配置常量
export const VIDEO_CONFIG = {
  fps: 30,
  width: 1920,
  height: 1080,
} as const;

// Notion 温暖明亮设计配色
export const COLORS = {
  // 主背景
  bgPrimary: '#ffffff',
  bgSecondary: '#f6f5f4',

  // 文字
  textPrimary: 'rgba(0,0,0,0.95)',
  textSecondary: 'rgba(0,0,0,0.65)',
  textTertiary: 'rgba(0,0,0,0.45)',

  // 品牌色
  brandBlue: '#0075de',
  brandBlueHover: '#0062b8',

  // 边框
  borderStandard: 'rgba(0,0,0,0.1)',
  borderLight: 'rgba(0,0,0,0.06)',

  // 功能色
  success: '#52c41a',
  warning: '#faad14',
  error: '#ff4d4f',

  // 渐变
  gradientStart: '#ffffff',
  gradientEnd: '#f6f5f4',
} as const;

// 字体配置
export const FONTS = {
  title: 64,        // 大标题
  subtitle: 48,     // 副标题
  heading: 36,      // 小标题
  body: 28,         // 正文
  caption: 24,      // 说明文字
  code: 20,         // 代码
} as const;

// 间距配置
export const SPACING = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  xxl: 64,
} as const;

// 圆角配置
export const RADIUS = {
  sm: 4,
  md: 6,
  lg: 10,
  xl: 12,
  full: 9999,
} as const;

// 阴影配置
export const SHADOWS = {
  card: '0 1px 2px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.04)',
  elevated: '0 2px 4px rgba(0,0,0,0.05), 0 4px 8px rgba(0,0,0,0.05)',
} as const;

// 版本历史数据
export const VERSION_HISTORY = [
  { version: 'v1.1.0', date: '2026-02-28', feature: '国际化支持，中英文双语界面' },
  { version: 'v1.2.0', date: '2026-03-05', feature: '插件化架构，语雀知识库数据源' },
  { version: 'v1.3.0', date: '2026-03-10', feature: '云端大模型，OpenAI/DeepSeek/阿里云' },
  { version: 'v1.4.0', date: '2026-03-15', feature: 'MCP 服务器，融入 Claude 生态' },
  { version: 'v1.5.0', date: '2026-03-20', feature: 'Agent Skills，AI 助手工具调用' },
  { version: 'v1.6.0', date: '2026-03-26', feature: '云端嵌入模型，搜索质量提升' },
  { version: 'v1.7.0', date: '2026-03-31', feature: '飞书文档支持' },
  { version: 'v1.8.0', date: '2026-04-08', feature: '钉钉文档支持' },
  { version: 'v1.9.0', date: '2026-04-12', feature: '术语库系统，召回率提升 60%' },
] as const;

// UI 展示页面数据
export const UI_PAGES = [
  { name: '搜索首页', image: '搜索界面-主界面.png', desc: '居中布局，多模态指示器' },
  { name: '文本搜索', image: '搜索界面-文本搜索.png', desc: '实时结果展示，匹配度高亮' },
  { name: '语音搜索', image: '搜索界面-语音搜索.png', desc: '30秒内语音录制，自动转文字' },
  { name: '图片搜索', image: '搜索界面-图片搜索.png', desc: '上传图片即可搜索，AI理解图像' },
  { name: '索引管理', image: '索引管理界面.png', desc: '实时状态监控，一键重建索引' },
  { name: '设置页面', image: '设置界面.png', desc: 'AI模型配置，多模态管理' },
  { name: '术语库管理', image: '术语库管理界面.png', desc: '多术语库集合，同义词扩展' },
] as const;

// 技术栈数据
export const TECH_STACK = {
  frontend: ['Electron', 'Vue 3', 'TypeScript', 'Ant Design Vue', 'Lucide Icons'],
  backend: ['Python', 'FastAPI', 'Uvicorn'],
  ai: ['BGE-M3', 'FasterWhisper', 'CN-CLIP', 'Ollama'],
  search: ['Faiss', 'Whoosh'],
  database: ['SQLite'],
} as const;
