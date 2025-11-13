# 小遥搜索 - 本地桌面应用部署文档

## 📋 目录

- [概述](#概述)
- [环境要求](#环境要求)
- [开发环境搭建](#开发环境搭建)
- [桌面应用构建](#桌面应用构建)
- [平台特定安装包](#平台特定安装包)
- [自动更新配置](#自动更新配置)
- [CI/CD 自动构建](#cicd-自动构建)
- [故障排除](#故障排除)

## 📖 概述

小遥搜索是一款本地桌面应用程序，采用 Electron + React + TypeScript 前端和 Python + FastAPI 后端的混合架构。应用完全运行在用户本地计算机上，无需外部服务器依赖。

### 🔧 技术架构
- **前端**: Electron + React + TypeScript + Vite (桌面应用界面)
- **后端**: Python 3.12+ + FastAPI + SQLAlchemy + SQLite (本地嵌入式服务)
- **数据库**: SQLite (本地文件数据库)
- **打包工具**: electron-builder (跨平台安装包生成)

### 🏗️ 应用架构
```
┌─────────────────────────────────────┐
│         Electron 主进程             │
│    ┌─────────────────────────────┐  │
│    │      React 渲染进程         │  │
│    │   (用户界面组件)            │  │
│    └─────────────────────────────┘  │
│             ↕ IPC 通信              │
│    ┌─────────────────────────────┐  │
│    │    Python 后端进程          │  │
│    │   (FastAPI + SQLite)        │  │
│    └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 🖥️ 环境要求

### 开发环境
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Node.js**: 18.0.0+ (推荐 LTS 版本)
- **Python**: 3.12.0+
- **Git**: 2.30.0+

### 用户环境（运行时要求）
- **Windows**: Windows 10/11 (x64)
- **macOS**: macOS 10.15+ (x64, Apple Silicon)
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+ (x64)

### 开发工具
- **IDE**: VSCode / WebStorm / PyCharm
- **包管理器**: npm 9.0.0+ / pip 24.0.0+

## 📊 环境策略对比

| 环境 | 构建方式 | 使用场景 | 构建速度 | 输出文件 | 部署方式 |
|------|----------|----------|----------|----------|----------|
| **Dev** | Web + API 分离开发 | 本地开发调试 | ⚡ 极快 | 无构建产物 | 本地运行 |
| **Test** | Windows exe 打包 | 功能测试、用户验证 | 🐢 中等 | Windows 安装包 | 手动安装测试 |
| **Release** | GitHub Actions 多平台构建 | 生产发布、用户分发 | 🚀 较慢 | 全平台安装包 | GitHub Releases |

### 快速使用指南

#### 开发者
```bash
# 启动开发环境
npm run dev
# 访问 http://localhost:3000 开始开发
```

#### 测试人员
```bash
# 构建 Windows 测试版本（本地打包）
npm run build:test
# 在 release/test/ 目录找到 .exe 安装包

# 或者直接使用本地构建脚本
npm run build:test:win
```

#### 发布版本
```bash
# 推送版本标签触发自动构建
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions 自动构建多平台安装包
```

## 🛠️ 开发环境搭建

### 1. 克隆项目
```bash
git clone https://github.com/xiaoyaosearch/xiaoyao-search.git
cd xiaoyao-search
```

### 2. 后端环境配置

#### 2.1 创建 Python 虚拟环境
```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate

# Linux/macOS
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装后端依赖
```bash
# 激活虚拟环境后
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 快速启动脚本（推荐）
```bash
# Windows
cd backend
activate_venv.bat

# 启动后端服务
python main.py
```

### 3. 前端环境配置

#### 3.1 安装前端依赖
```bash
# 直接进入前端目录
cd frontend
npm install
```

#### 3.2 开发模式启动
```bash
# 方法 1: Web 开发模式（调试用）
cd frontend
npm run dev:renderer

# 方法 2: Electron 开发模式
cd frontend
npm run dev

# 方法 3: 使用快速启动脚本
frontend/start-web-dev.bat  # Windows
frontend/start-web-dev.sh   # Linux/macOS
```

### 4. 完整开发环境启动
```bash
# 根目录执行（同时启动前后端）
npm run dev

# 或分别启动
npm run dev:backend  # 后端服务 (端口 8000)
npm run dev:frontend # 前端 Electron
```

## 📦 桌面应用构建

小遥搜索根据不同环境采用不同的构建策略：

### 🏗️ 环境构建策略

#### 🔧 Dev 开发环境
**目标**: 快速开发和调试
**方式**: Web 前端 + 后端接口分离开发
```bash
# 启动开发环境（推荐）
npm run dev

# 或分别启动
npm run dev:backend   # 后端 FastAPI 服务 (端口 8000)
npm run dev:frontend  # 前端 Vite 开发服务器 (端口 3000)
```

**特点**:
- 前端使用 Vite 热重载，修改代码即时生效
- 后端使用 uvicorn 重载，API 修改自动重启
- 支持浏览器开发者工具调试
- 无需打包，启动速度快

#### 🧪 Test 测试环境
**目标**: 生成 Windows 可执行文件进行功能测试
**方式**: 本地打包为 Windows exe 安装包
```bash
# 测试环境打包（仅 Windows，本地构建）
npm run build:test
# 或
npm run build:test:win

# 使用构建脚本（支持自定义输出目录）
node frontend/build-scripts.js windows --local --output-dir=release/test

# 或使用批处理脚本（Windows）
scripts\build-desktop.bat windows --local
```

**输出文件**:
- `release/test/XiaoyaoSearch Setup x.x.x.exe` - 安装包
- `release/test/XiaoyaoSearch-x.x.x.exe` - 便携版
- `release/test/checksums.txt` - 校验和文件

**特点**:
- 本地构建，无需依赖 GitHub Actions
- 仅打包 Windows 版本，提高构建效率
- 输出到 `release/test/` 目录，与生产构建分离
- 包含完整的前后端，模拟生产环境
- 适合功能测试和用户体验验证
- 生成安装包便于分发测试
- 自动设置测试环境变量配置

#### 🚀 Release 生产环境
**目标**: 多平台发布包，通过 GitHub Actions 自动构建
**方式**: GitHub Actions CI/CD 多平台自动构建
```bash
# 本地手动构建（不推荐，仅用于调试）
npm run build:desktop:all
npm run release

# 生产环境主要使用 GitHub Actions
git tag v1.0.0
git push origin v1.0.0
```

**GitHub Actions 自动构建**:
```yaml
# 触发方式
# 1. 推送版本标签: git tag v1.0.0 && git push origin v1.0.0
# 2. 创建 GitHub Release
```

**输出文件**:
- **Windows**: `XiaoyaoSearch Setup x.x.x.exe` (NSIS 安装包)
- **macOS**: `XiaoyaoSearch-x.x.x.dmg` (磁盘镜像)
- **Linux**: `XiaoyaoSearch-x.x.x.AppImage` (便携应用)

### 1. 构建准备

#### 1.1 安装构建依赖
```bash
cd frontend
npm ci --production
```

#### 1.2 环境变量配置

小遥搜索为前端和后端分别提供了完整的环境变量配置：

##### 前端环境变量 (frontend/)
- `.env.development` - 开发环境配置
- `.env.test` - 测试环境配置
- `.env.production` - 生产环境配置

##### 后端环境变量 (backend/)
- `.env.development` - 开发环境配置
- `.env.test` - 测试环境配置
- `.env.production` - 生产环境配置

##### 环境切换命令
```bash
# 切换到开发环境
npm run env:dev

# 切换到测试环境
npm run env:test

# 切换到生产环境
npm run env:prod

# 或单独设置前端/后端环境
npm run env:dev:frontend
npm run env:test:backend

# 使用脚本手动设置
# Windows
scripts\set-env.bat frontend development

# Linux/macOS
./scripts/set-env.sh backend test
```

##### 主要环境变量说明

**前端变量**:
- `NODE_ENV`: 环境类型 (development/test/production)
- `VITE_API_BASE_URL`: 后端服务地址
- `VITE_LOG_LEVEL`: 日志级别
- `VITE_ENABLE_DEVTOOLS`: 是否开启开发者工具
- `VITE_UPDATE_CHECK_ENABLED`: 是否启用自动更新

**后端变量**:
- `DEBUG`: 是否启用调试模式
- `HOST/PORT`: 服务监听地址和端口
- `LOG_LEVEL`: 日志级别
- `DATABASE_URL`: 数据库连接
- `CORS_ORIGINS`: CORS 允许的源
- `API_RATE_LIMIT`: API 速率限制

#### 1.3 electron-builder 配置
当前配置在 `frontend/package.json` 的 `build` 部分：

```json
{
  "build": {
    "appId": "com.xiaoyaosearch.app",
    "productName": "小遥搜索",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "package.json"
    ],
    "extraResources": [
      {
        "from": "../backend",
        "to": "backend",
        "filter": [
          "**/*",
          "!venv/**/*",
          "!__pycache__/**/*",
          "!*.pyc",
          "!*.pyo",
          ".env"
        ]
      }
    ]
  }
}
```

### 2. 平台特定构建

#### 2.1 Windows 构建（测试/生产）
```bash
# 基础构建（所有架构）
npm run build:win

# 指定架构
npm run build:win:x64
npm run build:win:ia32

# 仅安装包
npm run build:win -- --win nsis

# 仅便携版
npm run build:win -- --win portable

# 测试环境快速构建
npm run build:test

# 输出文件
# - release/XiaoyaoSearch Setup x.x.x.exe
# - release/XiaoyaoSearch-x.x.x.exe (便携版)
```

#### 2.2 macOS 构建（仅生产环境）
```bash
# 基础构建（所有架构）
npm run build:mac

# 指定架构
npm run build:mac:x64
npm run build:mac:arm64

# 仅 DMG
npm run build:mac -- --mac dmg

# 输出文件
# - release/XiaoyaoSearch-x.x.x.dmg
# - release/XiaoyaoSearch-x.x.x-arm64.dmg
```

#### 2.3 Linux 构建（仅生产环境）
```bash
# 基础构建
npm run build:linux

# 指定格式
npm run build:linux -- --linux AppImage
npm run build:linux -- --linux deb

# 输出文件
# - release/XiaoyaoSearch-x.x.x.AppImage
# - release/xiaoyaosearch_x.x.x_amd64.deb
```

### 3. 自动化构建脚本

#### 3.1 使用项目脚本
```bash
# 根目录执行
npm run build:test          # 测试环境构建 (Windows, 本地打包)
npm run build:test:win      # 测试环境构建 (Windows, 本地打包)
npm run build:desktop       # 生产环境构建 (所有平台)
npm run pack                # 同 build:desktop
npm run release             # 完整构建和打包流程

# 前端目录执行
cd frontend
node build-scripts.js windows    # Windows 构建脚本
node build-scripts.js windows --local --output-dir=release/test  # 测试环境构建
node build-scripts.js all        # 所有平台构建
```

#### 3.2 跨平台脚本
```bash
# Linux/macOS
./scripts/build-desktop.sh windows

# Windows
.\scripts\build-desktop.bat windows
```

#### 3.3 构建结果验证
```bash
# 查看测试环境构建结果
ls -la release/test/

# 查看生产环境构建结果
ls -la frontend/release/

# 验证校验和（测试环境）
cd release/test
sha256sum -c checksums.txt  # Linux/macOS
certutil -hashfile *.exe SHA256  # Windows

# 验证校验和（生产环境）
cd frontend/release
sha256sum -c checksums.txt  # Linux/macOS
certutil -hashfile *.exe SHA256  # Windows
```

### 3. 构建脚本示例

创建 `frontend/build-scripts.js`：

```javascript
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 构建配置
const buildConfig = {
  windows: {
    targets: [
      { target: 'nsis', arch: ['x64'] },
      { target: 'portable', arch: ['x64'] }
    ]
  },
  macos: {
    targets: [
      { target: 'dmg', arch: ['x64', 'arm64'] }
    ]
  },
  linux: {
    targets: [
      { target: 'AppImage', arch: ['x64'] },
      { target: 'deb', arch: ['x64'] }
    ]
  }
};

// 构建函数
async function build(platform) {
  console.log(`🚀 开始构建 ${platform} 平台...`);

  const config = buildConfig[platform];
  const targets = config.targets.map(t => `${t.target}-${t.arch.join(',')}`).join(',');

  try {
    execSync(`npm run build:renderer`, { stdio: 'inherit' });
    execSync(`npm run build:main`, { stdio: 'inherit' });
    execSync(`electron-builder --${platform} --${targets}`, { stdio: 'inherit' });

    console.log(`✅ ${platform} 平台构建完成！`);
  } catch (error) {
    console.error(`❌ ${platform} 平台构建失败:`, error.message);
    process.exit(1);
  }
}

// 命令行参数
const platform = process.argv[2];
if (!platform || !buildConfig[platform]) {
  console.error('请指定构建平台: windows, macos, linux');
  process.exit(1);
}

build(platform);
```

## 🎯 平台特定安装包

### Windows 安装包

#### NSIS 安装程序配置
```json
{
  "win": {
    "target": [
      {
        "target": "nsis",
        "arch": ["x64", "ia32"]
      },
      {
        "target": "portable",
        "arch": ["x64"]
      }
    ],
    "icon": "assets/icon.ico"
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "allowElevation": true,
    "installerIcon": "assets/installer.ico",
    "uninstallerIcon": "assets/uninstaller.ico",
    "installerHeaderIcon": "assets/header.ico",
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true,
    "shortcutName": "小遥搜索",
    "language": "2052"
  }
}
```

#### Windows 代码签名（可选）
```json
{
  "win": {
    "certificateFile": "certs/certificate.p12",
    "certificatePassword": "your-password",
    "publisherName": "XiaoyaoSearch Team"
  }
}
```

### macOS 安装包

#### DMG 配置
```json
{
  "mac": {
    "target": [
      {
        "target": "dmg",
        "arch": ["x64", "arm64"]
      },
      {
        "target": "zip",
        "arch": ["x64", "arm64"]
      }
    ],
    "icon": "assets/icon.icns",
    "category": "public.app-category.productivity",
    "darkModeSupport": true
  },
  "dmg": {
    "title": "${productName} ${version}",
    "icon": "assets/dmg-icon.icns",
    "background": "assets/dmg-background.png",
    "contents": [
      {
        "x": 130,
        "y": 220
      },
      {
        "x": 410,
        "y": 220,
        "type": "link",
        "path": "/Applications"
      }
    ]
  }
}
```

#### macOS 代码签名（可选）
```json
{
  "mac": {
    "identity": "Developer ID Application: Your Name",
    "hardenedRuntime": true,
    "entitlements": "assets/entitlements.mac.plist",
    "entitlementsInherit": "assets/entitlements.mac.plist"
  }
}
```

### Linux 安装包

#### Linux 配置
```json
{
  "linux": {
    "target": [
      {
        "target": "AppImage",
        "arch": ["x64"]
      },
      {
        "target": "deb",
        "arch": ["x64"]
      },
      {
        "target": "rpm",
        "arch": ["x64"]
      }
    ],
    "icon": "assets/icon.png",
    "category": "Utility"
  },
  "deb": {
    "depends": [
      "libgtk-3-0",
      "libnotify4",
      "libnss3",
      "libxss1",
      "libxtst6",
      "xdg-utils",
      "libatspi2.0-0",
      "libdrm2",
      "libxcomposite1",
      "libxdamage1",
      "libxrandr2",
      "libgbm1",
      "libxkbcommon0",
      "libasound2"
    ]
  }
}
```

## 🔄 自动更新配置

### electron-updater 配置

#### 1. 更新服务器设置
```javascript
// frontend/src/main/updater.ts
import { autoUpdater } from 'electron-updater';
import { app, dialog } from 'electron';

export class AppUpdater {
  constructor() {
    autoUpdater.checkForUpdatesAndNotify();
    this.initEventHandlers();
  }

  private initEventHandlers() {
    autoUpdater.on('checking-for-update', () => {
      console.log('正在检查更新...');
    });

    autoUpdater.on('update-available', (info) => {
      console.log('发现新版本:', info.version);
    });

    autoUpdater.on('update-not-available', (info) => {
      console.log('当前已是最新版本');
    });

    autoUpdater.on('error', (err) => {
      console.error('更新检查失败:', err);
    });

    autoUpdater.on('download-progress', (progressObj) => {
      let log_message = "下载速度: " + progressObj.bytesPerSecond;
      log_message = log_message + ' - 已下载 ' + progressObj.percent + '%';
      log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
      console.log(log_message);
    });

    autoUpdater.on('update-downloaded', (info) => {
      console.log('更新下载完成');
      this.showUpdateDialog();
    });
  }

  private showUpdateDialog() {
    dialog.showMessageBox({
      type: 'info',
      title: '应用更新',
      message: '新版本已下载完成',
      detail: '应用将重启以完成更新',
      buttons: ['立即重启', '稍后重启']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  }
}
```

#### 2. 更新服务器配置
```json
{
  "publish": [
    {
      "provider": "github",
      "owner": "xiaoyaosearch",
      "repo": "xiaoyao-search"
    }
  ]
}
```

### 更新检查脚本
```javascript
// frontend/src/main/check-updater.ts
import { app } from 'electron';
import { AppUpdater } from './updater';

export function setupUpdater() {
  if (process.env.NODE_ENV === 'production') {
    // 生产环境下启用自动更新
    new AppUpdater();
  } else {
    // 开发环境下禁用自动更新
    console.log('开发环境，自动更新已禁用');
  }
}
```

## 🔄 CI/CD 自动构建

### GitHub Actions 工作流

小遥搜索的 CI/CD 策略：
- **Release 环境**: 推送版本标签时自动构建多平台安装包
- **Test 环境**: 通过 Pull Request 触发 Windows 测试构建
- **Dev 环境**: 本地开发，不使用 CI/CD

#### 1. 生产环境构建（Release）
```yaml
# .github/workflows/release.yml
name: Release Desktop App

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    runs-on: ${{ matrix.os }}

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Install backend dependencies
      run: |
        cd backend
        python -m venv venv
        source venv/bin/activate || venv\\Scripts\\activate
        pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci

    - name: Build application
      run: |
        cd frontend
        npm run build:renderer
        npm run build:main
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Build desktop app
      run: |
        cd frontend
        npm run build
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: desktop-app-${{ matrix.os }}
        path: frontend/release/

    - name: Release
      uses: softprops/action-gh-release@v1
      if: startsWith(github.ref, 'refs/tags/')
      with:
        files: frontend/release/*
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 2. 测试环境构建（Test）
```yaml
# .github/workflows/test-build.yml
name: Test Build Windows

on:
  pull_request:
    branches: [main, develop]
    paths: ['frontend/**', 'backend/**']

jobs:
  test-build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Install backend dependencies
      run: |
        cd backend
        python -m venv venv
        venv\Scripts\activate
        pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci

    - name: Build test application (Windows only)
      run: |
        cd frontend
        npm run build:renderer
        npm run build:main
        npm run build:win

    - name: Upload test artifacts
      uses: actions/upload-artifact@v3
      with:
        name: test-windows-build
        path: frontend/release/
        retention-days: 7

    - name: Test application startup
      run: |
        cd frontend/release
        dir *.exe
        echo "Windows 测试构建完成"
```

#### 3. 发布到 GitHub Releases
生产环境的自动发布通过 `release.yml` 工作流的最后一步完成：
- 自动创建 GitHub Release
- 上传所有平台的安装包
- 生成校验和文件

### 构建脚本优化

#### 跨平台构建脚本
```bash
#!/bin/bash
# scripts/build-all.sh

set -e

echo "🚀 开始构建全平台桌面应用..."

# 清理旧的构建文件
rm -rf frontend/release

# 安装依赖
echo "📦 安装依赖..."
cd frontend
npm ci

# 构建渲染进程和主进程
echo "🔨 构建 React 应用..."
npm run build:renderer
npm run build:main

# 构建所有平台
echo "📦 构建安装包..."
electron-builder --publish never

# 显示构建结果
echo "✅ 构建完成！"
echo "📁 构建文件位置:"
ls -la frontend/release/

# 生成校验和
echo "🔐 生成校验和..."
cd frontend/release
sha256sum * > checksums.txt
echo "📄 校验和文件: checksums.txt"
```

## 🔧 故障排除

### 常见问题

#### 1. 应用启动失败
```bash
# 检查 Electron 进程
ps aux | grep electron

# 检查 Python 后端进程
ps aux | grep python

# 查看应用日志
# Windows: %APPDATA%/xiaoyao-search/logs/
# macOS: ~/Library/Logs/xiaoyao-search/
# Linux: ~/.config/xiaoyao-search/logs/
```

#### 2. 构建失败
```bash
# 清理构建缓存
cd frontend
rm -rf node_modules dist release
npm install

# 重新构建
npm run build:renderer
npm run build:main
npm run build
```

#### 3. Python 后端连接问题
```bash
# 检查虚拟环境
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
python --version

# 检查依赖
pip list

# 手动启动后端测试
python main.py
```

#### 4. 权限问题
```bash
# Linux/macOS: 确保可执行权限
chmod +x backend/activate_venv.bat
chmod +x frontend/start-web-dev.sh

# Windows: 以管理员身份运行
# 右键应用图标 -> "以管理员身份运行"
```

### 调试技巧

#### 1. 开发者工具
```javascript
// 在 Electron 主进程中开启开发者工具
mainWindow.webContents.openDevTools();
```

#### 2. 后端调试
```python
# 在 backend/main.py 中添加调试配置
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式
        log_level="debug"
    )
```

#### 3. 进程管理
```javascript
// 检查进程状态
const { spawn } = require('child_process');

// 启动 Python 后端
const backendProcess = spawn('python', ['main.py'], {
  cwd: path.join(__dirname, '../backend'),
  stdio: 'inherit'
});

backendProcess.on('error', (error) => {
  console.error('后端启动失败:', error);
});

backendProcess.on('close', (code) => {
  console.log(`后端进程退出，代码: ${code}`);
});
```

## 📊 性能优化

### 应用优化
- 使用 `electron-builder` 的压缩选项减小安装包体积
- 启用代码分割减少初始加载时间
- 配置 SQLite 数据库连接池优化性能
- 使用 Electron 的 contextIsolation 提高安全性

### 资源管理
- 合理配置 Electron 进程模型
- 优化 SQLite 查询性能
- 实现适当的缓存策略
- 监控内存使用情况

---

## 📞 技术支持

如有部署问题，请通过以下方式获取支持：
- GitHub Issues: https://github.com/xiaoyaosearch/xiaoyao-search/issues
- 技术文档: https://docs.xiaoyao.local
- 社区讨论: https://discuss.xiaoyao.local