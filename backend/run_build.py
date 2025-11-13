#!/usr/bin/env python3
"""
构建脚本 - 用于打包 xiaoyao-search-backend 应用程序
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """检查构建要求"""
    print("检查构建要求...")

    # 检查虚拟环境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ 错误：请先激活虚拟环境！")
        print("运行: venv\\Scripts\\activate (Windows) 或 source venv/bin/activate (Linux/Mac)")
        return False

    # 检查必要文件
    if not Path("main.py").exists():
        print("❌ 错误：未找到 main.py 文件！")
        return False

    if not Path("requirements.txt").exists():
        print("❌ 错误：未找到 requirements.txt 文件！")
        return False

    print("✅ 构建要求检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("🔧 安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def clean_build():
    """清理之前的构建"""
    print("🧹 清理之前的构建文件...")
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.pyc', '*.pyo']

    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  删除目录: {dir_name}")

    for file_pattern in files_to_clean:
        for file_path in Path('.').glob(file_pattern):
            if file_path.is_file():
                file_path.unlink()
                print(f"  删除文件: {file_path}")

def build_app():
    """构建应用程序"""
    print("🚀 开始构建应用程序...")

    try:
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "build.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 构建成功！")
            return True
        else:
            print("❌ 构建失败！")
            print("错误输出:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ 构建过程中出现异常: {e}")
        return False

def verify_build():
    """验证构建结果"""
    print("✅ 验证构建结果...")

    if sys.platform == "win32":
        exe_path = Path("dist/xiaoyao-search-backend.exe")
    else:
        exe_path = Path("dist/xiaoyao-search-backend")

    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ 可执行文件已生成: {exe_path}")
        print(f"📁 文件大小: {file_size:.1f} MB")
        print("\n📝 使用说明:")
        print("1. 将 .env 文件复制到可执行文件相同目录")
        print("2. 首次运行可能需要初始化数据库")
        print("3. 如果遇到模块导入错误，请检查 hiddenimports 配置")
        print("4. 建议在目标系统上进行测试")
        return True
    else:
        print("❌ 可执行文件未找到！")
        return False

def main():
    """主函数"""
    print("🎯 xiaoyao-search-backend 构建工具")
    print("=" * 50)

    # 检查要求
    if not check_requirements():
        sys.exit(1)

    # 安装依赖
    print("\n📋 是否安装/更新依赖？(y/n): ", end="")
    response = input().strip().lower()
    if response in ['y', 'yes', '']:
        if not install_dependencies():
            sys.exit(1)

    # 安装 PyInstaller
    if not install_pyinstaller():
        sys.exit(1)

    # 清理构建
    clean_build()

    # 构建应用
    if not build_app():
        sys.exit(1)

    # 验证构建
    if not verify_build():
        sys.exit(1)

    print("\n🎉 构建完成！")

if __name__ == "__main__":
    main()