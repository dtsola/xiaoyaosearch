# 小遥搜索代码架构设计

## 项目概述

小遥搜索采用前后端分离架构，前端使用Electron + Vue3构建跨平台桌面应用，后端使用Python + FastAPI提供AI驱动的搜索服务。项目结构清晰，职责分明，便于开发、测试和维护。

## 整体项目结构

```
xiaoyaosearch-new/
├── README.md                    # 项目说明文档
├── CHANGELOG.md                 # 版本更新日志
├── LICENSE                      # 开源协议
├── .gitignore                   # Git忽略文件
├── .env.example                 # 环境变量示例
├── docker-compose.yml           # 开发环境Docker配置
│
├── docs/                        # 项目文档
│   ├── prd.md                   # 产品需求文档
│   ├── tech-stack.md            # 技术选型文档
│   ├── system-process.md        # 系统流程文档
│   ├── ui.md                    # UI设计规范
│   ├── data-model.md            # 数据模型设计
│   ├── api.md                   # API接口文档
│   ├── code-arch.md             # 代码架构设计 ⬅
│   ├── deploy.md                # 部署指南
│   └── qa.md                    # 测试文档
│
├── frontend/                    # 前端代码 (Electron + Vue3)
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.ts           # Vite构建配置
│   ├── electron-builder.yml     # Electron打包配置
│   ├── tsconfig.json            # TypeScript配置
│   ├── src/                     # 源代码
│   │   ├── main/                # Electron主进程
│   │   │   ├── index.ts         # 主进程入口
│   │   │   ├── window.ts        # 窗口管理
│   │   │   ├── ipc.ts           # IPC通信处理
│   │   │   └── utils.ts         # 工具函数
│   │   ├── preload/             # 预加载脚本
│   │   │   └── index.ts         # 预加载脚本入口
│   │   └── renderer/            # 渲染进程 (Vue应用)
│   │       ├── main.ts          # Vue应用入口
│   │       ├── App.vue          # 根组件
│   │       ├── router/          # 路由配置
│   │       ├── stores/          # 状态管理 (Zustand)
│   │       ├── views/           # 页面组件
│   │       ├── components/      # 通用组件
│   │       ├── services/        # API服务
│   │       ├── utils/           # 工具函数
│   │       ├── types/           # TypeScript类型定义
│   │       └── assets/          # 静态资源
│   ├── dist/                    # 构建输出目录
│   └── build/                   # 构建脚本
│
├── backend/                     # 后端代码 (Python + FastAPI)
│   ├── pyproject.toml           # Python项目配置 (工具配置)
│   ├── requirements.txt         # 生产依赖
│   ├── requirements-dev.txt     # 开发依赖
│   ├── .env.example             # 环境变量示例
│   ├── alembic.ini              # 数据库迁移配置
│   ├── alembic_env.py           # Alembic环境配置
│   ├── setup_env.py             # 环境设置脚本
│   ├── setup.bat                # Windows快速设置脚本
│   ├── setup.sh                 # Unix快速设置脚本
│   ├── README.md                # 后端README文档
│   ├── main.py                  # FastAPI应用入口
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── deps.py              # 依赖注入
│   │   ├── v1/                  # API v1版本
│   │   │   ├── __init__.py
│   │   │   ├── api.py           # 路由汇总
│   │   │   └── endpoints/       # 具体端点
│   │   │       ├── __init__.py
│   │   │       ├── search.py
│   │   │       ├── files.py
│   │   │       ├── directories.py
│   │   │       ├── user_settings.py
│   │   │       └── tags.py
│   │   └── websocket.py         # WebSocket处理
│   ├── core/                    # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── config.py            # 应用配置
│   │   └── database.py          # 数据库配置
│   ├── db/                      # 数据库相关
│   │   ├── __init__.py
│   │   └── base.py              # 数据库基类
│   ├── models/                  # SQLAlchemy数据模型
│   │   ├── __init__.py
│   │   ├── file.py
│   │   ├── directory.py
│   │   ├── search_history.py
│   │   ├── user_settings.py
│   │   └── tag.py
│   ├── schemas/                 # Pydantic数据验证模型
│   │   ├── __init__.py
│   │   ├── file.py
│   │   ├── directory.py
│   │   ├── search.py
│   │   ├── user_settings.py
│   │   └── tag.py
│   ├── services/                # 业务服务层
│   │   └── __init__.py
│   ├── utils/                   # 工具函数
│   │   └── __init__.py
│   └── tests/                   # 测试代码
│       ├── __init__.py
│       ├── conftest.py          # pytest配置
│       ├── unit/                # 单元测试
│       └── integration/         # 集成测试
├── tools/                       # 开发工具和脚本
│   ├── build.py                 # 构建脚本
│   ├── dev.py                   # 开发服务器
│   ├── test.py                  # 测试脚本
│   └── release.py               # 发布脚本
│
├── resources/                   # 资源文件
│   ├── icons/                   # 应用图标
│   ├── images/                  # 图片资源
│   ├── ai-models/                  # AI模型文件 (可选)
│   └── locales/                 # 国际化文件
│       ├── zh-CN.json
│       └── en-US.json
│
└── openspec/                    # OpenSpec规范
    ├── project.md               # 项目配置
    ├── AGENTS.md                # 代理配置
    ├── specs/                   # 能力规范
    ├── changes/                 # 变更提案
    └── archive/                 # 归档文件
```

