#!/bin/bash

# 环境变量设置脚本
# 用法: ./scripts/set-env.sh [frontend|backend] [development|test|production]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 <service> <environment>"
    echo ""
    echo "服务:"
    echo "  frontend   - 设置前端环境变量"
    echo "  backend    - 设置后端环境变量"
    echo ""
    echo "环境:"
    echo "  development - 开发环境"
    echo "  test        - 测试环境"
    echo "  production  - 生产环境"
    echo ""
    echo "示例:"
    echo "  $0 frontend development"
    echo "  $0 backend test"
}

# 检查参数
if [ $# -ne 2 ]; then
    show_help
    exit 1
fi

SERVICE=$1
ENVIRONMENT=$2

# 验证参数
case $SERVICE in
    frontend|backend) ;;
    *)
        log "$RED" "错误: 无效的服务 '$SERVICE'"
        show_help
        exit 1
        ;;
esac

case $ENVIRONMENT in
    development|test|production) ;;
    *)
        log "$RED" "错误: 无效的环境 '$ENVIRONMENT'"
        show_help
        exit 1
        ;;
esac

# 设置环境变量
ENV_FILE=""
COPY_DEST=""

case $SERVICE in
    frontend)
        ENV_FILE="frontend/.env.$ENVIRONMENT"
        COPY_DEST="frontend/.env"
        ;;
    backend)
        ENV_FILE="backend/.env.$ENVIRONMENT"
        COPY_DEST="backend/.env"
        ;;
esac

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    log "$RED" "错误: 环境文件不存在: $ENV_FILE"
    exit 1
fi

# 复制环境文件
log "$BLUE" "设置 $SERVICE 环境为: $ENVIRONMENT"
cp "$ENV_FILE" "$COPY_DEST"

if [ $? -eq 0 ]; then
    log "$GREEN" "✅ 环境变量设置成功"
    log "$CYAN" "配置文件: $ENV_FILE -> $COPY_DEST"

    # 显示当前环境信息
    echo ""
    log "$YELLOW" "当前环境配置:"
    if [ "$SERVICE" = "frontend" ]; then
        log "$NC" "NODE_ENV: $ENVIRONMENT"
        log "$NC" "VITE_API_BASE_URL: $(grep VITE_API_BASE_URL $COPY_DEST | cut -d'=' -f2)"
        log "$NC" "VITE_LOG_LEVEL: $(grep VITE_LOG_LEVEL $COPY_DEST | cut -d'=' -f2)"
    else
        log "$NC" "DEBUG: $(grep DEBUG $COPY_DEST | cut -d'=' -f2)"
        log "$NC" "HOST: $(grep HOST $COPY_DEST | cut -d'=' -f2)"
        log "$NC" "PORT: $(grep PORT $COPY_DEST | cut -d'=' -f2)"
    fi
else
    log "$RED" "❌ 环境变量设置失败"
    exit 1
fi

echo ""
log "$BLUE" "提示:"
if [ "$SERVICE" = "frontend" ]; then
    log "$NC" "请重新启动前端服务以应用新的环境变量"
    log "$NC" "npm run dev:frontend"
else
    log "$NC" "请重新启动后端服务以应用新的环境变量"
    log "$NC" "npm run dev:backend"
fi