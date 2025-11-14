# 小遥搜索 (Xiaoyao Search)

一个AI驱动的跨平台桌面搜索应用程序，为个人用户提供本地文件的智能搜索能力。

## 功能特性

### 🔍 多模态搜索
- **文本搜索**: 支持自然语言查询，理解语义而非仅关键词匹配
- **语音搜索**: 通过语音输入进行搜索，支持实时语音识别
- **图像搜索**: 以图搜图，支持图像语义理解和OCR文字识别

### 🤖 AI智能理解
- **查询意图识别**: 自动分析用户查询意图，提取关键词和时间范围
- **语义搜索**: 基于BGE模型的向量嵌入，实现语义相似度搜索
- **智能标签**: 自动生成文件标签，提升搜索准确性

### 📁 全文件类型支持
- **文档类**: PDF、Word、Excel、PowerPoint、TXT等
- **图片类**: JPG、PNG、GIF、SVG等，支持OCR和标签识别
- **音频类**: MP3、WAV、FLAC等，支持语音转文字
- **视频类**: MP4、AVI、MOV等，支持关键帧提取和音频转录

### ⚡ 高性能搜索
- **多路召回**: 向量搜索 + 全文搜索 + 元数据搜索
- **智能融合**: RRF算法融合多路搜索结果
- **实时索引**: 文件变更监控和增量索引更新
- **快速响应**: 搜索响应时间 < 1秒

### 🔒 隐私保护
- **本地存储**: 所有数据存储在本地，保护用户隐私
- **离线运行**: 无需网络连接即可正常使用
- **数据安全**: 用户完全控制自己的数据

### 🖥️ 跨平台支持
- **Windows**: Windows 10/11
- **macOS**: macOS 10.15+
- **Linux**: Ubuntu 18.04+, CentOS 7+

## 技术架构

### 前端技术栈
- **框架**: Vue 3.4+ with Composition API
- **语言**: TypeScript 5.3+
- **UI组件**: Ant Design Vue (待集成)
- **状态管理**: Pinia (electron-vite 默认)
- **构建工具**: electron-vite (基于 Vite)
- **桌面框架**: Electron 28.0+

### 后端技术栈
- **框架**: FastAPI 0.104+
- **语言**: Python 3.9+
- **数据库**: SQLite (元数据) + Faiss (向量索引) + Whoosh (全文索引)
- **依赖管理**: Poetry
- **测试框架**: pytest

### AI服务
- **文本嵌入**: FlagEmbedding BGE模型
- **语音识别**: FastWhisper
- **图像理解**: Chinese-CLIP + PaddleOCR
- **大语言模型**: Ollama本地LLM + OpenAI云端API

## 项目结构

```
xiaoyaosearch/
├── frontend/           # Electron + Vue3 前端应用 (electron-vite)
│   ├── src/
│   │   ├── main/       # Electron 主进程
│   │   ├── preload/    # 预加载脚本
│   │   └── renderer/   # Vue 渲染进程
│   │       ├── src/
│   │       │   ├── components/  # Vue组件
│   │       │   ├── views/       # 页面视图
│   │       │   ├── stores/      # 状态管理
│   │       │   ├── utils/       # 工具函数
│   │       │   └── types/       # TypeScript类型定义
│   │       └── assets/      # 静态资源
│   ├── resources/       # Electron 资源文件
│   ├── out/            # 构建输出
│   ├── release/        # 打包发布文件
│   └── electron.vite.config.ts  # electron-vite 配置
├── backend/            # FastAPI 后端服务
│   ├── app/
│   │   ├── api/        # API路由
│   │   ├── core/       # 核心配置
│   │   ├── models/     # 数据模型
│   │   ├── services/   # 业务逻辑
│   │   └── utils/      # 工具函数
│   ├── tests/          # 测试代码
│   └── alembic/        # 数据库迁移
├── tools/              # 开发工具和脚本
│   ├── setup/          # 安装脚本
│   ├── scripts/        # 辅助脚本
│   └── dev/           # 开发工具
├── resources/          # 资源文件
│   ├── ai-models/         # AI模型文件
│   ├── icons/          # 图标文件
│   └── docs/           # 文档资源
└── docs/              # 项目文档
    ├── api/           # API文档
    ├── user/          # 用户文档
    └── dev/           # 开发文档
```