## 前端架构详细设计

### 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **语言**: TypeScript 5.3+
- **构建工具**: electron-vite 2.0+ (基于 Vite)
- **UI组件**: Ant Design Vue
- **状态管理**: Pinia (electron-vite 默认，可替换为 Zustand)
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios
- **桌面框架**: Electron 28.0+

### 目录结构详解

```
frontend/src/
├── main/                        # Electron主进程
│   └── index.ts                 # 主进程入口点 (electron-vite默认)
│       ├── 创建主窗口
│       ├── 管理应用生命周期
│       └── 启动后端服务
│   ├── window.ts                # 窗口管理 (新增)
│   │   ├── 创建和配置窗口
│   │   ├── 处理窗口事件
│   │   └── 窗口状态管理
│   ├── ipc.ts                   # IPC通信处理 (新增)
│   │   ├── 注册IPC处理器
│   │   ├── 处理前后端通信
│   │   └── 启动/监控后端进程
│   └── utils.ts                 # 主进程工具函数 (新增)
│       ├── 进程管理
│       ├── 文件系统操作
│       └── 系统信息获取
│
├── preload/                     # 预加载脚本
│   └── index.ts                 # 预加载脚本入口 (electron-vite默认)
│       ├── 暴露安全的API给渲染进程
│       ├── 封装Node.js功能
│       └── 类型安全的IPC通信
│
└── renderer/                    # 渲染进程 (Vue应用)
    └── src/                     # Vue应用源码 (electron-vite结构)
    ├── main.ts                  # Vue应用入口
    │   ├── 创建Vue应用实例
    │   ├── 注册全局插件
    │   └── 挂载应用
    ├── App.vue                  # 根组件
    │   ├── 应用布局
    │   ├── 全局状态初始化
    │   └── 路由视图
    ├── router/                  # 路由配置
    │   ├── index.ts             # 路由主配置
    │   │   ├── 定义路由规则
    │   │   ├── 配置路由守卫
    │   │   └── 路由元信息
    │   └── modules/             # 路由模块
    │       ├── search.ts        # 搜索页面路由
    │       ├── index.ts         # 索引管理路由
    │       ├── settings.ts      # 设置页面路由
    │       └── favorites.ts     # 收藏页面路由
    ├── stores/                  # 状态管理 (Zustand)
    │   ├── index.ts             # Store汇总
    │   ├── searchStore.ts       # 搜索状态
    │   │   ├── 搜索查询状态
    │   │   ├── 搜索结果状态
    │   │   └── 搜索历史状态
    │   ├── indexStore.ts        # 索引状态
    │   │   ├── 目录列表状态
    │   │   ├── 索引进度状态
    │   │   └── 索引配置状态
    │   ├── settingsStore.ts     # 设置状态
    │   │   ├── 用户配置状态
    │   │   ├── 应用设置状态
    │   │   └── 主题状态
    │   └── uiStore.ts           # UI状态
    │       ├── 侧边栏状态
    │       ├── 模态框状态
    │       └── 通知状态
    ├── views/                   # 页面组件
    │   ├── SearchPage.vue       # 搜索页面
    │   │   ├── 搜索输入组件
    │   │   ├── 结果展示组件
    │   │   └── 搜索过滤器
    │   ├── IndexPage.vue        # 索引管理页面
    │   │   ├── 目录管理组件
    │   │   ├── 索引进度组件
    │   │   └── 索引配置组件
    │   ├── SettingsPage.vue     # 设置页面
    │   │   ├── 搜索设置组件
    │   │   ├── 索引设置组件
    │   │   ├── AI设置组件
    │   │   └── 界面设置组件
    │   └── FavoritesPage.vue    # 收藏页面
    │       ├── 收藏列表组件
    │       ├── 收藏管理组件
    │       └── 标签管理组件
    ├── components/              # 通用组件
    │   ├── common/              # 通用基础组件
    │   │   ├── AppHeader.vue    # 应用头部
    │   │   ├── AppSidebar.vue   # 应用侧边栏
    │   │   ├── AppFooter.vue    # 应用底部
    │   │   └── LoadingSpinner.vue # 加载动画
    │   ├── search/              # 搜索相关组件
    │   │   ├── SearchInput.vue  # 搜索输入框
    │   │   ├── SearchFilters.vue # 搜索过滤器
    │   │   ├── SearchResults.vue # 搜索结果
    │   │   ├── ResultCard.vue   # 结果卡片
    │   │   └── SearchHistory.vue # 搜索历史
    │   ├── file/                # 文件相关组件
    │   │   ├── FileIcon.vue     # 文件图标
    │   │   ├── FilePreview.vue  # 文件预览
    │   │   ├── FileActions.vue  # 文件操作
    │   │   └── FileUploader.vue # 文件上传
    │   ├── index/               # 索引相关组件
    │   │   ├── DirectoryTree.vue # 目录树
    │   │   ├── IndexProgress.vue # 索引进度
    │   │   └── DirectoryConfig.vue # 目录配置
    │   └── ui/                  # UI组件
    │       ├── Modal.vue        # 模态框
    │       ├── Dropdown.vue     # 下拉菜单
    │       ├── TagSelector.vue  # 标签选择器
    │       └── Notification.vue # 通知组件
    ├── services/                # API服务
    │   ├── index.ts             # 服务汇总
    │   ├── api.ts               # API基础配置
    │   │   ├── Axios实例配置
    │   │   ├── 请求拦截器
    │   │   └── 响应拦截器
    │   ├── searchService.ts     # 搜索服务
    │   │   ├── 执行搜索
    │   │   ├── 获取建议
    │   │   └── 搜索历史
    │   ├── fileService.ts       # 文件服务
    │   │   ├── 文件信息获取
    │   │   ├── 文件预览
    │   │   └── 文件操作
    │   ├── indexService.ts      # 索引服务
    │   │   ├── 目录管理
    │   │   ├── 索引操作
    │   │   └── 索引状态
    │   ├── aiService.ts         # AI服务
    │   │   ├── 查询分析
    │   │   ├── 文件摘要
    │   │   └── 语音转文字
    │   └── systemService.ts     # 系统服务
    │       ├── 系统信息
    │       ├── 设置管理
    │       └── 系统操作
    ├── utils/                   # 工具函数
    │   ├── index.ts             # 工具函数汇总
    │   ├── format.ts            # 格式化工具
    │   │   ├── 文件大小格式化
    │   │   ├── 时间格式化
    │   │   └── 数字格式化
    │   ├── validation.ts        # 验证工具
    │   │   ├── 文件路径验证
    │   │   ├── URL验证
    │   │   └── 表单验证
    │   ├── storage.ts           # 存储工具
    │   │   ├── 本地存储
    │   │   ├── 缓存管理
    │   │   └── 设置持久化
    │   └── constants.ts         # 常量定义
    │       ├── API端点常量
    │       ├── 错误消息常量
    │       └── 应用常量
    ├── types/                   # TypeScript类型定义
    │   ├── index.ts             # 类型汇总
    │   ├── api.ts               # API相关类型
    │   │   ├── 请求参数类型
    │   │   ├── 响应数据类型
    │   │   └── 错误类型
    │   ├── search.ts            # 搜索相关类型
    │   │   ├── 查询类型
    │   │   ├── 结果类型
    │   │   └── 过滤器类型
    │   ├── file.ts              # 文件相关类型
    │   │   ├── 文件信息类型
    │   │   ├── 文件操作类型
    │   │   └── 文件预览类型
    │   ├── index.ts             # 索引相关类型
    │   │   ├── 目录类型
    │   │   ├── 索引状态类型
    │   │   └── 索引配置类型
    │   └── ui.ts                # UI相关类型
    │       ├── 组件属性类型
    │       ├── 状态类型
    │       └── 事件类型
    └── assets/                  # 静态资源
        ├── images/              # 图片资源
        ├── icons/               # 图标资源
        ├── styles/              # 样式文件
        │   ├── main.css         # 主样式
        │   ├── variables.css    # CSS变量
        │   └── components.css   # 组件样式
        └── fonts/               # 字体文件
```

