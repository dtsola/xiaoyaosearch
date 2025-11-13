#!/bin/bash

# 小遥搜索 - 前端 Web 开发启动脚本
# 用于快速启动 Web 开发服务器（不包括 Electron）

echo "🚀 启动小遥搜索前端 Web 开发服务器..."
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
    echo ""
fi

echo "✅ 启动 Vite 开发服务器..."
echo "📍 访问地址: http://localhost:3000"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

# 启动 Vite 开发服务器
npx vite --port 3000 --host