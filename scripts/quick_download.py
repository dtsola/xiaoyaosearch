#!/usr/bin/env python3
"""
快速模型下载脚本 - 使用wget直接下载到指定目录
"""

import os
import subprocess
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent

# 下载配置
DOWNLOADS = [
    {
        "name": "BGE-M3 模型文件",
        "files": [
            "https://hf-mirror.com/BAAI/bge-m3/resolve/main/pytorch_model.bin",
            "https://hf-mirror.com/BAAI/bge-m3/resolve/main/config.json",
            "https://hf-mirror.com/BAAI/bge-m3/resolve/main/tokenizer.json",
            "https://hf-mirror.com/BAAI/bge-m3/resolve/main/vocab.txt",
            "https://hf-mirror.com/BAAI/bge-m3/resolve/main/tokenizer_config.json"
        ],
        "target_dir": project_root / "data/models/embedding/BAAI/bge-m3"
    },
    {
        "name": "FasterWhisper 模型文件",
        "files": [
            "https://hf-mirror.com/Systran/faster-whisper-base/resolve/main/model.bin",
            "https://hf-mirror.com/Systran/faster-whisper-base/resolve/main/config.json",
            "https://hf-mirror.com/Systran/faster-whisper-base/resolve/main/tokenizer.json",
            "https://hf-mirror.com/Systran/faster-whisper-base/resolve/main/vocabulary.txt"
        ],
        "target_dir": project_root / "data/models/faster-whisper/Systran/faster-whisper-base"
    },
    {
        "name": "CN-CLIP 模型文件",
        "files": [
            "https://hf-mirror.com/OFA-Sys/chinese-clip-vit-base-patch16/resolve/main/pytorch_model.bin",
            "https://hf-mirror.com/OFA-Sys/chinese-clip-vit-base-patch16/resolve/main/config.json",
            "https://hf-mirror.com/OFA-Sys/chinese-clip-vit-base-patch16/resolve/main/preprocessor_config.json",
            "https://hf-mirror.com/OFA-Sys/chinese-clip-vit-base-patch16/resolve/main/tokenizer.json",
            "https://hf-mirror.com/OFA-Sys/chinese-clip-vit-base-patch16/resolve/main/vocab.txt"
        ],
        "target_dir": project_root / "data/models/cn-clip/OFA-Sys/chinese-clip-vit-base-patch16"
    }
]

def download_with_wget(url, target_dir):
    """使用wget下载文件"""
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = url.split('/')[-1]
    target_path = target_dir / filename

    try:
        # 使用wget下载，支持断点续传
        cmd = [
            "wget", "-c",  # 断点续传
            "-O", str(target_path),  # 输出文件
            "--progress=bar:force",  # 进度条
            url
        ]
        subprocess.run(cmd, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果wget不可用，使用curl
        try:
            cmd = [
                "curl", "-L",  # 跟随重定向
                "-o", str(target_path),  # 输出文件
                "--progress-bar",  # 进度条
                url
            ]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"[错误] 无法下载 {url}")
            return False

def main():
    print("开始快速下载AI模型...")
    print(f"   项目根目录: {project_root}")

    # 确保目录存在
    for download in DOWNLOADS:
        download["target_dir"].mkdir(parents=True, exist_ok=True)

    # 统计
    total_files = sum(len(d["files"]) for d in DOWNLOADS)
    success_count = 0

    # 开始下载
    for download in DOWNLOADS:
        print(f"\n下载 {download['name']}...")

        for url in download["files"]:
            filename = url.split('/')[-1]
            target_path = download["target_dir"] / filename

            # 检查文件是否已存在
            if target_path.exists():
                print(f"   [OK] {filename} (已存在，跳过)")
                success_count += 1
                continue

            print(f"   [下载] {filename}...")
            if download_with_wget(url, download["target_dir"]):
                print(f"   [OK] {filename}")
                success_count += 1
            else:
                print(f"   [失败] {filename} 下载失败")
                print(f"   [提示] 请手动下载: {url}")
                print(f"   [存放] 存放到: {target_path}")

    print(f"\n下载完成: {success_count}/{total_files}")

    if success_count == total_files:
        print("所有模型下载完成！")
        return 0
    else:
        print("部分文件需要手动下载，请查看上面的提示")
        return 1

if __name__ == "__main__":
    exit(main())