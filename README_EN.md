# XiaoyaoSearch

English | [简体中文](README.md)

![XiaoyaoSearch](docs/产品文档/产品截图/小遥搜索.png)

## 📖 Project Introduction

![XiaoyaoSearch](docs/产品文档/logo/logo_256x256.png)

XiaoyaoSearch is a cross-platform local desktop application (Windows/MacOS/Linux) designed for knowledge workers, content creators, and technical developers. Through integrated AI models, it supports multiple input methods including voice input (within 30 seconds), text input, and image input, converting user queries into semantic meaning for intelligent search and deep retrieval of local files.

## ⭐️ Important Notes
- This project is completely free for non-commercial use, allowing modification and distribution (subject to preserving copyright notices and agreement); commercial use requires authorization. See [XiaoyaoSearch Software License Agreement](LICENSE_EN) for details
- This project is entirely implemented through Vibe Coding, providing all source code and development documentation (context) for everyone to learn and exchange
  ![Development Documentation](docs/产品文档/产品截图/开发文档.png)

## Author Introduction

<p align="center">
  <img src="docs/产品文档/产品截图/作者头像.jpg" alt="dtsola" width="120" height="120" style="border-radius: 50%;">
</p>

<p align="center">
  <b>dtsola</b> — IT Architect | One-Person Company Practitioner
</p>

<p align="center">
  🌐 <a href="https://www.dtsola.com">Website</a> &nbsp;|&nbsp;
  📺 <a href="https://space.bilibili.com/736015">Bilibili</a> &nbsp;|&nbsp;
  💬 WeChat: dtsola (Technical Exchange | Business Cooperation)
</p>

<p align="center">
  <img src="docs/产品文档/产品截图/个人二维码.png" alt="WeChat QR Code" width="120">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/产品文档/产品截图/开发者交流群图.png" alt="Developer Community" width="120">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/产品文档/产品截图/用户交流群图.png" alt="User Community" width="120">
</p>

<p align="center">
  <small>WeChat Contact &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Developer Community &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; User Community</small>
</p>

### ✨ Core Features

- **🎤 Multimodal Input**: Supports voice recording, text input, and image upload
- **🔍 Deep Retrieval**: Supports content and filename search for videos (mp4, avi), audio (mp3, wav), and documents (txt, markdown, office, pdf)
- **🧠 AI-Enhanced**: Integrates advanced AI models including BGE-M3, FasterWhisper, CN-CLIP, and OLLAMA
  - **☁️ Cloud LLM Support**: OpenAI/DeepSeek/Alibaba Cloud compatible APIs with flexible local/cloud switching (v1.3.0)
  - **☁️ Cloud Embedding Models**: OpenAI/DeepSeek/Alibaba Cloud embedding APIs for enhanced search quality (v1.6.0)
  - **📚 Professional Glossary**: Terminology expansion and synonym matching with 60% improved recall in professional domains (v1.9.0)
- **⚡ High Performance**: Hybrid retrieval architecture based on Faiss vector search and Whoosh full-text search
- **🔒 Privacy Control**: Local-first with optional cloud APIs - you choose the balance between performance and privacy
- **🎨 Modern Interface**: Modern desktop application based on Electron + Vue 3 + TypeScript
- **🤖 AI Ecosystem Integration**:
  - **MCP Server Support**: Model Context Protocol support for Claude Desktop integration (v1.4.0)
  - **Agent Skills Support**: Standardized tool calling for Claude Code, VS Code, Cursor, and more (v1.5.0)

## 📖 Core Interfaces

### Search Interface

#### Main Interface
![Search Interface](docs/产品文档/产品截图/搜索界面-主界面.png)

#### Text Search
![Text Search](docs/产品文档/产品截图/搜索界面-文本搜索.png)

#### Voice Search
![Voice Search](docs/产品文档/产品截图/搜索界面-语音搜索.png)

#### Image Search
![Image Search](docs/产品文档/产品截图/搜索界面-图片搜索.png)

### Index Management Interface
![Index Management Interface](docs/产品文档/产品截图/索引管理界面.png)

