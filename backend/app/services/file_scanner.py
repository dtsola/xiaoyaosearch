"""
文件扫描服务

提供递归文件扫描功能，支持文件类型过滤、变更检测和增量扫描。
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Set, Dict, Optional, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    name: str
    size: int
    modified_time: datetime
    created_time: datetime
    extension: str
    mime_type: str
    content_hash: Optional[str] = None
    is_directory: bool = False


class FileScanner:
    """文件扫描器

    支持高效的文件扫描，包括：
    - 多线程并行扫描
    - 文件类型过滤
    - 基于哈希的变更检测
    - 增量扫描
    """

    # 默认支持的文件类型
    DEFAULT_SUPPORTED_EXTENSIONS = {
        # 文档类
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.md', '.rtf', '.odt', '.ods', '.odp',
        # 代码类
        '.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c',
        '.go', '.rs', '.php', '.rb', '.swift', '.kt',
        # 音频类
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
        # 视频类
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        # 图片类
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
        # 压缩包
        '.zip', '.rar', '.7z', '.tar', '.gz',
    }

    def __init__(
        self,
        max_workers: int = 4,
        chunk_size: int = 1024 * 1024,  # 1MB
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        supported_extensions: Optional[Set[str]] = None
    ):
        """初始化文件扫描器

        Args:
            max_workers: 线程池最大工作线程数
            chunk_size: 文件哈希计算的块大小
            max_file_size: 最大文件大小限制（字节）
            supported_extensions: 支持的文件扩展名集合
        """
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size
        self.supported_extensions = supported_extensions or self.DEFAULT_SUPPORTED_EXTENSIONS

        # 统计信息
        self.stats = {
            'total_files': 0,
            'supported_files': 0,
            'filtered_files': 0,
            'error_files': 0,
            'total_size': 0
        }

    def scan_directory(
        self,
        root_path: str,
        recursive: bool = True,
        include_hidden: bool = False,
        progress_callback: Optional[callable] = None
    ) -> List[FileInfo]:
        """扫描目录中的文件

        Args:
            root_path: 根目录路径
            recursive: 是否递归扫描子目录
            include_hidden: 是否包含隐藏文件
            progress_callback: 进度回调函数

        Returns:
            List[FileInfo]: 文件信息列表
        """
        logger.info(f"开始扫描目录: {root_path}")
        start_time = datetime.now()

        # 重置统计信息
        self._reset_stats()

        # 获取所有文件路径
        file_paths = list(self._walk_directory(
            root_path, recursive, include_hidden
        ))

        logger.info(f"发现 {len(file_paths)} 个文件，开始并行处理...")

        # 并行处理文件
        files = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_path = {
                executor.submit(self._process_file, path): path
                for path in file_paths
            }

            # 处理完成的任务
            completed = 0
            for future in as_completed(future_to_path):
                try:
                    file_info = future.result()
                    if file_info:
                        files.append(file_info)
                        self.stats['supported_files'] += 1
                    completed += 1

                    # 进度回调
                    if progress_callback:
                        progress_callback(completed, len(file_paths))

                except Exception as e:
                    path = future_to_path[future]
                    logger.error(f"处理文件失败 {path}: {e}")
                    self.stats['error_files'] += 1

        # 更新统计信息
        self.stats['total_files'] = len(file_paths)
        self.stats['total_size'] = sum(f.size for f in files)
        self.stats['filtered_files'] = len(file_paths) - self.stats['supported_files']

        duration = datetime.now() - start_time
        logger.info(f"扫描完成，耗时 {duration.total_seconds():.2f} 秒")
        logger.info(f"总文件: {self.stats['total_files']}, "
                   f"支持文件: {self.stats['supported_files']}, "
                   f"过滤文件: {self.stats['filtered_files']}, "
                   f"错误文件: {self.stats['error_files']}, "
                   f"总大小: {self.stats['total_size'] / 1024 / 1024:.2f} MB")

        return files

    def scan_changes(
        self,
        root_path: str,
        known_files: Dict[str, FileInfo],
        recursive: bool = True,
        include_hidden: bool = False
    ) -> Tuple[List[FileInfo], List[str], List[str]]:
        """扫描文件变更

        Args:
            root_path: 根目录路径
            known_files: 已知文件字典 {path: FileInfo}
            recursive: 是否递归扫描
            include_hidden: 是否包含隐藏文件

        Returns:
            Tuple[List[FileInfo], List[str], List[str]]:
                (新增/修改的文件, 删除的文件路径, 移动的文件路径)
        """
        logger.info(f"开始扫描文件变更: {root_path}")

        # 获取当前文件列表
        current_files = self.scan_directory(
            root_path, recursive, include_hidden
        )

        # 创建当前文件路径到文件信息的映射
        current_file_map = {f.path: f for f in current_files}
        known_file_map = {f.path: f for f in known_files.values()}

        # 查找删除的文件
        deleted_files = list(set(known_file_map.keys()) - set(current_file_map.keys()))

        # 查找新增和修改的文件
        changed_files = []
        for path, current_file in current_file_map.items():
            if path not in known_file_map:
                # 新文件
                changed_files.append(current_file)
            else:
                # 检查文件是否修改
                known_file = known_file_map[path]
                if (current_file.modified_time != known_file.modified_time or
                    current_file.size != known_file.size):
                    # 文件被修改，重新计算哈希
                    current_file.content_hash = self._calculate_file_hash(path)
                    changed_files.append(current_file)

        logger.info(f"变更扫描完成: 新增/修改 {len(changed_files)} 个文件, "
                   f"删除 {len(deleted_files)} 个文件")

        return changed_files, deleted_files, []

    def _walk_directory(
        self,
        root_path: str,
        recursive: bool,
        include_hidden: bool
    ) -> Generator[str, None, None]:
        """遍历目录生成文件路径"""
        try:
            root = Path(root_path)
            if not root.exists():
                logger.error(f"目录不存在: {root_path}")
                return

            pattern = "**/*" if recursive else "*"
            for path in root.glob(pattern):
                if not include_hidden and path.name.startswith('.'):
                    continue

                if path.is_file():
                    yield str(path.absolute())

        except Exception as e:
            logger.error(f"遍历目录失败 {root_path}: {e}")

    def _process_file(self, file_path: str) -> Optional[FileInfo]:
        """处理单个文件，提取基本信息"""
        try:
            path = Path(file_path)

            # 检查文件大小
            if path.stat().st_size > self.max_file_size:
                logger.debug(f"文件过大，跳过: {file_path}")
                return None

            # 检查文件扩展名
            extension = path.suffix.lower()
            if extension not in self.supported_extensions:
                return None

            # 获取文件信息
            stat = path.stat()
            mime_type, _ = mimetypes.guess_type(file_path)

            file_info = FileInfo(
                path=str(path.absolute()),
                name=path.name,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                created_time=datetime.fromtimestamp(stat.st_ctime),
                extension=extension,
                mime_type=mime_type or "application/octet-stream"
            )

            # 计算文件哈希（用于变更检测）
            file_info.content_hash = self._calculate_file_hash(file_path)

            return file_info

        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {e}")
            return None

    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """计算文件内容的SHA256哈希值"""
        try:
            hash_sha256 = hashlib.sha256()

            with open(file_path, 'rb') as f:
                # 分块读取文件，避免大文件内存问题
                while chunk := f.read(self.chunk_size):
                    hash_sha256.update(chunk)

            return hash_sha256.hexdigest()

        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return None

    def _reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_files': 0,
            'supported_files': 0,
            'filtered_files': 0,
            'error_files': 0,
            'total_size': 0
        }

    def get_stats(self) -> Dict[str, int]:
        """获取扫描统计信息"""
        return self.stats.copy()


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试文件扫描
    scanner = FileScanner(max_workers=2)

    # 扫描当前目录
    files = scanner.scan_directory(
        ".",
        recursive=True,
        include_hidden=False,
        progress_callback=lambda current, total: print(f"进度: {current}/{total}")
    )

    print(f"扫描到 {len(files)} 个支持的文件")
    print(f"统计信息: {scanner.get_stats()}")