### 前端架构特点

1. **模块化设计**: 按功能模块组织代码，职责清晰
2. **TypeScript全覆盖**: 提供类型安全和更好的开发体验
3. **组合式API**: 使用Vue3的Composition API，提高代码复用性
4. **electron-vite架构**: 统一的构建工具支持主进程、预加载脚本和渲染进程
5. **状态管理灵活**: 默认使用Pinia，可替换为Zustand等轻量级方案
6. **服务层抽象**: API服务与UI组件解耦
7. **组件化开发**: 可复用的Vue组件库
8. **工具函数封装**: 常用功能模块化
9. **类型定义完整**: 前后端共享类型定义
10. **优化的构建流程**: electron-vite 提供更快的构建和热重载体验

## 后端架构详细设计

### 技术栈

- **框架**: FastAPI 0.104+
- **语言**: Python 3.11+
- **异步**: asyncio + uvicorn
- **数据库ORM**: SQLAlchemy 2.0+ (异步)
- **数据验证**: Pydantic 2.5+
- **数据库迁移**: Alembic
- **测试**: pytest + pytest-asyncio
- **AI/ML**: PyTorch, Transformers, FlagEmbedding
- **向量搜索**: Faiss
- **全文搜索**: Whoosh
- **文件处理**: Marker, FastWhisper, PaddleOCR

