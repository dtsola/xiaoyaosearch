# 小遥搜索 XiaoyaoSearch - 项目基础文档

> **项目概述**：小遥搜索是一款支持多模态AI智能搜索的本地桌面应用，为知识工作者、内容创作者和技术开发者提供语音、文本、图像输入的智能文件检索能力。

## 🎯 核心功能

- **多模态智能搜索**：支持语音输入（30秒内）、文本输入、图片输入，通过AI转换为语义进行搜索
- **本地文件深度检索**：支持视频（mp4、avi）、音频（mp3、wav）、文档（txt、markdown、office、pdf）的内容和文件名搜索
- **灵活的AI模型配置**：支持云端API（OpenAI、Claude、阿里云等）和本地模型（Ollama、FastWhisper、CN-CLIP）的自由切换

## 💻 开发环境
- **操作系统**：Windows 11
- **Python版本**：3.10.11
- **Node.js版本**：21.x

## 🏗️ 技术架构

### 技术栈
- **前端**：Electron + Vue 3 + TypeScript + Ant Design Vue + vue-i18n@9（国际化）
- **后端**：Python 3.10 + FastAPI + Uvicorn
- **AI模型**：BGE-M3（文本嵌入）+ FasterWhisper（语音识别）+ CN-CLIP（图像理解）+ Ollama（大语言模型）
- **搜索引擎**：Faiss（向量搜索）+ Whoosh（全文搜索）
- **数据库**：SQLite（主数据库）+ Faiss索引文件 + Whoosh索引文件
- **国际化**：vue-i18n@9 + Ant Design Vue locale + Day.js locale（中英文双语支持）

### 系统架构图
```
┌─────────────────────────────────────────────────────────────────────┐
│                     Electron 桌面应用                            │
├─────────────────────────────────────────────────────────────────────┤
│                     Vue 3 前端框架                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │ 搜索组件     │  │ 索引组件     │  │ 配置组件          │        │
│  │ - 多模态输入  │  │ - 索引管理   │  │ - AI模型配置      │        │
│  │ - 结果展示   │  │ - 索引状态   │  │ - 应用设置        │        │
│  └──────────────┘  └──────────────┘  └──────────────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│                   HTTP API 通信层                              │
│                 (Axios + FastAPI)                              │
├─────────────────────────────────────────────────────────────────────┤
│                           后端服务                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │ 搜索API      │  │ 索引API      │  │ 配置API            │        │
│  │ /api/search  │  │ /api/index   │  │ /api/config        │        │
│  └──────────────┘  └──────────────┘  └──────────────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│                   核心服务层                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │ 搜索服务     │  │ 索引服务     │  │ AI模型服务         │        │
│  │ - 向量搜索   │  │ - 文件扫描   │  │ - 文本嵌入         │        │
│  │ - 全文搜索   │  │ - 索引构建   │  │ - 语音识别         │        │
│  │ - 混合搜索   │  │ - 索引管理   │  │ - 图像理解         │        │
│  └──────────────┘  └──────────────┘  └──────────────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│                   存储引擎                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │ Faiss        │  │ Whoosh      │  │ SQLite            │        │
│  │ 向量索引      │  │ 全文索引     │  │ 配置/元数据        │        │
│  │ 高效检索      │  │ 模糊搜索     │  │ 搜索历史          │        │
│  └──────────────┘  └──────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

## 📋 设计文档引用

### 核心设计文档
- **[产品需求文档(PRD)](docs/01-prd.md)** - 详细的功能规格说明和用户故事（含i18n国际化需求）
- **[产品原型设计](docs/02-原型.md)** - 完整的UI设计和交互规范（含i18n语言切换器设计）
- **[技术方案设计](docs/03-技术方案.md)** - 技术架构和实现细节（含i18n技术方案）
- **[技术选型文档](docs/技术选型.md)** - 技术选型理由和对比分析（含i18n技术选型）
- **[数据库设计文档](docs/数据库设计文档.md)** - 完整的数据库架构和表结构设计
- **[市场调研文档(MRD)](docs/00-mrd.md)** - 市场分析和商业模式
- **[开发任务清单](docs/04-开发任务清单.md)** - 详细的开发任务分解
- **[开发排期表](docs/05-开发排期表.md)** - 项目时间规划和里程碑
- **[开发进度](docs/开发进度.md)** - 实时开发进度跟踪和任务管理

### 接口文档
- **[API接口文档](docs/接口文档.md)** - 详细的API规范说明（含i18n错误响应格式）

### i18n 国际化文档
- **[i18n PRD](docs/特性开发/i18n/i18n-01-prd.md)** - 国际化产品需求文档
- **[i18n 原型设计](docs/特性开发/i18n/i18n-02-原型.md)** - 国际化UI/UX设计规范
- **[i18n 技术方案](docs/特性开发/i18n/i18n-03-技术方案.md)** - 国际化技术实现方案
- **[i18n 开发任务清单](docs/特性开发/i18n/i18n-04-开发任务清单.md)** - 42个任务清单（100%完成）
- **[i18n 开发排期表](docs/特性开发/i18n/i18n-05-开发排期表.md)** - 国际化开发时间规划

### 测试文档
- **[配置接口测试](docs/测试文档/测试用例/test-data-config.md)** - AI模型配置接口完整测试数据（包含创建、测试、启用/禁用、删除等操作的curl命令）
- **[搜索接口测试](docs/测试文档/测试用例/test-data-search.md)** - 搜索服务接口完整测试数据（包含文本搜索、多模态搜索、搜索历史、搜索建议等功能测试）
- **[索引接口测试](docs/测试文档/测试用例/test-data-index.md)** - 索引管理接口完整测试数据（包含创建索引、更新索引、停止索引、索引状态等操作测试）
- **[系统接口测试](docs/测试文档/测试用例/test-data-system.md)** - 系统配置和健康检查接口测试数据
- **测试数据目录** - 包含测试配置和测试资源的 [测试数据目录](docs/测试文档/测试数据/)

### 产品文档
- **产品资源目录** - 包含产品相关的视觉资源：
  - **logo/** - 产品logo文件（logo.png、logo_256x256.png）
  - **应用截图/** - 产品截图和系统架构图（搜索界面、索引管理、设置界面等）

## 🛠️ 开发规范

### 代码规范
所有代码编写、文档编写、注释必须使用中文。

#### 前端代码规范 (Vue3 + TypeScript)
```typescript
// 组件文件命名：PascalCase，如 SearchApp.vue
// 变量和函数：camelCase，如 searchResults, handleSearch()
// 常量：UPPER_SNAKE_CASE，如 API_BASE_URL
// 类型定义：PascalCase，如 SearchType, FileType