### Settings Interface
![Settings Interface](docs/产品文档/产品截图/设置界面.png)

## 🏗️ Technical Architecture

### System Architecture Diagram

![System Architecture](docs/产品文档/产品截图/系统架构.png)

### Tech Stack

**Frontend Technologies**
- **Framework**: Electron + Vue 3 + TypeScript
- **UI Library**: Ant Design Vue
- **State Management**: Pinia
- **Build Tool**: Vite

**Backend Technologies**
- **Framework**: Python 3.10 + FastAPI + Uvicorn
- **AI Models**: BGE-M3 + FasterWhisper + CN-CLIP + Ollama
- **Search Engine**: Faiss (Vector Search) + Whoosh (Full-text Search)
- **Database**: SQLite + Index Files

### Project Structure

```
xiaoyaosearch/
├── backend/                        # Backend service (Python FastAPI)
│   ├── app/                       # Application core code
│   │   ├── api/                   # API routing layer
│   │   ├── core/                  # Core configuration
│   │   ├── models/                # Data models
│   │   ├── services/              # Business services
│   │   ├── schemas/               # Data schemas
│   │   └── utils/                 # Utility functions
│   ├── requirements.txt           # Python dependencies
│   ├── main.py                   # Application entry point
│   └── .env                      # Environment variables
├── frontend/                      # Frontend application (Electron + Vue3)
│   ├── src/                      # Source code
│   │   ├── main/                 # Electron main process
│   │   ├── preload/              # Preload scripts
│   │   └── renderer/             # Vue renderer process
│   ├── out/                      # Build output
│   ├── dist-electron/            # Package output
│   ├── resources/                # Application resources
│   ├── package.json              # Node.js dependencies
│   └── electron-builder.yml      # Package configuration
├── docs/                          # Project documentation
│   ├── 00-mrd.md                  # Market research
│   ├── 01-prd.md                  # Product requirements
│   ├── 02-原型.md                 # Product prototype
│   ├── 03-技术方案.md             # Technical solution
│   ├── 04-开发任务清单.md         # Development tasks
│   ├── 05-开发排期表.md           # Development schedule
│   ├── 开发进度.md                # Progress tracking
│   ├── 接口文档.md                # API documentation
│   ├── 数据库设计文档.md          # Database design
│   └── 高保真原型/                # UI prototype
├── data/                          # Data directory
│   ├── database/                  # SQLite database
│   ├── indexes/                   # Search indexes
│   │   ├── faiss/                 # Vector indexes
│   │   └── whoosh/                # Full-text indexes
│   ├── models/                   # Model files
│   └── logs/                   # Log files
├── .claude/                       # Claude assistant configuration
├── LICENSE                        # Software license agreement (Chinese)
├── LICENSE_EN                     # Software license agreement (English)
├── README.md                      # Project description (Chinese)
└── README_EN.md                   # Project description (English)
```

## 🚀 Quick Start

### Method 1: Integrated Package Deployment (Recommended for General Users)

> **Target Audience**: Non-developers who want to quickly experience XiaoyaoSearch
> **Supported Platform**: Windows only
> **Deployment Difficulty**: ⭐ Simple (One-click installation)

#### Download Integrated Package

Download the latest Windows integrated package from Baidu Drive:
- Link: https://pan.baidu.com/s/1lDaWjMCRXIT-Sqx9UFjerg?pwd=37ed
- Extraction code: 37ed

Please select the latest version to download (e.g., `XiaoyaoSearch-Windows-v1.1.1.zip`)

#### Installation Steps

**1. Extract the Package**

Extract the downloaded archive to any directory (paths without Chinese characters are recommended)

**2. Run Environment Setup Script**

Double-click `scripts/setup.bat`, which will automatically:
- Extract Python embedded runtime
- Install backend Python dependencies
- Install frontend Node dependencies
- Generate configuration files
- Create data directories

> **RTX 50 Series GPU Users**: If you are using an RTX 50 series GPU, please run `scripts/setup_rtx50显卡.bat`, which will install PyTorch with CUDA 12.8 support for optimal performance.