### 目录结构详解

```
backend/src/
├── main.py                      # FastAPI应用入口
│   ├── 创建FastAPI应用实例
│   ├── 配置中间件
│   ├── 注册路由
│   ├── 异常处理器
│   └── 启动事件
│
├── config/                      # 配置管理
│   ├── settings.py              # 应用配置
│   │   ├── 数据库配置
│   │   ├── AI模型配置
│   │   ├── 日志配置
│   │   └── 性能配置
│   └── logging.py               # 日志配置
│       ├── 日志格式设置
│       ├── 日志级别配置
│       └── 日志输出配置
│
├── api/                         # API路由层
│   ├── deps.py                  # 依赖注入
│   │   ├── 数据库会话
│   │   ├── 用户认证 (预留)
│   │   ├── 请求验证
│   │   └── 错误处理
│   ├── v1/                      # API v1版本
│   │   ├── router.py            # 路由汇总
│   │   │   ├── 搜索相关路由
│   │   │   ├── 文件相关路由
│   │   │   ├── 索引相关路由
│   │   │   ├── AI相关路由
│   │   │   ├── 设置相关路由
│   │   │   └── 系统相关路由
│   │   └── endpoints/           # 具体端点
│   │       ├── search.py        # 搜索端点
│   │       │   ├── POST /search  # 执行搜索
│   │       │   ├── GET /suggestions # 搜索建议
│   │       │   └── GET /history # 搜索历史
│   │       ├── files.py         # 文件端点
│   │       │   ├── GET /files/{id} # 获取文件信息
│   │       │   ├── GET /files/{id}/preview # 文件预览
│   │       │   ├── POST /files/{id}/actions # 文件操作
│   │       │   └── GET /files/{id}/download # 文件下载
│   │       ├── index.py         # 索引端点
│   │       │   ├── POST /directories # 添加目录
│   │       │   ├── GET /directories # 目录列表
│   │       │   ├── POST /rebuild # 重建索引
│   │       │   └── GET /status # 索引状态
│   │       ├── ai.py            # AI端点
│   │       │   ├── POST /query-analysis # 查询分析
│   │       │   ├── POST /summarize # 文件摘要
│   │       │   ├── POST /speech-to-text # 语音转文字
│   │       │   └── POST /image-analysis # 图片分析
│   │       ├── settings.py      # 设置端点
│   │       │   ├── GET /settings # 获取设置
│   │       │   ├── PUT /settings # 更新设置
│   │       │   └── POST /reset # 重置设置
│   │       └── system.py        # 系统端点
│   │           ├── GET /info # 系统信息
│   │           ├── GET /health # 健康检查
│   │           └── POST /cleanup # 系统清理
│   └── websocket.py             # WebSocket处理
│       ├── 实时搜索结果推送
│       ├── 索引进度推送
│       └── 系统通知推送
│
├── core/                        # 核心业务逻辑
│   ├── search/                  # 搜索引擎
│   │   ├── engine.py            # 搜索引擎主逻辑
│   │   │   ├── 多模态搜索协调
│   │   │   ├── 查询处理流程
│   │   │   └── 结果排序策略
│   │   ├── query_parser.py      # 查询解析
│   │   │   ├── 查询预处理
│   │   │   ├── AI查询理解
│   │   │   └── 查询意图识别
│   │   ├── retrievers/          # 检索器
│   │   │   ├── vector_retriever.py # 向量检索
│   │   │   ├── text_retriever.py   # 全文检索
│   │   │   └── hybrid_retriever.py # 混合检索
│   │   ├── result_fusion.py     # 结果融合
│   │   │   ├── RRF算法实现
│   │   │   ├── 权重调整
│   │   │   └── 结果去重
│   │   └── highlighter.py       # 结果高亮
│   │       ├── 关键词高亮
│   │       ├── 片段提取
│   │       └── 摘要生成
│   │
│   ├── indexing/                # 索引管理
│   │   ├── manager.py           # 索引管理器
│   │   │   ├── 索引创建和更新
│   │   │   ├── 索引优化和合并
│   │   │   └── 索引状态监控
│   │   ├── scanner.py           # 文件扫描器
│   │   │   ├── 递归目录扫描
│   │   │   ├── 文件变更检测
│   │   │   └── 文件类型过滤
│   │   ├── processor.py         # 文件处理器
│   │   │   ├── 多格式文件处理
│   │   │   ├── 内容提取和清理
│   │   │   └── 文本分块策略
│   │   ├── file_handlers/       # 文件处理器
│   │   │   ├── document_handler.py # 文档处理器
│   │   │   ├── image_handler.py    # 图片处理器
│   │   │   ├── audio_handler.py    # 音频处理器
│   │   │   └── video_handler.py    # 视频处理器
│   │   └── monitor.py           # 文件监控器
│   │       ├── 实时文件监控
│   │       ├── 增量索引更新
│   │       └── 事件去抖处理
│   │
│   ├── ai/                      # AI服务
│   │   ├── llm.py               # LLM服务
│   │   │   ├── Ollama本地模型
│   │   │   ├── OpenAI云端模型
│   │   │   └── 模型切换和缓存
│   │   ├── embedding.py         # 嵌入服务
│   │   │   ├── BGE模型加载
│   │   │   ├── 文本向量化
│   │   │   └── 批量处理优化
│   │   ├── asr.py               # 语音识别
│   │   │   ├── FastWhisper集成
│   │   │   ├── 多语言支持
│   │   │   └── 音频预处理
│   │   ├── vision.py            # 视觉理解
│   │   │   ├── CN-CLIP模型
│   │   │   ├── 图像标签生成
│   │   │   └── OCR文本识别
│   │   └── model_manager.py     # 模型管理
│   │       ├── 模型下载和缓存
│   │       ├── 模型加载和卸载
│   │       └── GPU内存管理
│   │
│   ├── storage/                 # 数据存储
│   │   ├── database.py          # 数据库操作
│   │   │   ├── SQLAlchemy配置
│   │   │   ├── 异步会话管理
│   │   │   └── 事务处理
│   │   ├── vector_store.py      # 向量存储
│   │   │   ├── Faiss索引管理
│   │   │   ├── 向量CRUD操作
│   │   │   └── 索引优化
│   │   ├── text_store.py        # 文本存储
│   │   │   ├── Whoosh索引管理
│   │   │   ├── 全文搜索操作
│   │   │   └── 索引更新
│   │   └── cache.py             # 缓存管理
│   │       ├── 内存缓存
│   │       ├── LRU策略
│   │       └── 缓存失效
│   │
│   └── models/                  # 数据模型
│       ├── database.py          # SQLAlchemy模型
│       │   ├── File模型
│       │   ├── Directory模型
│       │   ├── SearchHistory模型
│       │   ├── UserSettings模型
│       │   └── SystemLog模型
│       ├── schemas.py           # Pydantic模型
│       │   ├── 请求模型
│       │   ├── 响应模型
│       │   ├── 配置模型
│       │   └── 验证模型
│       └── enums.py             # 枚举定义
│           ├── 文件类型枚举
│           ├── 索引状态枚举
│           ├── 日志级别枚举
│           └── 搜索模式枚举
│
├── services/                    # 业务服务层
│   ├── file_service.py          # 文件服务
│   │   ├── 文件CRUD操作
│   │   ├── 文件预览生成
│   │   ├── 文件操作封装
│   │   └── 文件权限检查
│   ├── search_service.py        # 搜索服务
│   │   ├── 搜索请求处理
│   │   ├── 搜索结果格式化
│   │   ├── 搜索历史管理
│   │   └── 搜索建议生成
│   ├── index_service.py         # 索引服务
│   │   ├── 目录管理
│   │   ├── 索引任务调度
│   │   ├── 索引进度监控
│   │   └── 索引统计收集
│   ├── ai_service.py            # AI服务
│   │   ├── AI任务处理
│   │   ├── 模型服务调用
│   │   ├── 结果缓存管理
│   │   └── 性能监控
│   └── system_service.py        # 系统服务
│       ├── 系统信息收集
│       ├── 配置管理
│       ├── 日志管理
│       └── 健康检查
│
├── utils/                       # 工具函数
│   ├── file_utils.py            # 文件工具
│   │   ├── 文件路径处理
│   │   ├── 文件类型检测
│   │   ├── 文件哈希计算
│   │   └── 文件系统操作
│   ├── text_utils.py            # 文本工具
│   │   ├── 文本预处理
│   │   ├── 中文分词
│   │   ├── 文本清理
│   │   └── 关键词提取
│   ├── crypto_utils.py          # 加密工具
│   │   ├── 数据加密解密
│   │   ├── 哈希计算
│   │   └── 密钥管理
│   ├── validation.py            # 数据验证
│   │   ├── 输入验证
│   │   ├── 文件路径验证
│   │   └── 配置验证
│   └── performance.py           # 性能工具
│       ├── 执行时间监控
│       ├── 内存使用监控
│       └── 性能指标收集
│
└── workers/                     # 后台任务
    ├── index_worker.py          # 索引任务
    │   ├── 异步文件处理
    │   ├── 批量索引更新
    │   └── 错误重试机制
    ├── cleanup_worker.py        # 清理任务
    │   ├── 临时文件清理
    │   ├── 缓存清理
    │   └── 日志轮转
    └── base_worker.py           # 任务基类
        ├── 任务队列管理
        ├── 并发控制
        └── 任务监控
```