// 组件示例
<template>
  <div class="search-container">
    <!-- 使用中文注释 -->
    <a-input
      v-model:value="searchQuery"
      placeholder="请输入搜索内容"
      @press-enter="handleSearch"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { SearchRequest } from '@/types/api'

// 搜索查询状态
const searchQuery = ref<string>('')

// 处理搜索请求
const handleSearch = async (): Promise<void> => {
  try {
    // 搜索逻辑实现
  } catch (error) {
    console.error('搜索失败:', error)
  }
}
</script>
```

#### 后端代码规范 (Python + FastAPI)
```python
# 文件命名：snake_case，如 search_service.py
# 类名：PascalCase，如 SearchEngine
# 函数和变量：snake_case，如 search_files, api_client
# 常量：UPPER_SNAKE_CASE，如 MAX_FILE_SIZE

# API路由示例
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/search", tags=["搜索"])

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索查询词", min_length=1, max_length=500)
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")

@router.post("/", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    执行文件搜索

    Args:
        request: 搜索请求参数

    Returns:
        SearchResponse: 搜索结果响应

    Raises:
        HTTPException: 搜索失败时返回错误信息
    """
    try:
        # 搜索逻辑实现
        results = await search_service.search(request.query, request.limit)
        return SearchResponse(data=results)
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
```

### Git 规范

#### 分支命名规范
- `main` - 主分支，用于生产环境
- `develop` - 开发分支，用于集成测试
- `feature/功能名称` - 功能开发分支，如 `feature/multimodal-search`
- `bugfix/问题描述` - 问题修复分支，如 `bugfix/index-crash-fix`
- `hotfix/紧急修复` - 紧急修复分支，如 `hotfix/memory-leak`

#### 提交信息规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型(type)说明：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 重构代码
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(search): 添加多模态搜索功能

- 支持语音输入转换为搜索查询
- 支持图片上传进行图像理解搜索
- 优化搜索结果展示界面

Closes #123
```

#### 代码审查要求
1. 所有代码必须经过至少一人审查才能合并
2. 审查重点：功能正确性、代码质量、性能影响、安全性
3. 必须通过所有自动化测试
4. 代码覆盖率不低于80%

### 测试规范

#### 单元测试
```python
# 后端测试示例 (pytest)
import pytest
from app.services.search_service import SearchService

class TestSearchService:
    """搜索服务测试类"""

    @pytest.fixture
    def search_service(self):
        """创建搜索服务实例"""
        return SearchService()

    async def test_search_with_valid_query(self, search_service):
        """测试有效查询的搜索功能"""
        # Arrange
        query = "测试查询"

        # Act
        results = await search_service.search(query)

        # Assert
        assert results.success is True
        assert len(results.data) > 0
```

```typescript
// 前端测试示例 (Vitest + Vue Test Utils)
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchApp from '@/components/SearchApp.vue'

describe('SearchApp', () => {
  it('应该正确处理搜索输入', async () => {
    const wrapper = mount(SearchApp)

    await wrapper.find('input').setValue('测试查询')
    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')[0]).toEqual(['测试查询'])
  })
})
```

#### 测试覆盖率要求
- 无需完全覆盖：满足80-20原则、简单原则
- 后端核心服务：>90%
- 前端组件：>80%
- API接口：100%

### 功能规范

#### 响应时间要求
- 应用启动：<3秒
- 搜索功能：稳定可靠
- 文件预览：<1秒
- 索引构建：后台异步处理

#### 内存使用限制
- 前端应用：<500MB
- 后端服务：<2GB
- AI模型加载：按需动态加载

### 安全规范

#### 数据安全
- 所有API密钥使用环境变量存储
- 本地数据库文件加密存储
- 用户数据不上传云端
- 支持隐私模式（不记录搜索历史）

#### 输入验证
```python
# 文件上传验证
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.png', '.jpg', '.jpeg'}

def validate_uploaded_file(file: UploadFile) -> bool:
    """验证上传文件的安全性"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超出限制")

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    return True
```

### 部署规范

#### 环境配置
```bash
# 开发环境
NODE_ENV=development
API_BASE_URL=http://localhost:8000
LOG_LEVEL=debug

