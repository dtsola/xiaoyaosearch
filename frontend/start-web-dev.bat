@echo off
chcp 65001 >nul

echo 🚀 启动小遥搜索前端 Web 开发服务器...
echo.

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo 📦 安装前端依赖...
    npm install
    echo.
)

echo ✅ 启动 Vite 开发服务器...
echo 📍 访问地址: http://localhost:3000
echo ⏹️  按 Ctrl+C 停止服务器
echo.

REM 启动 Vite 开发服务器
npx vite --port 3000 --host