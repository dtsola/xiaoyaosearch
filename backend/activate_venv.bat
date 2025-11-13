@echo off
echo 正在激活小遥搜索后端虚拟环境...
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
    echo 虚拟环境创建完成！
)

call venv\Scripts\activate.bat

echo.
echo ✅ 虚拟环境已激活！
echo 🐍 Python版本：
python --version
echo 📦 当前已安装的包：
pip list | findstr /C:"fastapi" /C:"sqlalchemy" /C:"uvicorn"
echo.
echo 💡 提示：
echo - 运行 'python main.py' 启动后端服务
echo - 运行 'pip install package_name' 安装新包
echo - 运行 'deactivate' 退出虚拟环境
echo.

cmd /k