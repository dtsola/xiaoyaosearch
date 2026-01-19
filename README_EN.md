# XiaoyaoSearch

English | [简体中文](README.md)

![XiaoyaoSearch](docs/产品文档/应用截图/小遥搜索.png)

## 📖 Project Introduction

![XiaoyaoSearch](docs/产品文档/logo/logo_256x256.png)

XiaoyaoSearch is a cross-platform local desktop application (Windows/MacOS/Linux) designed for knowledge workers, content creators, and technical developers. Through integrated AI models, it supports multiple input methods including voice input (within 30 seconds), text input, and image input, converting user queries into semantic meaning for intelligent search and deep retrieval of local files.

## ⭐️ Important Notes
- This project is completely free for personal use but cannot be modified and redistributed; commercial use requires authorization. See [XiaoyaoSearch Software License Agreement](LICENSE_EN) for details
- This project is entirely implemented through Vibe Coding, providing all source code and development documentation (context) for everyone to learn and exchange
  ![Development Documentation](docs/产品文档/应用截图/开发文档.png)

## Author Introduction
- dtsola [IT Solution Architect | One-Person Company Practitioner]
- Website: https://www.dtsola.com
- Bilibili: https://space.bilibili.com/736015
- WeChat: dtsola (please state your purpose when contacting)
![dtsola](docs/产品文档/应用截图/个人二维码.png)

### ✨ Core Features

- **🎤 Multimodal Input**: Supports voice recording, text input, and image upload
- **🔍 Deep Retrieval**: Supports content and filename search for videos (mp4, avi), audio (mp3, wav), and documents (txt, markdown, office, pdf)
- **🧠 AI-Enhanced**: Integrates advanced AI models including BGE-M3, FasterWhisper, CN-CLIP, and OLLAMA
- **⚡ High Performance**: Hybrid retrieval architecture based on Faiss vector search and Whoosh full-text search
- **🔒 Privacy & Security**: Runs locally, data is not uploaded to the cloud, supports privacy mode
- **🎨 Modern Interface**: Modern desktop application based on Electron + Vue 3 + TypeScript

## 📖 Core Interfaces

### Search Interface

#### Main Interface
![Search Interface](docs/产品文档/应用截图/搜索界面-主界面.png)

#### Text Search
![Text Search](docs/产品文档/应用截图/搜索界面-文本搜索.png)

#### Voice Search
![Voice Search](docs/产品文档/应用截图/搜索界面-语音搜索.png)

#### Image Search
![Image Search](docs/产品文档/应用截图/搜索界面-图片搜索.png)

### Index Management Interface
![Index Management Interface](docs/产品文档/应用截图/索引管理界面.png)

### Settings Interface
![Settings Interface](docs/产品文档/应用截图/设置界面.png)

## 🏗️ Technical Architecture

### System Architecture Diagram

![System Architecture](docs/产品文档/应用截图/系统架构.png)

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

### Environment Requirements

- **Operating System**: Windows/MAC OS/Linux
- **Python**: 3.10.11+
- **Node.js**: 21.x+
- **Memory**: 8GB or more recommended

### Installation Steps

#### 1. Clone the Project
```bash
git clone https://github.com/dtsola/xiaoyaosearch.git
cd xiaoyaosearch
```

#### 2. Backend Deployment

```shell
# Enter backend directory
cd backend

# Install dependency packages (CPU version inference engine by default)
pip install -r requirements.txt

# Install faster-whisper
pip install faster-whisper

# Enable CUDA (optional, note: cuda version needs to be determined based on environment)
pip uninstall torch torchaudio torchvision
pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

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

## Product Roadmap
[Product Roadmap](ROADMAP_EN.md)