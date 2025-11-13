# 小遥搜索项目上下文

## 项目目的
构建一个跨平台的本地文件智能搜索工具，通过AI多模态理解能力，实现文本、语音、图片、视频等多种文件的语义化检索，提升个人知识管理效率。

## 整体项目结构

```
xiaoyaosearch/
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
│   ├── code-arch.md             # 代码架构设计
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
│   ├── pyproject.toml           # Python项目配置
│   ├── requirements.txt         # 生产依赖
│   ├── requirements-dev.txt     # 开发依赖
│   ├── .env.example             # 环境变量示例
│   ├── alembic.ini              # 数据库迁移配置
│   ├── main.py                  # FastAPI应用入口
│   ├── api/                     # API路由
│   │   ├── deps.py              # 依赖注入
│   │   ├── v1/                  # API v1版本
│   │   │   ├── api.py           # 路由汇总
│   │   │   └── endpoints/       # 具体端点
│   │   │       ├── search.py
│   │   │       ├── files.py
│   │   │       ├── directories.py
│   │   │       ├── user_settings.py
│   │   │       └── tags.py
│   │   └── websocket.py         # WebSocket处理
│   ├── core/                    # 核心业务逻辑
│   │   ├── config.py            # 应用配置
│   │   └── database.py          # 数据库配置
│   ├── db/                      # 数据库相关
│   │   └── base.py              # 数据库基类
│   ├── models/                  # SQLAlchemy数据模型
│   │   ├── file.py
│   │   ├── directory.py
│   │   ├── search_history.py
│   │   ├── user_settings.py
│   │   └── tag.py
│   ├── schemas/                 # Pydantic数据验证模型
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
│   ├── models/                  # AI模型文件 (可选)
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

## 技术栈
### 前端
- **框架**: Vue 3.4+ (Composition API)
- **语言**: TypeScript 5.3+
- **构建工具**: electron-vite 2.0+ (基于 Vite)
- **UI组件**: Ant Design Vue (待集成)
- **状态管理**: Zustand 4.4+ (或使用 Pinia)
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios
- **桌面框架**: Electron 28.0+

### 后端
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

### AI模型
- **文本嵌入**: BGE (BAAI General Embedding)
- **语音识别**: FastWhisper
- **图像理解**: Chinese-CLIP
- **大语言模型**: Ollama (本地) / OpenAI (云端)

## 前端架构详细设计

### 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **语言**: TypeScript 5.3+
- **构建工具**: electron-vite 2.0+ (基于 Vite)
- **UI组件**: Ant Design Vue (待集成)
- **状态管理**: Zustand (electron-vite 默认，可替换为 Zustand)
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios
- **桌面框架**: Electron 28.0+

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

### 项目规范

### 代码风格
#### 前端
- ESLint + Prettier代码格式化
- TypeScript严格模式
- Vue3组合式API规范
- 组件命名 PascalCase
- 文件命名 kebab-case

#### 后端
- Black代码格式化
- mypy类型检查
- flake8代码检查
- PEP 8编码规范
- 文档字符串规范

### 架构模式
- **前后端分离**: Electron + FastAPI架构
- **分层架构**: API层、服务层、核心逻辑层分离
- **模块化设计**: 按功能域组织代码
- **依赖注入**: 使用FastAPI的依赖注入系统
- **数据验证**: 使用Pydantic进行强类型验证

### 测试策略
#### 前端测试
- Jest单元测试
- Vue Test Utils组件测试
- Cypress端到端测试
- 测试覆盖率 > 80%

#### 后端测试
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

### Git工作流
- **分支策略**: GitFlow (main, develop, feature/*, hotfix/*)
- **提交规范**: Conventional Commits
- **代码审查**: 所有PR必须经过审查
- **自动化**: CI/CD pipeline自动测试和构建

## 领域上下文
小遥搜索是一个AI驱动的个人知识管理工具，专注于：
- **多模态搜索**: 支持文本、语音、图像输入
- **语义理解**: 理解查询意图，非精确匹配
- **本地优先**: 所有数据存储在用户本地，保护隐私
- **跨平台**: 支持Windows、Mac、Linux
- **实时索引**: 监控文件变化，增量更新索引

## 重要约束
- **隐私保护**: 所有数据存储在用户本地，不上传到云端
- **性能要求**: 支持1万文件规模，搜索响应时间<1秒
- **资源限制**: 内存使用<2GB，磁盘占用<10GB
- **跨平台兼容**: 必须在Windows、Mac、Linux上运行
- **离线工作**: 核心功能必须支持离线使用

## 外部依赖
- **AI模型**: 需要下载BGE、Whisper、Chinese-CLIP模型
- **系统工具**: LibreOffice (文档转换)、FFmpeg (音视频处理)
- **Python包**: 通过PyPI管理
- **Node.js包**: 通过npm管理
- **可选云服务**: OpenAI API (可选的云端LLM服务)