## 快速开始

### 环境要求

- **Node.js**: 18.0+
- **Python**: 3.9+
- **操作系统**: Windows 10+, macOS 10.15+, or Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/xiaoyaosearch.git
   cd xiaoyaosearch
   ```

2. **安装后端依赖**
   ```bash
   cd backend
   # 自动设置环境（推荐）
   python setup_env.py  # Windows可使用 setup.bat，Unix/Linux/macOS可使用 setup.sh
   # 或手动设置
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/Linux/macOS
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   ```

4. **下载AI模型**
   ```bash
   python tools/setup/download_models.py
   ```

5. **启动后端服务**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/Linux/macOS
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

6. **启动前端应用**
   ```bash
   cd frontend
   npm run dev
   ```

### 开发模式

```bash
# 启动后端开发服务器
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Linux/macOS
uvicorn main:app --reload

# 启动前端 Electron 应用 (推荐使用 electron-vite)
cd frontend
npm run dev

# 或者分步启动
# 1. 启动渲染进程开发服务器
cd frontend
npm run dev:renderer

# 2. 在另一个终端启动 Electron
npm run dev:electron
```

## 使用指南

### 添加搜索目录

1. 打开应用设置
2. 选择"索引设置"
3. 点击"添加目录"
4. 选择要搜索的文件夹
5. 等待索引完成

### 搜索文件

1. **文本搜索**: 在搜索框输入关键词或自然语言描述
2. **语音搜索**: 点击麦克风图标，说出搜索内容
3. **图像搜索**: 拖拽图片到搜索框或点击图片图标

### 高级搜索

- 使用过滤器按文件类型、时间范围、目录进行筛选
- 支持搜索语法：`filetype:pdf 时间:昨天 重要文档`
- 搜索历史记录和建议

## 开发指南

### 后端开发

```bash
cd backend
poetry shell

# 运行测试
pytest

# 数据库迁移
alembic upgrade head

# 代码格式化
black .
isort .
```

### 前端开发

```bash
cd frontend

# 运行测试
npm run test

# 代码检查
npm run lint

# 代码格式化
npm run format
```

### 代码规范

- **Python**: 遵循PEP 8，使用Black格式化
- **TypeScript**: 遵循ESLint规则，使用Prettier格式化
- **提交**: 使用Conventional Commits规范

## 性能优化

### 搜索性能
- 向量搜索使用Faiss IndexIVFFlat
- 全文搜索使用Whoosh BM25算法
- 多路结果使用RRF融合
- 查询结果缓存机制

### 内存优化
- AI模型按需加载
- 向量索引分块处理
- 文件内容流式读取

### 磁盘优化
- 增量索引更新
- 压缩存储向量数据
- 定期清理临时文件

## 故障排除

### 常见问题

**Q: 搜索速度慢怎么办？**
A: 检查AI模型是否正确加载，考虑减少索引目录大小或升级硬件配置。

**Q: 某些文件类型无法搜索？**
A: 确保已安装相应的依赖库，如LibreOffice用于Office文档，FFmpeg用于音视频处理。

**Q: 内存占用过高？**
A: 调整AI模型配置，使用较小的模型或启用CPU模式。

### 日志查看

- **应用日志**: `logs/app.log`
- **搜索日志**: `logs/search.log`
- **错误日志**: `logs/error.log`

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- **项目主页**: https://github.com/yourusername/xiaoyaosearch
- **问题反馈**: https://github.com/yourusername/xiaoyaosearch/issues
- **邮箱**: your.email@example.com

## 致谢

感谢以下开源项目的支持：
- [BGE](https://github.com/FlagOpen/FlagEmbedding) - 文本嵌入模型
- [FastWhisper](https://github.com/guillaumekln/faster-whisper) - 语音识别
- [Chinese-CLIP](https://github.com/OFA-Sys/Chinese-CLIP) - 图像理解
- [Faiss](https://github.com/facebookresearch/faiss) - 向量索引
- [Whoosh](https://whoosh.readthedocs.io/) - 全文搜索
- [Vue.js](https://vuejs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Electron](https://www.electronjs.org/) - 桌面应用框架