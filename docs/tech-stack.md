# 小遥搜索技术选型文档

## 整体架构图

```mermaid
graph TB
    subgraph "客户端层 (Client Layer)"
        A[Electron 桌面应用<br/>跨平台支持]
        A --> B[Vue3 + TypeScript + Ant Design 5]
        B --> C[搜索界面]
        B --> D[结果展示]
        B --> E[设置管理]
        B --> F[文件预览]
        B --> G[状态管理: Zustand + React Query]
    end

    A --> H[IPC通信]

    subgraph "Electron Main Process"
        I[窗口管理]
        J[文件系统访问]
        K[进程管理]
        L[系统托盘]
    end

    H --> M[HTTP/WebSocket]

    subgraph "后端服务层 (Backend Layer)"
        N[FastAPI 服务<br/>Python 3.10+]
        N --> O[API路由层<br/>/search /index /files /settings /ai]
        N --> P[业务逻辑层<br/>搜索引擎 | 索引管理 | 用户管理 | 文件管理]
    end

    M --> N

    subgraph "AI服务层 (AI Service Layer)"
        Q[LLM服务<br/>Ollama(本地) | OpenAI(云端)]
        R[ASR服务<br/>Whisper(本地) | 云端API]
        S[视觉服务<br/>CN-CLIP(本地) | GPT-4V(云端)]
        T[Embedding服务<br/>BGE(本地)]
    end

    N --> Q
    N --> R
    N --> S
    N --> T

    subgraph "数据存储层 (Storage Layer)"
        U[向量索引<br/>Faiss .index]
        V[全文索引<br/>Whoosh 索引目录]
        W[元数据库<br/>SQLite .db]
        X[文件系统<br/>本地文件]
    end

    N --> U
    N --> V
    N --> W
    N --> X
```

## 技术选型详情

### 前端技术栈

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Electron** | 28.0+ | 跨平台桌面应用框架 | 成熟的跨平台方案，支持Web技术栈，丰富的原生API |
| **Vue3** | 3.4+ | UI框架 | 渐进式框架，组合式API，优秀性能和开发体验 |
| **TypeScript** | 5.3+ | 类型安全 | 提供强类型支持，减少运行时错误，提高代码质量 |
| **electron-vite** | 2.0+ | 构建工具 | 专为Electron优化的构建工具，统一的开发体验 |
| **Ant Design Vue** | 4.1+ | UI组件库 | 企业级UI设计语言，丰富的组件，完善的文档，自动导入支持 |
| **Pinia** | 2.1+ | 状态管理 | Vue官方推荐，与Vue3完美集成，electron-vite默认 |
| **Zustand** | 4.4+ | 备选状态管理 | 轻量级状态管理，简洁API，TypeScript友好 |
| **Vue Router** | 4.2+ | 路由管理 | Vue官方路由，TypeScript支持良好 |
| **Axios** | 1.6+ | HTTP客户端 | Promise based HTTP client，支持请求拦截和响应处理 |

### 后端技术栈

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Python** | 3.11+ | 后端语言 | 丰富的AI/ML生态，简洁的语法，强大的社区支持 |
| **FastAPI** | 0.104+ | Web框架 | 现代Python框架，自动API文档，高性能异步支持 |
| **Uvicorn** | 0.24+ | ASGI服务器 | 高性能ASGI服务器，支持HTTP/2和WebSocket |
| **Pydantic** | 2.5+ | 数据验证 | 类型安全的数据验证，与FastAPI深度集成 |
| **SQLAlchemy** | 2.0+ | ORM | 强大的Python SQL工具包，支持异步操作 |
| **Alembic** | 1.13+ | 数据库迁移 | SQLAlchemy的数据库迁移工具 |
| **asyncio** | 3.11+ | 异步任务处理 | Python内置异步框架，处理文件处理和索引任务 |

