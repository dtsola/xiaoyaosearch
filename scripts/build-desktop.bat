@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 小遥搜索桌面应用构建脚本 (Windows 版本)

echo 🎯 小遥搜索桌面应用构建器
echo ================================

:: 检查参数
set PLATFORM=%1
if "%PLATFORM%"=="" set PLATFORM=all

if /i "%PLATFORM%"=="-h" goto :show_help
if /i "%PLATFORM%"=="--help" goto :show_help

:: 检查必要工具
echo 🔧 检查构建工具...

where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo ❌ npm 未安装
    pause
    exit /b 1
)

echo ✅ 构建工具检查通过

:: 检查必要文件
echo 📁 检查必要文件...

set "BACKEND_MAIN=..\backend\main.py"
set "BACKEND_REQS=..\backend\requirements.txt"
set "BACKEND_APP=..\backend\app"
set "FRONTEND_PACKAGE=..\frontend\package.json"

if not exist "%BACKEND_MAIN%" (
    echo ❌ 缺少必要文件: %BACKEND_MAIN%
    pause
    exit /b 1
)

if not exist "%BACKEND_REQS%" (
    echo ❌ 缺少必要文件: %BACKEND_REQS%
    pause
    exit /b 1
)

if not exist "%BACKEND_APP%" (
    echo ❌ 缺少必要文件: %BACKEND_APP%
    pause
    exit /b 1
)

if not exist "%FRONTEND_PACKAGE%" (
    echo ❌ 缺少必要文件: %FRONTEND_PACKAGE%
    pause
    exit /b 1
)

echo ✅ 文件检查通过

:: 清理构建目录
echo 🧹 清理旧的构建文件...

cd frontend

if exist "dist" (
    rmdir /s /q "dist"
    echo   清理目录: dist
)

if exist "release" (
    rmdir /s /q "release"
    echo   清理目录: release
)

cd ..
echo ✅ 构建目录清理完成

:: 安装依赖
echo 📦 安装依赖...

cd frontend
npm ci
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

cd ..
echo ✅ 依赖安装完成

:: 构建 React 应用
echo 🔨 构建 React 应用...

cd frontend
call npm run build:renderer
if errorlevel 1 (
    echo ❌ 渲染进程构建失败
    pause
    exit /b 1
)

call npm run build:main
if errorlevel 1 (
    echo ❌ 主进程构建失败
    pause
    exit /b 1
)

cd ..
echo ✅ React 应用构建完成

:: 构建指定平台
if /i "%PLATFORM%"=="all" goto :build_all
if /i "%PLATFORM%"=="windows" goto :build_windows
if /i "%PLATFORM%"=="linux" goto :build_linux

echo ❌ 不支持的平台: %PLATFORM%
echo 支持的平台: windows, linux, all
pause
exit /b 1

:build_all
echo 🔄 构建所有平台...

call :build_windows_internal
call :build_linux_internal

echo 🎉 所有平台构建完成！
goto :show_results

:build_windows
echo 🚀 开始构建 Windows 平台...
call :build_windows_internal
echo ✅ Windows 平台构建完成
goto :show_results

:build_linux
echo 🚀 开始构建 Linux 平台...
call :build_linux_internal
echo ✅ Linux 平台构建完成
goto :show_results

:build_windows_internal
cd frontend
call npm run build:win
if errorlevel 1 (
    echo ❌ Windows 平台构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
goto :eof

:build_linux_internal
cd frontend
call npm run build:linux
if errorlevel 1 (
    echo ❌ Linux 平台构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
goto :eof

:show_results
echo 📁 构建结果:

if exist "frontend\release" (
    echo.
    dir /b "frontend\release\*.exe" "frontend\release\*.msi" "frontend\release\*.dmg" "frontend\release\*.AppImage" "frontend\release\*.deb" 2>nul
    echo.

    :: 生成校验和
    echo 🔐 生成校验和...
    cd frontend\release

    if not exist "checksums.txt" (
        for %%f in (*) do (
            if /i not "%%f"=="checksums.txt" (
                powershell -Command "Get-FileHash -Path '%%f' -Algorithm SHA256 | Select-Object -ExpandProperty Hash" > temp_hash.txt
                set /p hash=<temp_hash.txt
                echo !hash!  %%f >> checksums.txt
                del temp_hash.txt
            )
        )
        echo ✅ 校验和文件生成完成: checksums.txt
    ) else (
        echo ℹ️  校验和文件已存在
    )

    cd ..\..
) else (
    echo ⚠️  release 目录不存在
)

echo.
echo 📝 后续步骤:
echo 1. 测试生成的安装包
echo 2. 上传到发布平台
echo 3. 创建发布说明
echo.
goto :end

:show_help
echo 使用方法: %0 [platform]
echo.
echo 平台:
echo   windows - 构建 Windows 应用
echo   linux   - 构建 Linux 应用
echo   all     - 构建所有平台（默认）
echo.
echo 示例:
echo   %0 windows
echo   %0 linux
echo   %0
echo.
goto :end

:end
pause