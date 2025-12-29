@echo off
echo 🔨 构建小遥搜索高保真原型...
echo.

REM 检查Node.js是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Node.js，请先安装Node.js 16+
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

echo 🏗️  正在构建生产版本...
npm run build

if %errorlevel% equ 0 (
    echo ✅ 构建成功！
    echo 📁 输出目录：dist/
    echo 🌐 可以部署到任何静态文件服务器
) else (
    echo ❌ 构建失败
)

pause