const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 颜色输出工具
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

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

// 检查必要文件
function checkRequiredFiles() {
  const requiredFiles = [
    '../backend/main.py',
    '../backend/requirements.txt',
    '../backend/app'
  ];

  for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
      log(`❌ 缺少必要文件: ${file}`, 'red');
      process.exit(1);
    }
  }
  log('✅ 所有必要文件检查通过', 'green');
}

// 清理构建目录
function cleanBuildDir() {
  log('🧹 清理旧的构建文件...', 'yellow');

  const dirsToClean = ['dist', 'release'];

  for (const dir of dirsToClean) {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true });
      log(`  清理目录: ${dir}`, 'cyan');
    }
  }

  log('✅ 构建目录清理完成', 'green');
}

// 安装依赖
function installDependencies() {
  log('📦 安装依赖...', 'yellow');

  try {
    execSync('npm ci', { stdio: 'inherit' });
    log('✅ 依赖安装完成', 'green');
  } catch (error) {
    log('❌ 依赖安装失败', 'red');
    process.exit(1);
  }
}

// 构建 React 应用
function buildReactApp() {
  log('🔨 构建 React 应用...', 'yellow');

  try {
    execSync('npm run build:renderer', { stdio: 'inherit' });
    execSync('npm run build:main', { stdio: 'inherit' });
    log('✅ React 应用构建完成', 'green');
  } catch (error) {
    log('❌ React 应用构建失败', 'red');
    process.exit(1);
  }
}

// 构建桌面应用
async function buildDesktopApp(platform, outputDir = 'release') {
  log(`🚀 开始构建 ${platform} 平台...`, 'cyan');

  const config = buildConfig[platform];
  if (!config) {
    log(`❌ 不支持的平台: ${platform}`, 'red');
    log('支持的平台: windows, macos, linux', 'yellow');
    process.exit(1);
  }

  // 确保 outputDir 存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    log(`📁 创建输出目录: ${outputDir}`, 'cyan');
  }

  // 构建 electron-builder 参数
  const targets = config.targets.map(t => {
    const archList = t.arch.join(',');
    return `${t.target}-${archList}`;
  }).join(' ');

  const buildCommand = `electron-builder --${platform} ${targets} --publish never --config.outputDir=${outputDir}`;

  try {
    log(`🔨 执行构建命令: ${buildCommand}`, 'blue');
    execSync(buildCommand, { stdio: 'inherit' });

    log(`✅ ${platform} 平台构建完成！`, 'green');

    // 显示构建结果
    showBuildResults(outputDir);

  } catch (error) {
    log(`❌ ${platform} 平台构建失败: ${error.message}`, 'red');
    process.exit(1);
  }
}

// 显示构建结果
function showBuildResults(outputDir = 'release') {
  log('📁 构建文件位置:', 'cyan');

  if (fs.existsSync(outputDir)) {
    const files = fs.readdirSync(outputDir);
    files.forEach(file => {
      const filePath = path.join(outputDir, file);
      const stats = fs.statSync(filePath);
      const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
      log(`  📦 ${file} (${sizeMB} MB)`, 'white');
    });
  }

  // 生成校验和文件
  generateChecksums(outputDir);
}

// 生成校验和
function generateChecksums(outputDir = 'release') {
  log('🔐 生成校验和...', 'yellow');

  try {
    const crypto = require('crypto');

    if (!fs.existsSync(outputDir)) {
      log(`⚠️  ${outputDir} 目录不存在，跳过校验和生成`, 'yellow');
      return;
    }

    const files = fs.readdirSync(outputDir)
      .filter(file => !file.startsWith('checksums'))
      .filter(file => fs.statSync(path.join(outputDir, file)).isFile());

    const checksums = [];

    for (const file of files) {
      const filePath = path.join(outputDir, file);
      const fileBuffer = fs.readFileSync(filePath);
      const hash = crypto.createHash('sha256').update(fileBuffer).digest('hex');
      checksums.push(`${hash}  ${file}`);
    }

    const checksumsPath = path.join(outputDir, 'checksums.txt');
    fs.writeFileSync(checksumsPath, checksums.join('\n'));

    log(`✅ 校验和文件生成完成: ${outputDir}/checksums.txt`, 'green');

  } catch (error) {
    log(`⚠️  校验和生成失败: ${error.message}`, 'yellow');
  }
}

// 解析命令行参数
function parseArguments() {
  const args = process.argv.slice(2);
  const options = {
    platform: null,
    local: false,
    outputDir: null
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--local':
        options.local = true;
        break;
      case '--output-dir':
        if (i + 1 < args.length) {
          options.outputDir = args[i + 1];
          i++; // 跳过下一个参数
        }
        break;
      default:
        if (!arg.startsWith('--')) {
          options.platform = arg;
        }
        break;
    }
  }

  return options;
}

// 主函数
async function main() {
  const options = parseArguments();

  log('🎯 小遥搜索桌面应用构建器', 'bright');
  log('================================', 'cyan');

  if (!options.platform) {
    log('使用方法: node build-scripts.js <platform> [选项]', 'yellow');
    log('支持的平台: windows, macos, linux, all', 'white');
    log('选项:', 'white');
    log('  --local              本地构建模式（用于测试环境）', 'white');
    log('  --output-dir <dir>   指定输出目录（默认: release）', 'white');
    process.exit(1);
  }

  // 如果是本地构建模式，设置环境变量
  if (options.local) {
    process.env.NODE_ENV = 'test';
    log('🔧 本地构建模式已启用，环境设置为 test', 'yellow');
  }

  // 设置输出目录
  const outputDir = options.outputDir || 'release';
  if (outputDir !== 'release') {
    log(`📁 输出目录设置为: ${outputDir}`, 'cyan');
  }

  if (options.platform === 'all') {
    // 构建所有平台
    const platforms = ['windows', 'macos', 'linux'];

    checkRequiredFiles();
    cleanBuildDir();
    installDependencies();
    buildReactApp();

    for (const p of platforms) {
      if (process.platform === 'win32' && p === 'macos') {
        log(`⚠️  跳过 ${p} 平台构建（在 Windows 上无法构建 macOS 应用）`, 'yellow');
        continue;
      }

      if (process.platform === 'darwin' && p === 'windows') {
        log(`⚠️  跳过 ${p} 平台构建（在 macOS 上无法构建 Windows 应用）`, 'yellow');
        continue;
      }

      await buildDesktopApp(p, outputDir);
    }

    log('🎉 所有平台构建完成！', 'green');

  } else {
    // 构建单个平台
    checkRequiredFiles();
    cleanBuildDir();
    installDependencies();
    buildReactApp();
    await buildDesktopApp(options.platform, outputDir);

    log('🎉 桌面应用构建完成！', 'green');
  }

  log('\n📝 后续步骤:', 'cyan');
  log('1. 测试生成的安装包', 'white');
  log('2. 上传到发布平台', 'white');
  log('3. 创建发布说明', 'white');
}

// 错误处理
process.on('uncaughtException', (error) => {
  log(`❌ 未捕获的异常: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  log(`❌ 未处理的 Promise 拒绝: ${reason}`, 'red');
  process.exit(1);
});

// 运行主函数
main().catch(error => {
  log(`❌ 构建失败: ${error.message}`, 'red');
  process.exit(1);
});