@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 环境变量设置脚本 (Windows 版本)
:: 用法: scripts\set-env.bat [frontend|backend] [development|test|production]

echo 🔧 环境变量设置工具
echo ====================

:: 检查参数
if "%1"=="" goto :show_help
if "%2"=="" goto :show_help

set "SERVICE=%1"
set "ENVIRONMENT=%2"

:: 验证服务参数
if /i not "%SERVICE%"=="frontend" if /i not "%SERVICE%"=="backend" (
    echo ❌ 错误: 无效的服务 '%SERVICE%'
    goto :show_help
)

:: 验证环境参数
if /i not "%ENVIRONMENT%"=="development" if /i not "%ENVIRONMENT%"=="test" if /i not "%ENVIRONMENT%"=="production" (
    echo ❌ 错误: 无效的环境 '%ENVIRONMENT%'
    goto :show_help
)

:: 设置环境变量
set "ENV_FILE="
set "COPY_DEST="

if /i "%SERVICE%"=="frontend" (
    set "ENV_FILE=frontend\.env.%ENVIRONMENT%"
    set "COPY_DEST=frontend\.env"
) else (
    set "ENV_FILE=backend\.env.%ENVIRONMENT%"
    set "COPY_DEST=backend\.env"
)

:: 检查环境文件是否存在
if not exist "%ENV_FILE%" (
    echo ❌ 错误: 环境文件不存在: %ENV_FILE%
    goto :end_error
)

:: 复制环境文件
echo 🔄 设置 %SERVICE% 环境为: %ENVIRONMENT%
copy "%ENV_FILE%" "%COPY_DEST%" >nul

if %errorlevel% equ 0 (
    echo ✅ 环境变量设置成功
    echo 📁 配置文件: %ENV_FILE% -^> %COPY_DEST%
    echo.
    echo 📋 当前环境配置:

    if /i "%SERVICE%"=="frontend" (
        for /f "tokens=2 delims==" %%a in ('findstr /C:"NODE_ENV" "%COPY_DEST%"') do echo    NODE_ENV: %%a
        for /f "tokens=2 delims==" %%a in ('findstr /C:"VITE_API_BASE_URL" "%COPY_DEST%"') do echo    VITE_API_BASE_URL: %%a
        for /f "tokens=2 delims==" %%a in ('findstr /C:"VITE_LOG_LEVEL" "%COPY_DEST%"') do echo    VITE_LOG_LEVEL: %%a
    ) else (
        for /f "tokens=2 delims==" %%a in ('findstr /C:"DEBUG" "%COPY_DEST%"') do echo    DEBUG: %%a
        for /f "tokens=2 delims==" %%a in ('findstr /C:"HOST" "%COPY_DEST%"') do echo    HOST: %%a
        for /f "tokens=2 delims==" %%a in ('findstr /C:"PORT" "%COPY_DEST%"') do echo    PORT: %%a
    )

    echo.
    echo 💡 提示:
    if /i "%SERVICE%"=="frontend" (
        echo    请重新启动前端服务以应用新的环境变量
        echo    npm run dev:frontend
    ) else (
        echo    请重新启动后端服务以应用新的环境变量
        echo    npm run dev:backend
    )
) else (
    echo ❌ 环境变量设置失败
    goto :end_error
)

goto :end

:show_help
echo.
echo 使用方法: %0 ^<service^> ^<environment^>
echo.
echo 服务:
echo   frontend   - 设置前端环境变量
echo   backend    - 设置后端环境变量
echo.
echo 环境:
echo   development - 开发环境
echo   test        - 测试环境
echo   production  - 生产环境
echo.
echo 示例:
echo   %0 frontend development
echo   %0 backend test
echo.
goto :end

:end_error
exit /b 1

:end
exit /b 0