# 生产环境
NODE_ENV=production
API_BASE_URL=http://127.0.0.1:8000
LOG_LEVEL=info
```

#### 🔧 后端部署（Python FastAPI）

**Windows开发环境启动步骤：**

1. **创建Python虚拟环境**
```powershell
cd backend
python -m venv venv
```

2. **安装依赖包**
```powershell
# 升级pip
.\venv\Scripts\python.exe -m pip install --upgrade pip

# 安装基础依赖（当前使用）
.\venv\Scripts\pip.exe install -r requirements.txt

# 完整AI模型依赖（后续添加）
# .\venv\Scripts\pip.exe install -r requirements-ai.txt
```

3. **创建数据目录**
```powershell
mkdir ..\data\database
mkdir ..\data\indexes\faiss
mkdir ..\data\indexes\whoosh
mkdir ..\data\configs
mkdir ..\data\logs
mkdir ..\data\uploads
```

4. **创建环境配置文件**
```powershell
# 创建 .env 文件
New-Item .env -type file -force
```

**`.env` 文件内容：**
```env
# AI模型配置
CLIP_MODEL_NAME=OFA-Sys/chinese-clip-vit-base-patch16
BGE_MODEL_NAME=BAAI/bge-m3
WHISPER_MODEL_SIZE=base

# 数据路径
FAISS_INDEX_PATH=../data/indexes/faiss
WHOOSH_INDEX_PATH=../data/indexes/whoosh
DATABASE_PATH=../data/database/xiaoyao_search.db

# API配置
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# 日志配置
LOG_LEVEL=info
LOG_FILE=../data/logs/app.log

# 文件上传配置
MAX_FILE_SIZE=50MB
UPLOAD_FOLDER=../data/uploads