**3. Install Ollama**

Double-click `runtime\ollama\OllamaSetup.exe` and follow the prompts.

After installation, open a command line and run:
```bash
ollama serve
ollama pull qwen2.5:1.5b
```

**4. Download AI Models**

Download default models from Baidu Drive:
- Link: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg
- Extraction code: ycr5

Extract models to corresponding directories:
- `data\models\embedding\BAAI\bge-m3\` - Embedding model
- `data\models\cn-clip\` - Vision model
- `data\models\faster-whisper\` - Speech recognition model

**5. Launch the Application**

Double-click `scripts/startup.bat`, which will:
- Start backend service
- Start frontend service

**Detailed Documentation**: [Integrated Package Deployment Guide](docs/部署文档/整合包部署指南.md)

---

### Method 2: Developer Deployment

> **Target Audience**: Developers who want to contribute to the project
> **Supported Platform**: Windows / macOS / Linux
> **Deployment Difficulty**: ⭐⭐⭐ Requires development environment

#### Environment Requirements

- **Operating System**: Windows / macOS / Linux
- **Python**: 3.10.11+ (https://www.python.org/downloads/)
- **Node.js**: 21.x+ (https://nodejs.org/en/download)
- **Memory**: 16GB or more recommended
- **Graphics Card**: RTX3060 6GB or more recommended

#### Installation Steps

**1. Clone the Project**
```bash
git clone https://github.com/dtsola/xiaoyaosearch.git
cd xiaoyaosearch
```

**2. Backend Deployment**

```shell
# Enter backend directory
cd backend

# Install dependency packages (CPU version inference engine by default)
pip install -r requirements.txt

# Install faster-whisper
pip install faster-whisper

# Enable CUDA (optional, note: cuda version needs to be determined based on environment)
pip uninstall torch torchaudio torchvision

# RTX 40 series and older GPUs (CUDA 12.1)
pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# RTX 50 series GPUs (CUDA 12.8)
pip install torch==2.10.0+cu128 torchaudio==2.10.0+cu128 torchvision==0.25.0+cu128 --index-url https://download.pytorch.org/whl/cu128

```

**Install ffmpeg**:
https://ffmpeg.org/download.html

**Install ollama**:
https://ollama.com/

**Configure `.env` file**:
```env

# Data configuration
FAISS_INDEX_PATH=../data/indexes/faiss
WHOOSH_INDEX_PATH=../data/indexes/whoosh
DATABASE_PATH=../data/database/xiaoyao_search.db

# API configuration
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# Log configuration
LOG_LEVEL=info
LOG_FILE=../data/logs/app.log
```

**Prepare Models**:
System default model description:
- ollama: qwen2.5:1.5b
- Embedding model: BAAI/bge-m3
- Speech recognition model: Systran/faster-whisper-base
- Vision model: OFA-Sys/chinese-clip-vit-base-patch16

Note: It is recommended to prepare the default models first, successfully start the application, and then change models.

Ollama model:
ollama pull qwen2.5:1.5b (choose according to your situation)

All model download addresses: (Baidu Drive)
Link: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg?pwd=ycr5 Extraction code: ycr5

Embedding model:
- Model root directory: data/models/embedding
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/embedding/BAAI/bge-m3
  - data/models/embedding/BAAI/bge-small-zh
  - data/models/embedding/BAAI/bge-large-zh

Speech recognition model:
- Model root directory: data/models/faster-whisper
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/faster-whisper/Systran/faster-whisper-base
  - data/models/faster-whisper/Systran/faster-whisper-small
  - data/models/faster-whisper/Systran/faster-whisper-medium
  - data/models/faster-whisper/Systran/faster-whisper-large-v3

Vision model:
- Model root directory: data/models/cn-clip
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-base-patch16
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-large-patch14



**Start Backend Service**:
```shell
# Start with built-in configuration
python main.py

# Or start with uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. Frontend Deployment

