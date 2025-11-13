# 使用 PyInstaller 打包 xiaoyao-search-backend

本文档介绍如何使用 PyInstaller 将 xiaoyao-search-backend 打包成独立可执行文件。

## 📋 前置要求

1. **Python 环境**: Python 3.8+
2. **虚拟环境**: 已激活的 Python 虚拟环境
3. **依赖安装**: 所有项目依赖已安装

## 🚀 快速开始

### 方法一：使用自动化脚本（推荐）

1. **激活虚拟环境**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. **运行构建脚本**
   ```bash
   # Windows
   python run_build.py

   # 或者使用批处理脚本
   build.bat

   # Linux/Mac
   ./build.sh
   ```

### 方法二：手动使用 PyInstaller

1. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **运行构建命令**
   ```bash
   pyinstaller --clean build.spec
   ```

## 📁 构建结果

构建成功后，可执行文件位于：
- **Windows**: `dist/xiaoyao-search-backend.exe`
- **Linux/Mac**: `dist/xiaoyao-search-backend`

## ⚙️ 配置说明

### build.spec 文件说明

`build.spec` 是 PyInstaller 的配置文件，包含以下重要配置：

1. **主入口**: `main.py`
2. **数据文件**: 包含配置文件、迁移文件、源代码等
3. **隐藏导入**: 确保所有依赖库都被正确包含
4. **排除模块**: 排除不需要的模块以减小文件大小
5. **压缩选项**: 启用 UPX 压缩

### 常见问题解决

#### 1. ModuleNotFoundError
如果运行时出现模块找不到的错误，需要在 `build.spec` 的 `hiddenimports` 列表中添加缺失的模块：

```python
hiddenimports=[
    # 添加缺失的模块
    'your_missing_module',
],
```

#### 2. 文件过大
如果可执行文件过大，可以：
- 在 `excludes` 列表中添加更多不需要的模块
- 移除一些可选的 AI/ML 库（如果不使用的话）

#### 3. 运行时错误
- 确保 `.env` 文件在可执行文件相同目录
- 检查数据库文件路径是否正确
- 验证上传目录和索引目录的权限

## 🔧 高级配置

### 1. 自定义图标
在 `build.spec` 中添加图标配置：

```python
exe = EXE(
    # ... 其他配置
    icon='path/to/icon.ico',  # Windows
    # icon='path/to/icon.icns',  # Mac
)
```

### 2. 单文件模式
如果需要生成单个可执行文件，修改 `build.spec`：

```python
# 在 Analysis 中添加
datas=[],
# 确保所有必要文件都被包含

# 在 EXE 中
exe = EXE(
    # ...
    onefile=True,  # 启用单文件模式
)
```

### 3. 优化启动速度
- 使用 `--noconfirm` 参数跳过确认
- 预加载常用模块
- 考虑使用文件夹模式而非单文件模式

## 📦 部署说明

### Windows 部署
1. 将 `dist/xiaoyao-search-backend.exe` 复制到目标机器
2. 复制 `.env` 文件到相同目录
3. 运行可执行文件

### Linux/Mac 部署
1. 将 `dist/xiaoyao-search-backend` 复制到目标机器
2. 添加执行权限：`chmod +x xiaoyao-search-backend`
3. 复制 `.env` 文件到相同目录
4. 运行可执行文件

## 🧪 测试

### 本地测试
```bash
# 运行构建的可执行文件
./dist/xiaoyao-search-backend

# 测试 API
curl http://localhost:8000/health
```

### 集成测试
确保前端能正常连接打包后的后端服务。

## 📝 注意事项

1. **首次运行**: 可能需要初始化数据库和索引
2. **性能**: 打包后的应用启动速度可能比源码运行慢
3. **更新**: 代码更新后需要重新打包
4. **兼容性**: 在目标系统上进行测试以确保兼容性
5. **资源占用**: 包含 AI/ML 库会显著增加文件大小

## 🐛 故障排除

### 常见错误

1. **UPX 错误**
   ```bash
   # 在 build.spec 中禁用 UPX
   exe = EXE(
       # ...
       upx=False,
   )
   ```

2. **缺少 DLL 文件（Windows）**
   - 安装 Microsoft Visual C++ Redistributable
   - 或在 `datas` 中手动添加缺失的 DLL

3. **权限问题**
   - 确保有写入日志和数据库的权限
   - 检查上传目录的访问权限

### 调试技巧

1. **启用调试模式**：
   在 `build.spec` 中设置 `debug=True`

2. **查看详细日志**：
   在 `.env` 中设置 `LOG_LEVEL=DEBUG`

3. **检查导入**：
   使用 `--log-level DEBUG` 参数运行 PyInstaller

## 📚 参考资料

- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Python 打包最佳实践](https://packaging.python.org/)