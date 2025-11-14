# XiaoyaoSearch Backend

AI驱动的桌面搜索应用程序后端服务，基于Python + FastAPI构建。

## 快速开始

### 环境要求

- **Python**: 3.9+
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最小8GB，推荐16GB+（用于AI模型）
- **存储**: 最小10GB可用空间

### 自动设置环境

#### Windows

```bash
# 双击运行或在命令行中执行
setup.bat
```

#### Unix/Linux/macOS

```bash
# 运行设置脚本
./setup.sh
```

### 手动设置环境

1. **创建虚拟环境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

2. **安装依赖**

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

3. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置你的设置
# 主要是数据库连接、API密钥等
```

4. **初始化数据库**

```bash
# 运行数据库迁移
alembic upgrade head
```

## 开发

### 启动开发服务器

```bash
# 激活虚拟环境后
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### API文档

启动服务器后，访问以下地址查看API文档：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 代码质量工具

```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码检查
flake8 .

# 类型检查
mypy .

# 运行所有代码质量检查
pre-commit run --all-files
```

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=backend --cov-report=html

# 运行特定类型的测试
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m "not slow"    # 跳过慢速测试
```

## 项目结构

```
backend/
├── main.py                    # FastAPI应用入口
├── requirements.txt           # 生产依赖
├── requirements-dev.txt       # 开发依赖
├── pyproject.toml            # 项目配置（工具配置）
├── setup_env.py              # 环境设置脚本
├── setup.bat                 # Windows快速设置脚本
├── setup.sh                  # Unix快速设置脚本
├── .env.example              # 环境变量模板
├── alembic.ini               # 数据库迁移配置
├── alembic_env.py            # Alembic环境配置
├── pytest.ini               # 测试配置
│
├── api/                      # API路由层
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── api.py           # API路由汇总
│       └── endpoints/       # API端点实现
│           ├── search.py
│           ├── files.py
│           ├── directories.py
│           ├── user_settings.py
│           └── tags.py
│
├── core/                     # 核心配置和工具
│   ├── __init__.py
│   ├── config.py            # 应用配置
│   └── database.py          # 数据库配置
│
├── db/                       # 数据库相关
│   ├── __init__.py
│   └── base.py              # 数据库基类
│
├── models/                   # SQLAlchemy数据模型
│   ├── __init__.py
│   ├── file.py
│   ├── directory.py
│   ├── search_history.py
│   ├── user_settings.py
│   └── tag.py
│
├── schemas/                  # Pydantic数据验证模型
│   ├── __init__.py
│   ├── file.py
│   ├── directory.py
│   ├── search.py
│   ├── user_settings.py
│   └── tag.py
│
├── services/                 # 业务服务层
│   └── __init__.py
│
├── utils/                    # 工具函数
│   └── __init__.py
│
└── tests/                    # 测试代码
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    └── integration/
```

## 核心功能

### 🔍 搜索引擎
- **多模态搜索**: 支持文本、语音、图像搜索
- **混合检索**: 向量搜索 + 全文搜索
- **智能查询理解**: AI增强的查询分析
- **结果融合**: RRF算法优化搜索结果

### 📁 索引管理
- **文件扫描**: 递归目录扫描和变更监控
- **多格式支持**: 文档、图片、音频、视频处理
- **增量索引**: 实时文件变更检测
- **索引优化**: 定期索引重建和优化

### 🤖 AI服务
- **LLM查询理解**: Ollama本地模型 + OpenAI云端
- **文本嵌入**: BGE中文语义模型
- **语音识别**: FastWhisper语音转文字
- **图像理解**: CN-CLIP图像理解 + OCR

### 💾 数据存储
- **向量索引**: Faiss高性能向量搜索
- **全文索引**: Whoosh轻量级文本搜索
- **元数据库**: SQLite嵌入式数据库
- **智能缓存**: 多级缓存优化性能

## 配置说明

### 环境变量

主要环境变量配置（`.env`文件）：

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./xiaoyaosearch.db

# API配置
API_V1_STR=/api/v1
DEBUG=False

# 安全配置
SECRET_KEY=your-secret-key-change-in-production

# AI模型配置
AI_MODEL_DIR=./ai-models
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=your-openai-api-key-here

# 文件存储配置
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760

# 索引存储配置
VECTOR_INDEX_PATH=./data/vector_index.faiss
FULLTEXT_INDEX_PATH=./data/fulltext_index
```

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### 开发部署

```bash
# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产部署

```bash
# 安装生产依赖
pip install gunicorn

# 启动生产服务器
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

```bash
# 构建镜像
docker build -t xiaoyaosearch-backend .

# 运行容器
docker run -p 8000:8000 xiaoyaosearch-backend
```

## 性能优化

### 内存优化
- AI模型按需加载
- LRU缓存机制
- 定期内存清理

### 搜索优化
- 向量索引压缩
- 查询结果缓存
- 并行搜索处理

### 文件处理优化
- 异步文件处理
- 批量操作优化
- 增量索引更新

## 故障排除

### 常见问题

1. **虚拟环境激活失败**
   - 确保Python版本 >= 3.9
   - 检查PATH环境变量

2. **依赖安装失败**
   - 更新pip: `pip install --upgrade pip`
   - 检查网络连接
   - 尝试使用国内镜像源

3. **数据库连接失败**
   - 检查DATABASE_URL配置
   - 确保目录权限正确

4. **AI模型加载失败**
   - 检查模型目录权限
   - 确保有足够的内存和磁盘空间
   - 查看详细错误日志

### 日志调试

```bash
# 启用调试日志
DEBUG=True python main.py

# 查看详细错误信息
uvicorn main:app --log-level debug
```

## 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见[LICENSE](../LICENSE)文件。

## 支持

如有问题或建议，请：

1. 查看[API文档](http://127.0.0.1:8000/docs)
2. 搜索现有的[Issues](../../issues)
3. 创建新的Issue描述问题

---

**注意**: 这是小遥搜索项目的后端服务，需要配合前端Electron应用使用。