### 后端架构特点

1. **分层架构**: API层、服务层、核心逻辑层分离
2. **异步编程**: 全面使用asyncio，提高并发性能
3. **模块化设计**: 按功能域组织代码
4. **依赖注入**: 使用FastAPI的依赖注入系统
5. **数据验证**: 使用Pydantic进行强类型验证
6. **错误处理**: 统一的异常处理机制
7. **测试友好**: 易于单元测试和集成测试
8. **扩展性**: 支持插件式功能扩展

## 前后端约定

### 简单的约定方式

前后端各自维护自己的类型定义和常量，通过API文档确保数据格式一致性：

#### 前端类型定义
```
frontend/src/types/
├── search.ts                    # 搜索相关类型
├── file.ts                      # 文件相关类型
├── api.ts                       # API接口类型
├── index.ts                     # 统一导出
└── constants/                   # 常量定义
    ├── file-types.ts
    ├── error-codes.ts
    └── api-endpoints.ts
```

#### 后端类型定义
```
backend/src/models/
├── schemas.py                   # Pydantic数据模型
├── enums.py                     # 枚举定义
└── constants.py                 # 常量定义
```

#### API文档作为唯一约束
- 所有数据格式以 `docs/api.md` API文档为准
- 后端按照API文档实现Pydantic模型
- 前端按照API文档定义TypeScript接口
- 开发时参考API文档确保一致性