### AI/ML技术栈

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **PyTorch** | 2.1+ | 深度学习框架 | 动态计算图，易用性，丰富的预训练模型 |
| **Transformers** | 4.36+ | HuggingFace模型库 | 最全面的预训练模型库，易用的API |
| **FlagEmbedding** | 1.2+ | BGE Embedding模型 | 中文语义搜索最佳选择，高性能 |
| **FastWhisper** | 0.10+ | 语音识别模型 | Whisper的优化版本，更快的推理速度，多语言支持 |
| **CN-CLIP** | 1.5+ | 中文视觉理解模型 | 中文图像-文本预训练模型，本地部署 |
| **Sentence Transformers** | 2.2+ | 句子嵌入 | 简化BERT等模型用于句子级别的嵌入 |
| **OpenCV** | 4.8+ | 图像处理 | 强大的计算机视觉库，支持多种图像格式 |
| **Pillow** | 10.1+ | 图像处理 | Python图像处理库，支持多种图像格式 |

### 检索与存储技术

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Faiss** | 1.7.4 | 向量检索引擎 | Facebook开源，高性能相似性搜索 |
| **Whoosh** | 2.7.4 | 全文检索引擎 | 纯Python全文索引库，轻量级 |
| **SQLite** | 3.45+ | 嵌入式关系数据库 | 无服务器，零配置，适合桌面应用 |

### 文件处理技术

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Marker** | 0.2+ | PDF转Markdown | 高质量PDF转换，保持格式和结构 |
| **LibreOffice** | 7.6+ | Office文档转PDF | 开源办公套件，支持Word/Excel/PPT统一转PDF |
| **PaddleOCR** | 2.7+ | 中文OCR | 百度开源，支持多种语言，高精度识别 |
| **FFmpeg** | 6.1+ | 音视频处理 | 音视频处理的瑞士军刀，格式转换和元数据提取 |
| **watchdog** | 3.0+ | 文件系统监控 | 跨平台文件系统事件监控库 |

### 开发与部署工具

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Poetry** | 1.7+ | Python依赖管理 | 现代Python包管理，锁文件支持 |
| **pytest** | 7.4+ | 测试框架 | 功能丰富的测试框架，插件丰富 |
| **pytest-asyncio** | 0.21+ | 异步测试 | pytest的异步测试支持 |
| **black** | 23.11+ | 代码格式化 | Python代码格式化工具 |
| **ruff** | 0.1+ | 代码检查 | 极快的Python代码检查和格式化工具 |
| **mypy** | 1.7+ | 类型检查 | Python静态类型检查器 |
| **ESLint** | 8.55+ | JavaScript/TypeScript代码检查 | 可配置的代码检查工具 |
| **Prettier** | 3.1+ | 代码格式化 | 统一代码格式化工具 |
| **electron-builder** | 24.9+ | 前端应用打包 | Electron应用打包和分发工具，与electron-vite集成 |
| **PyInstaller** | 6.2+ | 后端应用打包 | Python应用打包成可执行文件，跨平台支持 |

### 测试技术

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Jest** | 29.7+ | 前端测试框架 | 零配置测试框架，优秀的快照测试 |
| **Vue Test Utils** | 2.4+ | Vue组件测试 | Vue官方测试工具库 |
| **Cypress** | 13.6+ | E2E测试 | 现代端到端测试框架 |
| **Playwright** | 1.40+ | E2E测试 | 跨浏览器自动化测试 |
| **locust** | 2.17+ | 性能测试 | Python负载测试工具 |

## 安全与隐私技术

| 技术 | 作用 | 选型理由 |
|------|------|----------|
| **bcrypt** | 密码哈希 | 安全的密码哈希算法 |
| **cryptography** | 加密 | Python加密库，支持多种算法 |
| **keyring** | 敏感信息存储 | 安全存储密钥和密码 |
| **pycryptodome** | 数据加密 | 强大的Python加密库 |
| **TLS/SSL** | 通信加密 | HTTPS和WebSocket安全通信 |

## 监控与日志技术

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **Loguru** | 0.7+ | 日志记录 | 简单易用的Python日志库 |
| **structlog** | 23.2+ | 结构化日志 | 结构化日志记录，支持JSON格式 |
| **psutil** | 5.9+ | 系统监控 | 跨平台系统和进程监控库 |
| **prometheus-client** | 0.19+ | 指标收集 | Prometheus Python客户端 |
| **sentry-sdk** | 1.38+ | 错误监控 | 应用错误监控和性能分析 |

## 配置管理技术

| 技术 | 版本 | 作用 | 选型理由 |
|------|------|------|----------|
| **pydantic-settings** | 2.1+ | 配置管理 | 基于Pydantic的配置管理 |
| **python-dotenv** | 1.0+ | 环境变量管理 | 从.env文件加载环境变量 |
| **PyYAML** | 6.0+ | YAML配置 | Python YAML解析器 |