```shell
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🔄 Version Upgrade Guide

When you need to upgrade to a new version, please refer to the [Version Upgrade Guide](docs/技术文档/版本升级指南_EN.md) to easily preserve your index data and configurations.

---

## 🤝 How to Contribute

Thank you for your interest in XiaoyaoSearch! We welcome contributions in any form, whether it's code, documentation, bug fixes, or new feature suggestions.

### Contribution Methods

#### Method 1: Submit a Pull Request (Recommended)

**Step 1: Fork the Project**
1. Visit the [xiaoyaosearch](https://github.com/dtsola/xiaoyaosearch) repository
2. Click the "Fork" button in the upper right corner to fork the project to your GitHub account

**Step 2: Clone to Local**
```bash
git clone https://github.com/<your-username>/xiaoyaosearch.git
cd xiaoyaosearch
```

**Step 3: Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Step 4: Make Changes**
- Follow the project coding standards
- Ensure your code has appropriate comments
- Run tests to ensure functionality works correctly

**Step 5: Commit Your Changes**
```bash
git add .
git commit -m "feat(scope): brief description of your changes"
```
Commit format conventions:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting changes
- `refactor`: Code refactoring
- `perf`: Performance optimization
- `test`: Testing related
- `chore`: Build/toolchain related

**Step 6: Push to GitHub**
```bash
git push origin feature/your-feature-name
```

**Step 7: Create a Pull Request**
1. Visit your forked repository page
2. Click the "Compare & pull request" button
3. Fill in the PR description:
   - Title: Briefly describe the changes
   - Description: Detailed explanation of the reason, implementation, and test results
4. Wait for maintainer review

#### Method 2: Submit an Issue

If you find a bug or have a feature suggestion:
1. Visit the [Issues](https://github.com/dtsola/xiaoyaosearch/issues) page
2. Click "New Issue"
3. Select an appropriate issue template
4. Describe the problem or suggestion in detail

### Code Standards

#### Frontend Standards
- Component naming: PascalCase (e.g., `SearchPanel.vue`)
- Variables/Functions: camelCase (e.g., `searchResults`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)
- Code comments: Use Chinese

#### Backend Standards
- File naming: snake_case (e.g., `search_service.py`)
- Class names: PascalCase (e.g., `SearchService`)
- Functions/Variables: snake_case (e.g., `search_files`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RESULTS`)
- Code comments: Use Chinese

### Contribution Guidelines

- ✅ Follow project coding standards
- ✅ Keep code simple, avoid over-engineering
- ✅ Add appropriate error handling
- ✅ Ensure proper test coverage
- ✅ Update relevant documentation

### Get Help

- 💬 WeChat: dtsola (please note "XiaoyaoSearch Contribution")
- 📧 Email: Contact via https://www.dtsola.com
- 📺 Bilibili: https://space.bilibili.com/736015

### Contributor Benefits

- 📝 Your name will appear in the project contributors list
- 🌟 Your changes will help thousands of users
- 🤝 Join the indie developer community for exchange and learning
- 🎁 Outstanding contributors may receive project merchandise

---

**Let's build a better local search experience together!** 🚀

## Product Roadmap
[Product Roadmap](ROADMAP_EN.md)

## Data Source Plugins List

XiaoyaoSearch supports a **plugin-based architecture** that can be extended with various data sources through plugins:

### Supported Data Source Types

| Type | Description | Status |
|------|-------------|--------|
| 📁 Local File | Built-in system, no configuration required | ✅ Implemented |
| ☁️ Yuque | Alibaba Yuque Knowledge Base | ✅ Implemented |
| ☁️ Feishu | Feishu/Lark Documents (Zero-config) | ✅ Implemented |
| ☁️ DingTalk | DingTalk Documents (.xyddjson metadata) | ✅ Implemented |
| ☁️ Notion | Notion Notes | 📋 Planned |
| 🔗 GitHub | Code repositories and Wiki | 📋 Planned |
| 🔗 GitLab | GitLab repositories | 📋 Planned |

### Complete List

View the complete data source plugins list (13 types):