# 云端API配置
# ALIYUN_ACCESS_KEY_ID=your_access_key_id
# ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
# OPENAI_API_KEY=your_openai_api_key
```

5. **启动后端服务**
```powershell
# 方法一：直接启动main.py（内置uvicorn配置）
.\venv\Scripts\python.exe main.py

# 方法二：使用uvicorn命令启动
.\venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000 --reload

# 方法三：使用uvicorn命令（带详细日志）
.\venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000 --reload --log-level info
```

**验证后端服务运行状态：**
- API服务: http://127.0.0.1:8000
- 健康检查: http://127.0.0.1:8000/api/system/health
- Swagger文档: http://127.0.0.1:8000/docs
- ReDoc文档: http://127.0.0.1:8000/redoc

#### 🖥️ 前端部署（Electron + Vue3）

**Windows开发环境启动步骤：**

1. **安装Node.js依赖**
```powershell
cd frontend
npm install
```

2. **高保真原型启动（已完成）**
```powershell
# 启动高保真原型开发服务器
cd docs\高保真原型\v0.1
npm run dev

# 访问地址
# 开发服务器: http://localhost:5173
# 或根据终端输出的实际地址
```

3. **完整Electron应用启动**
```powershell
# 启动开发服务器
cd frontend
npm run dev

# 启动Electron应用
npm run electron:dev
```

4. **构建生产版本**
```powershell
# 构建Vue应用
npm run build

# 打包Electron应用
npm run electron:build
```

**验证前端服务：**
- **高保真原型**: http://localhost:5173 (docs/高保真原型/v0.1/)
- **完整前端**: http://localhost:3000 或 http://localhost:5173
- **Electron桌面应用**: 自动启动

#### 🚀 完整启动流程

**方法一：分别启动（推荐开发调试）**
```powershell
# 终端1：启动后端
cd backend
.\venv\Scripts\python.exe main.py

