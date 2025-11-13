@echo off
echo 正在构建 xiaoyao-search-backend...

:: 检查是否在虚拟环境中
if not defined VIRTUAL_ENV (
    echo 错误：请先激活虚拟环境！
    echo 运行: venv\Scripts\activate
    pause
    exit /b 1
)

:: 安装 PyInstaller（如果尚未安装）
echo 检查 PyInstaller...
pip install pyinstaller

:: 清理之前的构建文件
echo 清理之前的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
:: spec 文件需要保留，不删除

:: 开始构建
echo 开始构建可执行文件...
pyinstaller build.spec

:: 检查构建结果
if exist "dist\xiaoyao-search-backend.exe" (
    echo.
    echo ✅ 构建成功！
    echo 可执行文件位置: dist\xiaoyao-search-backend.exe
    echo.
    echo 注意事项：
    echo 1. 请确保将 .env 文件复制到可执行文件相同目录
    echo 2. 首次运行可能需要初始化数据库
    echo 3. 如果遇到 "ModuleNotFoundError"，请检查 hiddenimports 配置
) else (
    echo.
    echo ❌ 构建失败！请检查错误信息。
)

pause