**📖 [Data Source Plugins List](docs/技术文档/数据源插件列表_EN.md)** | [中文版](docs/技术文档/数据源插件列表.md)

### Develop Plugins

Want to develop a new data source plugin?

**📖 [Plugin Development Guide](docs/技术文档/插件开发文档.md)**

---

## 🔥 MCP Server Support

XiaoyaoSearch now supports **Model Context Protocol (MCP)**, which can be connected by AI applications like Claude Desktop for intelligent local file search.

### What is MCP?

MCP (Model Context Protocol) is an open-source protocol introduced by Anthropic that allows AI applications (such as Claude Desktop) to connect to local data sources. Through MCP, Claude can directly search and access your local files, providing smarter Q&A and assistance.

### Agent Skills Support

XiaoyaoSearch now supports **Agent Skills**, providing standardized MCP tool calling capabilities for AI assistants like Claude Code, VS Code, and Cursor.

**Install Skill**:

```bash
# Project level
cp -r skills/ .claude/skills/

# Or global level
cp -r skills/ ~/.claude/skills/
```

After installation, AI assistants can automatically discover XiaoyaoSearch's MCP tools and provide correct usage guidance.

### Supported Search Tools

| Tool Name | Description | AI Model |
|-----------|-------------|----------|
| semantic_search | Semantic search with natural language query understanding | BGE-M3 |
| fulltext_search | Full-text search with precise keyword matching and Chinese word segmentation | Whoosh |
| voice_search | Voice search with speech-to-text conversion | FasterWhisper |
| image_search | Image search with similarity-based content retrieval | CN-CLIP |
| hybrid_search | Hybrid search combining semantic and full-text search advantages | BGE-M3 + Whoosh |

### MCP Client Configuration

XiaoyaoSearch MCP server uses **HTTP transport protocol**. Any client that supports HTTP MCP can connect.

#### Claude Code CLI Configuration

Official command-line tool for quick configuration:

```bash
# Add HTTP MCP server
claude mcp add --transport http xiaoyao-search http://127.0.0.1:8000/mcp

# Check if MCP was added successfully (ensure MCP is running first)
claude mcp list
```

#### Other MCP-Enabled Clients

Any client that supports the MCP protocol can connect to: `http://127.0.0.1:8000/mcp`

**Basic Configuration Template**:

```json
{
  "name": "xiaoyao-search",
  "url": "http://127.0.0.1:8000/mcp",
  "type": "sse"
}
```

**Common Client Configuration Examples**:

- **Cline (VSCode Extension)**: Search for `cline.mcpServers` in VSCode settings and add the above configuration
- **Cursor**: Add the above configuration in Cursor's MCP server settings
- **Other MCP Clients**: Refer to the client documentation and use SSE transport

### Usage Examples

Once configured, you can perform the following operations in Claude Desktop:

**Semantic Search**:
```
User: Help me find documents about asynchronous programming
Claude: [Calls semantic_search tool] Found 5 related documents...
```

**Full-text Search**:
```
User: Search for code files containing "async def"
Claude: [Calls fulltext_search tool] Found 3 code files...
```

**Image Search**:
```
User: [Uploads image] Find similar charts
Claude: [Calls image_search tool] Found 2 similar charts...
```

### Verify MCP Connection

Visit the health check endpoint to verify MCP service status:
```bash
curl http://127.0.0.1:8000/mcp/health
```

Response example:
```json
{
  "status": "enabled",
  "server": "fastmcp",
  "tools_count": 5,
  "tools": ["semantic_search", "fulltext_search", "voice_search", "image_search", "hybrid_search"]
}
```

### Configuration Options

Configure MCP service in `backend/.env`:

```bash
# MCP Server Configuration
MCP_SSE_ENABLED=true              # Whether to enable MCP SSE service
MCP_SERVER_NAME=xiaoyao-search    # Server name
MCP_DEFAULT_LIMIT=20              # Default result count
MCP_DEFAULT_THRESHOLD=0.5         # Default similarity threshold
MCP_VOICE_ENABLED=true            # Whether to enable voice search
```

### Technical Implementation