# 终端2：启动前端
cd frontend
npm run electron:dev
```

**后端启动方式说明：**
重要：使用PowerShell来运行Windows的Python虚拟环境
- **方式1**：`.\venv\Scripts\python.exe main.py` - 使用main.py内置的uvicorn配置
- **方式2**：`.\venv\Scripts\uvicorn.exe main:app --reload` - 直接使用uvicorn命令
- **方式3**：`.\venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000 --reload --log-level info` - 带详细参数的uvicorn命令

**推荐使用方式1**，因为main.py已配置好默认参数，使用最简单。

**方法二：使用启动脚本（后续实现）**
```powershell
# 批量启动服务（待实现）
npm run start:all
```

## 📊 项目进度

### 进度跟踪方式
项目进度采用 **分文档管理** 方式：

- **📋 实时进度**: [开发进度文档](docs/开发进度.md) - 详细的任务状态、进度统计和里程碑追踪
- **📅 总体规划**: [开发排期表](docs/05-开发排期表.md) - 项目时间规划和整体安排

### 当前开发状态
- 🚀 **当前阶段**: 第五阶段应用打包和发布 (即将完成)
- ⏰ **开发周期**: 8-10周 (2025年11月-2026年2月)
- 🎯 **核心目标**: 完成多模态AI智能搜索桌面应用的MVP开发和发布
- 🎆 **重大成就**:
  - MVP开发100%完成，所有核心功能实现并测试通过
  - i18n国际化100%完成，720+翻译键，中英文双语支持
  - 36个API接口全部实现，多模态搜索功能完全就绪

> **进度管理规范**: 所有开发任务完成后，必须在 [开发进度文档](docs/开发进度.md) 中更新状态和里程碑进度。

## 🎯 AI助手使用指南

### 项目上下文
- **当前会话语言**：必须使用中文进行所有回复、文档编写和代码注释
- **项目特点**：桌面应用 + AI模型集成 + 多模态搜索
- **开发阶段**：MVP开发阶段，专注核心功能实现

### 功能检查要求
每次完成一个功能开发后，必须自行检查：
1. ✅ 功能是否完全按照需求实现
2. ✅ 代码是否遵循项目规范
3. ✅ 是否有适当的错误处理
4. ✅ 是否添加了必要的测试
5. ✅ 文档是否同步更新

### 常见任务指导
- **新功能开发**：先查看[技术方案](docs/03-技术方案.md)和[PRD](docs/01-prd.md)
- **Bug修复**：查看错误日志，定位问题根因，添加回归测试
- **性能优化**：参考性能规范，使用性能分析工具
- **代码重构**：保持向后兼容，更新相关测试和文档
- **进度跟踪**：使用[开发进度文档](docs/开发进度.md)更新任务状态和里程碑进度

### 进度管理要求
每次完成任务后，必须按照 [开发进度文档](docs/开发进度.md) 的使用指南：
1. ✅ 更新任务状态和里程碑进度
2. ✅ 记录遇到的问题和风险提醒
3. ✅ 同步实时进度更新
4. ✅ 验证阶段进入条件

> 📖 **详细操作**: 参考 [开发进度文档](docs/开发进度.md) 的"文档使用指南"部分。

## 📞 联系方式

### 📚 文档索引
根据不同需求参考对应文档：

| 需求类型 | 主要文档 | 用途 |
|---------|----------|------|
| **技术实现** | [技术方案](docs/03-技术方案.md) | 架构设计和技术细节（含i18n技术方案） |
| **数据库设计** | [数据库设计文档](docs/数据库设计文档.md) | 完整的数据库架构和表结构设计 |
| **产品需求** | [产品需求文档](docs/01-prd.md) | 功能规格和用户故事（含i18n需求） |
| **实时进度** | [开发进度](docs/开发进度.md) | 当前任务状态和里程碑 |
| **总体规划** | [开发排期表](docs/05-开发排期表.md) | 时间安排和整体计划 |
| **接口规范** | [API接口文档](docs/接口文档.md) | API详细规范说明（含i18n错误响应） |
| **高保真原型** | [高保真原型](docs/高保真原型/v1.0/) | Vue3前端交互原型，支持多模态搜索（含i18n） |
| **i18n国际化** | [i18n技术方案](docs/特性开发/i18n/i18n-03-技术方案.md) | 国际化技术实现和架构设计 |
| **API测试** | [配置接口测试](docs/测试文档/测试用例/test-data-config.md) | AI模型配置接口测试数据（curl/Postman） |
| **搜索测试** | [搜索接口测试](docs/测试文档/测试用例/test-data-search.md) | 搜索服务接口测试数据（含多模态搜索） |
| **索引测试** | [索引接口测试](docs/测试文档/测试用例/test-data-index.md) | 索引管理接口测试数据（创建/更新/停止） |
| **系统测试** | [系统接口测试](docs/测试文档/测试用例/test-data-system.md) | 系统配置和健康检查接口测试数据 |
| **产品资源** | [产品文档目录](docs/产品文档/) | 产品logo、应用截图、系统架构图等视觉资源 |

### 📞 快速导航
- **🔧 技术问题** → [技术方案文档](docs/03-技术方案.md)
- **📋 产品问题** → [产品需求文档](docs/01-prd.md)
- **📊 进度跟踪** → [开发进度文档](docs/开发进度.md)
- **📅 时间规划** → [开发排期表](docs/05-开发排期表.md)
- **🧪 API测试** → [测试文档目录](docs/测试文档/测试用例/)
- **🎨 产品资源** → [产品文档目录](docs/产品文档/)

---

## 📝 文档说明

### 本文档定位
`.claude/CLAUDE.md` 是 **项目基础配置和AI助手使用指南**，提供：
- 🎯 项目核心信息和架构概览
- 🛠️ 开发规范和部署流程
- 🤖 AI助手工作指导和上下文
- 📚 完整文档索引和快速导航

### 与其他文档的关系
- **📊 实时进度管理** → [开发进度文档](docs/开发进度.md)
- **📅 总体时间规划** → [开发排期表](docs/05-开发排期表.md)
- **🔧 技术实现细节** → [技术方案](docs/03-技术方案.md)
- **📋 产品功能需求** → [产品需求文档](docs/01-prd.md)

---

**最后更新时间**：2026年1月19日
**文档版本**：v5.1 (测试文档+产品文档补充版)
**维护者**：AI助手


### 💡 重要提醒
本项目要求所有AI回复、文档编写、代码注释必须使用中文。每次功能完成后需更新 [开发进度文档](docs/开发进度.md) 并遵循项目规范。