## 性能优化技术

| 技术 | 作用 | 选型理由 |
|------|------|----------|
| **lru-dict** | LRU缓存 | 高性能LRU缓存实现 |
| **orjson** | JSON序列化 | 高性能JSON序列化 |
| **ujson** | JSON序列化 | 超快的JSON编码器/解码器 |
| **aiofiles** | 异步文件IO | 异步文件操作支持 |
| **asyncio** | 异步编程 | Python异步编程支持 |

## 数据存储路径结构

```
~/.ai-search/
├── data.db              (SQLite元数据数据库)
├── faiss.index          (Faiss向量索引文件)
├── faiss.index.map      (向量ID映射文件)
├── whoosh_index/        (Whoosh全文索引目录)
│   ├── MAIN_0/          (主索引段)
│   ├── _toc.txt         (索引目录)
│   └── ...              (其他索引文件)
├── cache/               (缓存目录)
│   ├── embeddings/      (嵌入向量缓存)
│   ├── transcriptions/  (音频转录缓存)
│   └── previews/        (文件预览缓存)
├── models/              (本地AI模型目录)
│   ├── bge-base/        (BGE嵌入模型)
│   ├── whisper/         (Whisper语音模型)
│   └── cn-clip/         (CN-CLIP视觉模型)
├── logs/                (日志目录)
│   ├── app.log          (应用日志)
│   ├── search.log       (搜索日志)
│   └── index.log        (索引日志)
├── config/              (配置文件目录)
│   ├── app.yaml         (应用配置)
│   └── user.yaml        (用户配置)
└── temp/                (临时文件目录)
```

## 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最小8GB，推荐16GB+
- **存储**: 最小10GB可用空间，推荐50GB+
- **GPU**: 支持CUDA的NVIDIA GPU (可选，用于AI加速)

### 运行时要求
- **Python**: 3.11+
- **Node.js**: 18.0+
- **npm/yarn**: 最新版本
- **Git**: 2.0+

### AI模型要求
- **CPU模式**: 需要较强的CPU性能，推荐8核+
- **GPU模式**: 需要CUDA兼容的GPU，推荐8GB+显存
- **内存**: 加载所有模型需要约8-12GB内存

## 开发环境配置

### 前端开发环境 (electron-vite)
```bash
# 安装依赖
npm install
# 开发模式 (同时启动渲染进程和Electron)
npm run dev
# 分步启动 (可选)
npm run dev:renderer  # 仅启动渲染进程
npm run dev:electron   # 仅启动Electron主进程
# 类型检查
npm run typecheck
# 代码格式化
npm run format
# 代码检查
npm run lint
# 测试
npm run test
```

### 后端开发环境
```bash
# 安装poetry (如果未安装)
curl -sSL https://install.python-poetry.org | python3 -
# 安装依赖
poetry install
# 激活虚拟环境
poetry shell
# 开发模式
uvicorn app.main:app --reload
# 测试
pytest
# 代码格式化
black .
# 类型检查
mypy .
```

## 部署配置

### 构建配置
- **前端**: electron-vite构建，优化资源压缩，统一的开发体验
- **后端**: PyInstaller打包，包含所有依赖
- **整体打包**: electron-builder，与electron-vite集成，支持多平台

### 安装包结构
- **Windows**:
  - 前端: `xiaoyaosearch.exe` (Electron应用)
  - 后端: `xiaoyaosearch-server.exe` (PyInstaller打包)
- **macOS**:
  - 前端: `小遥搜索.app` (Electron应用)
  - 后端: `xiaoyaosearch-server` (Mac可执行文件)
- **Linux**:
  - 前端: `xiaoyaosearch` (Electron应用)
  - 后端: `xiaoyaosearch-server` (Linux可执行文件)

### 部署架构
- **前后端分离**: 前端Electron应用调用本地后端服务
- **本地服务**: 后端以HTTP API形式运行在localhost
- **进程管理**: 前端负责启动和监控后端进程
- **端口管理**: 自动分配可用端口，避免冲突

### 自动更新
- **Windows**: NSIS更新机制，分别更新前后端
- **macOS**: Sparkle更新框架，支持增量更新
- **Linux**: AppImage更新机制或包管理器更新