## 开发工作流

### 开发环境启动

1. **后端开发服务器**:
```bash
cd backend
# 自动设置环境
python setup_env.py  # 或使用 setup.bat (Windows) / setup.sh (Unix)
# 或手动设置
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Linux/macOS
pip install -r requirements.txt
uvicorn main:app --reload  # 启动开发服务器
```

2. **前端Electron开发服务器**:
```bash
cd frontend
npm install     # 安装依赖
npm run dev     # 启动electron-vite开发模式 (同时启动渲染进程和Electron)
```

3. **分步启动 (可选)**:
```bash
# 仅启动渲染进程开发服务器
cd frontend
npm run dev:renderer

# 在另一个终端启动Electron主进程
npm run dev:electron
```

### 代码规范

1. **前端代码规范**:
   - ESLint + Prettier代码格式化
   - TypeScript严格模式
   - Vue3组合式API规范
   - 组件命名 PascalCase
   - 文件命名 kebab-case

2. **后端代码规范**:
   - Black代码格式化
   - mypy类型检查
   - flake8代码检查
   - PEP 8编码规范
   - 文档字符串规范

### 测试策略

1. **前端测试**:
   - Jest单元测试
   - Vue Test Utils组件测试
   - Cypress端到端测试
   - 测试覆盖率 > 80%

2. **后端测试**:
   - pytest单元测试
   - pytest-asyncio异步测试
   - API集成测试
   - 性能测试和压力测试

### 构建和部署

1. **前端构建**:
```bash
cd frontend
npm run build     # 构建生产版本 (包含类型检查和Electron打包)
npm run build:win  # 构建Windows版本
npm run build:mac  # 构建macOS版本
npm run build:linux # 构建Linux版本
npm run build:unpack # 仅构建不打包
```

2. **后端打包**:
```bash
cd backend
pyinstaller --onefile src/main.py  # 打包成可执行文件
```

3. **发布流程**:
   - 代码审查
   - 自动化测试
   - 构建打包
   - 签名和公证
   - 发布到各平台

这个代码架构设计为小遥搜索提供了清晰、可扩展、易维护的开发基础，支持快速迭代和功能扩展。