- **Protocol Implementation**: Using [fastmcp](https://github.com/PrefectHQ/fastmcp) framework
- **Transport Method**: HTTP SSE (Server-Sent Events)
- **Architecture Pattern**: FastAPI integration, sharing AI models and search services
- **Memory Optimization**: Single process, models loaded only once, saving 4-6GB memory

### Detailed Documentation

- [MCP PRD](docs/特性开发/mcp/mcp-01-prd.md) - Product Requirements Document
- [MCP Technical Solution](docs/特性开发/mcp/mcp-03-技术方案.md) - Technical Implementation Solution
- [MCP Official Documentation](https://modelcontextprotocol.io/) - MCP Protocol Specification

---

## Project Contributors

Thanks to the following people for their contributions to this project:

<p align="center">
  <a href="https://github.com/luojiyin1987">
    <img src="https://avatars.githubusercontent.com/u/6524977?v=4" width="80" height="80" style="border-radius: 50%;">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/jidingliu">
    <img src="https://avatars.githubusercontent.com/u/26623206?v=4" width="80" height="80" style="border-radius: 50%;">
  </a>
</p>

<p align="center">
  <a href="https://github.com/luojiyin1987">@luojiyin1987</a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/jidingliu">@jidingliu</a>
</p>

---

## 📝 Version Changelog

### v1.9.0 (2026-04-12) - Search Optimization

**Core Optimizations**:
- ✅ **Terminology Expansion Timing**: Moved terminology expansion before LLM enhancement, based on original user input
- ✅ **Responsibility Separation**: Glossary (professional synonyms) vs LLM (general query optimization)
- ✅ **Smart Merging**: Automatic deduplication of expansion terms
- ✅ **Concurrency Control**: Intelligent concurrency control based on CPU cores (CPU cores × 2)
- ✅ **Recall Improvement**: 60% improved recall in professional terminology scenarios

**Detailed Documentation**: [v1.9.0 Release Notes](docs/产品文档/版本更新文档/v1.9.0-搜索优化-术语库支持.md)

### v1.8.0 (2026-04-08) - DingTalk Documents Support

**New Features**:
- ✅ DingTalk document data source support (with DingTalk export tool)
- ✅ Metadata file parsing (.xyddjson format)
- ✅ Original link jump functionality

**Detailed Documentation**: [v1.8.0 Release Notes](docs/产品文档/版本更新文档/v1.8.0-钉钉文档+知识库支持.md)

### v1.7.0 (2026-03-31) - Feishu Documents Support

**New Features**:
- ✅ Feishu document data source support
- ✅ Metadata block parsing
- ✅ Original link jump functionality

### v1.6.0 (2026-03-26) - Cloud Embedding Models

**New Features**:
- ✅ Cloud embedding model API support
- ✅ Local/cloud mutual switching
- ✅ Batch text embedding optimization

### v1.5.0 (2026-03-20) - Agent Skills

**New Features**:
- ✅ MCP Agent Skills support
- ✅ Tool calling capabilities for Claude Code/VS Code/Cursor

### v1.4.0 (2026-03-15) - MCP Server Support

**New Features**:
- ✅ MCP protocol support
- ✅ Connectable by Claude Desktop
- ✅ SSE transport method

### v1.3.0 (2026-03-10) - OpenAI Cloud Models

**New Features**:
- ✅ OpenAI-compatible cloud LLMs
- ✅ Dynamic form configuration
- ✅ Encrypted API key storage

### v1.2.0 (2026-03-05) - Plugin Architecture

**New Features**:
- ✅ Plugin architecture framework
- ✅ Yuque knowledge base data source

### v1.1.0 (2026-02-28) - i18n Internationalization

**New Features**:
- ✅ Bilingual Chinese/English support
- ✅ i18n framework integration

### v1.0.0 (2026-02-20) - MVP Version

**Core Features**:
- ✅ Multimodal search (text/voice/image)
- ✅ Deep local file retrieval
- ✅ BGE-M3 + FasterWhisper + CN-CLIP
- ✅ Faiss + Whoosh hybrid search

---