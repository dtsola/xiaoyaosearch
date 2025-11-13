# 后端虚拟环境设置指南

本项目使用Python虚拟环境来隔离后端依赖，避免与系统全局Python环境产生冲突。

## 🚀 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
```

### 2. 激活虚拟环境

**Windows:**
```cmd
# 命令行
venv\Scripts\activate.bat

# PowerShell
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 基础Web框架依赖
pip install fastapi uvicorn[standard] python-multipart sqlalchemy alembic

# 配置和工具库
pip install pydantic pydantic-settings httpx requests watchdog aiofiles python-dateutil pytz

# 日志和开发工具
pip install loguru rich pytest pytest-asyncio black mypy ruff

# 安全相关
pip install cryptography passlib[bcrypt] python-jose[cryptography]

# 其他工具
pip install click typer tqdm aiofiles
```

## 📁 项目结构

```
backend/
├── venv/                 # 虚拟环境目录
│   ├── Scripts/          # Windows可执行文件
│   ├── Lib/              # Python包
│   └── ...               # 其他虚拟环境文件
├── app/                  # 应用代码
├── requirements.txt      # 依赖列表
├── .env                 # 环境变量
└── main.py              # 应用入口
```

## 🔧 常用命令

### 开发模式启动后端

```bash
# 激活虚拟环境后
cd backend
venv\Scripts\activate
python main.py
```

### 依赖管理

```bash
# 安装新包
pip install package_name

# 导出依赖到文件
pip freeze > requirements.txt

# 从文件安装依赖
pip install -r requirements.txt

# 升级pip
python -m pip install --upgrade pip
```

### 开发工具

```bash
# 代码格式化
black .

# 代码检查
ruff check .

# 类型检查
mypy .

# 运行测试
pytest
```

## ⚠️ 注意事项

1. **每次开发前**：确保激活虚拟环境
2. **提交代码前**：更新requirements.txt
3. **协作开发**：不要提交venv目录到Git
4. **环境迁移**：使用requirements.txt复制环境

## 🐛 常见问题

### Q: 虚拟环境激活失败
A:
- Windows: 确保使用正确命令格式
- PowerShell: 可能需要执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### Q: pip版本过旧
A:
```bash
python -m pip install --upgrade pip
```

### Q: 依赖安装失败
A:
- 检查Python版本兼容性
- 使用国内镜像源：`pip install -i https://mirrors.aliyun.com/pypi/simple/ package_name`

## 📝 IDE配置

### VSCode
1. 安装Python扩展
2. 选择虚拟环境解释器：`backend/venv/Scripts/python.exe`
3. 配置settings.json：
```json
{
    "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.ruffEnabled": true
}
```

### PyCharm
1. File → Settings → Project → Python Interpreter
2. 选择：`backend/venv/Scripts/python.exe`
3. 应用并确定

## 🔄 更新流程

当添加新依赖时：

```bash
# 1. 激活虚拟环境
venv\Scripts\activate

# 2. 安装新包
pip install new_package

# 3. 更新requirements.txt
pip freeze > requirements.txt

# 4. 提交到版本控制
git add requirements.txt
git commit -m "🔧 chore: add new_package dependency"
```