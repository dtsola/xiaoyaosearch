@echo off
echo 🚀 启动小遥搜索高保真原型...
echo.

REM 检查Node.js是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Node.js，请先安装Node.js 16+
    echo 📥 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

REM 检查依赖是否安装
if not exist "node_modules" (
    echo 📦 正在安装依赖包...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

echo ✅ 环境检查完成
echo 🌐 启动开发服务器...
echo.
echo 📌 访问地址：http://localhost:5173
echo 🛑 按 Ctrl+C 停止服务
echo.

REM 启动开发服务器
npm run dev

pause