#!/bin/bash

# 小遥搜索桌面应用构建脚本
# 支持 Windows、macOS、Linux 三个平台的构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查必要工具
check_tools() {
    log "$BLUE" "🔧 检查构建工具..."

    if ! command -v node &> /dev/null; then
        log "$RED" "❌ Node.js 未安装"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        log "$RED" "❌ npm 未安装"
        exit 1
    fi

    log "$GREEN" "✅ 构建工具检查通过"
}

# 检查必要文件
check_files() {
    log "$BLUE" "📁 检查必要文件..."

    local required_files=(
        "../backend/main.py"
        "../backend/requirements.txt"
        "../backend/app"
        "../frontend/package.json"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "$RED" "❌ 缺少必要文件: $file"
            exit 1
        fi
    done

    log "$GREEN" "✅ 文件检查通过"
}

# 清理构建目录
clean_build() {
    log "$YELLOW" "🧹 清理旧的构建文件..."

    cd frontend

    local dirs_to_clean=("dist" "release")

    for dir in "${dirs_to_clean[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            log "$CYAN" "  清理目录: $dir"
        fi
    done

    cd ..
    log "$GREEN" "✅ 构建目录清理完成"
}

# 安装依赖
install_deps() {
    log "$YELLOW" "📦 安装依赖..."

    cd frontend

    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        npm ci
    fi

    cd ..
    log "$GREEN" "✅ 依赖安装完成"
}

# 构建 React 应用
build_react() {
    log "$YELLOW" "🔨 构建 React 应用..."

    cd frontend

    npm run build:renderer
    npm run build:main

    cd ..
    log "$GREEN" "✅ React 应用构建完成"
}

# 构建特定平台
build_platform() {
    local platform=$1

    log "$CYAN" "🚀 开始构建 $platform 平台..."

    cd frontend

    case $platform in
        "windows")
            if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" && "$OSTYPE" != "cygwin" ]]; then
                log "$YELLOW" "⚠️  跳过 Windows 平台构建（非 Windows 环境）"
                cd ..
                return
            fi
            npm run build:win
            ;;
        "macos")
            if [[ "$OSTYPE" != "darwin"* ]]; then
                log "$YELLOW" "⚠️  跳过 macOS 平台构建（非 macOS 环境）"
                cd ..
                return
            fi
            npm run build:mac
            ;;
        "linux")
            npm run build:linux
            ;;
        *)
            log "$RED" "❌ 不支持的平台: $platform"
            cd ..
            exit 1
            ;;
    esac

    cd ..
    log "$GREEN" "✅ $platform 平台构建完成"
}

# 显示构建结果
show_results() {
    log "$CYAN" "📁 构建结果:"

    if [[ -d "frontend/release" ]]; then
        local files=($(ls -1 frontend/release/ 2>/dev/null || true))

        if [[ ${#files[@]} -eq 0 ]]; then
            log "$YELLOW" "  ⚠️  没有找到构建文件"
            return
        fi

        for file in "${files[@]}"; do
            local filepath="frontend/release/$file"
            if [[ -f "$filepath" ]]; then
                if command -v stat &> /dev/null; then
                    local size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null || echo "unknown")
                    local size_mb=$((size / 1024 / 1024))
                    log "$NC" "  📦 $file (${size_mb} MB)"
                else
                    log "$NC" "  📦 $file"
                fi
            fi
        done
    else
        log "$YELLOW" "  ⚠️  release 目录不存在"
    fi

    # 生成校验和
    generate_checksums
}

# 生成校验和
generate_checksums() {
    log "$YELLOW" "🔐 生成校验和..."

    cd frontend/release

    if [[ ! -f "checksums.txt" ]]; then
        if command -v sha256sum &> /dev/null; then
            sha256sum * > checksums.txt 2>/dev/null || true
            log "$GREEN" "✅ 校验和文件生成完成: checksums.txt"
        elif command -v shasum &> /dev/null; then
            shasum -a 256 * > checksums.txt 2>/dev/null || true
            log "$GREEN" "✅ 校验和文件生成完成: checksums.txt"
        else
            log "$YELLOW" "⚠️  无法生成校验和（缺少 sha256sum 或 shasum 命令）"
        fi
    else
        log "$CYAN" "ℹ️  校验和文件已存在"
    fi

    cd ../..
}

# 主函数
main() {
    local platform=${1:-"all"}

    log "$CYAN" "🎯 小遥搜索桌面应用构建器"
    log "$CYAN" "================================"

    check_tools
    check_files
    clean_build
    install_deps
    build_react

    if [[ "$platform" == "all" ]]; then
        log "$CYAN" "🔄 构建所有平台..."

        # 根据当前操作系统决定构建哪些平台
        case "$OSTYPE" in
            "msys"|"win32"|"cygwin")
                build_platform "windows"
                build_platform "linux"
                ;;
            "darwin"*)
                build_platform "macos"
                build_platform "linux"
                ;;
            "linux"*)
                build_platform "linux"
                if command -v wine &> /dev/null; then
                    build_platform "windows"
                else
                    log "$YELLOW" "⚠️  跳过 Windows 平台构建（需要 Wine）"
                fi
                ;;
            *)
                log "$RED" "❌ 不支持的操作系统: $OSTYPE"
                exit 1
                ;;
        esac

        log "$GREEN" "🎉 所有平台构建完成！"

    else
        build_platform "$platform"
        log "$GREEN" "🎉 桌面应用构建完成！"
    fi

    show_results

    log "$CYAN" ""
    log "$CYAN" "📝 后续步骤:"
    log "$NC" "1. 测试生成的安装包"
    log "$NC" "2. 上传到发布平台"
    log "$NC" "3. 创建发布说明"
}

# 错误处理
trap 'log "$RED" "❌ 构建过程中发生错误"; exit 1' ERR

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [platform]"
    echo ""
    echo "平台:"
    echo "  windows - 构建 Windows 应用"
    echo "  macos   - 构建 macOS 应用"
    echo "  linux   - 构建 Linux 应用"
    echo "  all     - 构建所有平台（默认）"
    echo ""
    echo "示例:"
    echo "  $0 windows"
    echo "  $0 linux"
    echo "  $0"
}

# 处理命令行参数
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "${1:-all}"
        ;;
esac