"""
语雀知识库数据源插件

基于 yuque-dl CLI 工具实现语雀文档同步。
"""

import asyncio
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.plugins.interface.datasource import DataSourcePlugin
from app.plugins.base import PluginStatus
from app.core.logging_config import logger


class YuqueDataSource(DataSourcePlugin):
    """语雀知识库数据源插件

    使用 yuque-dl CLI 工具将语雀文档同步到本地，
    支持增量下载、断点续传等功能。

    依赖要求：
    - Node.js 18.4+
    - yuque-dl (全局安装或 npx)
    """

    def __init__(self):
        super().__init__()
        self._yuque_dl_path: Optional[str] = None
        self._plugin_dir: Optional[Path] = None
        self._repos: List[Dict[str, Any]] = []
        self._sync_results: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "基于 yuque-dl 的语雀知识库文档同步",
            "datasource_type": "yuque",
            "dependencies": ["Node.js 18.4+", "yuque-dl"],
            "home_page": "https://www.dtsola.com"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件

        Args:
            config: 插件配置，包含：
                - repos: 知识库配置列表
                - yuque_dl_path: yuque-dl 路径（可选，自动检测）

        Returns:
            bool: 初始化是否成功
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent

            # 获取知识库配置列表
            self._repos = config.get("repos", [])
            if not self._repos:
                logger.warning("未配置任何知识库")
                self._set_error("未配置任何知识库")
                return False

            # 初始化每个知识库的下载目录
            for repo in self._repos:
                download_dir = self._plugin_dir / repo.get("download_dir", "./data/downloaded")
                download_dir.mkdir(parents=True, exist_ok=True)
                repo["_download_dir"] = download_dir
                logger.debug(f"知识库 {repo.get('name')} 下载目录: {download_dir}")

            # 检测 yuque-dl 工具
            self._yuque_dl_path = await self._find_yuque_dl()
            if not self._yuque_dl_path:
                error_msg = "未找到 yuque-dl 工具，请确保已安装 Node.js 和 yuque-dl"
                logger.error(error_msg)
                self._set_error(error_msg)
                return False

            logger.info(f"语雀数据源初始化成功，yuque-dl: {self._yuque_dl_path}")
            self._set_ready()
            return True

        except Exception as e:
            error_msg = f"语雀数据源初始化失败: {str(e)}"
            logger.error(error_msg)
            self._set_error(error_msg)
            return False

    async def _find_yuque_dl(self) -> Optional[str]:
        """查找 yuque-dl 可执行文件

        使用 shutil.which 查找命令，支持 Windows .cmd 文件。

        Returns:
            str: yuque-dl 完整命令路径，未找到返回 None
        """
        # shutil.which 会自动处理平台差异（Windows 上会查找 .cmd/.exe 等）
        yuque_dl_path = shutil.which("yuque-dl")
        if yuque_dl_path:
            logger.debug(f"找到 yuque-dl: {yuque_dl_path}")
            return yuque_dl_path

        # 尝试 npx
        npx_path = shutil.which("npx")
        if npx_path:
            # 测试 npx yuque-dl 是否可用
            try:
                result = subprocess.run(
                    [npx_path, "yuque-dl", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.debug(f"使用 npx 执行 yuque-dl: {npx_path}")
                    return npx_path
            except Exception:
                pass

        logger.warning("未找到 yuque-dl 工具")
        return None

    async def sync(self) -> bool:
        """同步所有配置的知识库

        对每个配置的知识库执行 yuque-dl 命令进行同步。

        Returns:
            bool: 同步是否全部成功
        """
        if not self.is_ready:
            logger.warning("插件未就绪，无法同步")
            return False

        all_success = True
        self._sync_results = {}

        for repo in self._repos:
            repo_name = repo.get("name", "unknown")
            logger.info(f"开始同步知识库: {repo_name}")

            try:
                result = await self._sync_repo(repo)
                self._sync_results[repo_name] = result

                if result["success"]:
                    logger.info(f"✅ 知识库 {repo_name} 同步成功: {result['message']}")
                else:
                    logger.error(f"❌ 知识库 {repo_name} 同步失败: {result['error']}")
                    all_success = False

            except Exception as e:
                error_msg = f"知识库 {repo_name} 同步异常: {str(e)}"
                logger.error(error_msg)
                self._sync_results[repo_name] = {
                    "success": False,
                    "error": error_msg
                }
                all_success = False

        return all_success

    async def _sync_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """同步单个知识库

        Args:
            repo: 知识库配置

        Returns:
            dict: 同步结果
        """
        repo_name = repo.get("name", "unknown")
        download_dir = repo.get("_download_dir")

        try:
            cmd = self._build_yuque_dl_command(repo)
            logger.info(f"执行命令: {' '.join(cmd)}")

            # 使用 asyncio.to_thread 在线程池中运行 subprocess.run
            # 这样可以正确处理 Windows 上的 .CMD 批处理文件
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    encoding='utf-8',  # 显式指定 UTF-8 编码
                    errors='ignore',    # 忽略无法解码的字符
                    timeout=300  # 5分钟超时
                )
            )

            output = result.stdout or ''
            error_output = result.stderr or ''

            logger.debug(f"命令返回码: {result.returncode}")
            logger.debug(f"命令输出: {output[:200] if output else '(空)'}")
            if error_output:
                logger.debug(f"命令错误: {error_output[:200]}")

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": error_output or output,
                    "returncode": result.returncode
                }

            # 解析输出，提取同步统计信息
            stats = self._parse_sync_output(output)

            return {
                "success": True,
                "message": f"同步了 {stats.get('files', 0)} 个文件",
                "stats": stats
            }

        except subprocess.TimeoutExpired:
            logger.error(f"同步超时: {repo_name}")
            return {
                "success": False,
                "error": "同步超时（超过5分钟）"
            }
        except Exception as e:
            logger.error(f"同步异常: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _build_yuque_dl_command(self, repo: Dict[str, Any]) -> List[str]:
        """构建 yuque-dl 命令

        Args:
            repo: 知识库配置

        Returns:
            list: 命令参数列表
        """
        cmd = []

        # 添加 yuque-dl 命令
        # 如果路径包含 npx，使用 npx 方式；否则直接使用 yuque-dl
        if "npx" in self._yuque_dl_path.lower():
            cmd.extend([self._yuque_dl_path, "yuque-dl"])
        else:
            cmd.append(self._yuque_dl_path)

        # 添加知识库 URL
        cmd.append(repo["url"])

        # 添加下载目录
        download_dir = repo.get("_download_dir")
        if download_dir:
            cmd.extend(["-d", str(download_dir)])

        # 添加 Token（如果提供）
        if repo.get("token"):
            cmd.extend(["-t", repo["token"]])

        # 添加其他选项
        if repo.get("ignore_images", False):
            cmd.append("--ignoreImg")

        # 注意：当前版本的 yuque-dl 不支持 --incremental 参数
        # yuque-dl 默认输出 Markdown 格式

        return cmd

    def _parse_sync_output(self, output: str) -> Dict[str, int]:
        """解析同步输出，提取统计信息

        Args:
            output: yuque-dl 命令输出

        Returns:
            dict: 统计信息 {files, errors, skipped}
        """
        stats = {"files": 0, "errors": 0, "skipped": 0}

        if not output:
            return stats

        # 解析输出中的文件数量
        # yuque-dl 输出格式示例: "Downloaded 10 files"
        file_match = re.search(r'(\d+)\s+files?', output, re.IGNORECASE)
        if file_match:
            stats["files"] = int(file_match.group(1))

        # 解析错误数量
        error_match = re.search(r'(\d+)\s+errors?', output, re.IGNORECASE)
        if error_match:
            stats["errors"] = int(error_match.group(1))

        return stats

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """获取文件的数据源信息

        从文件路径和内容中提取语雀文档的原始信息。

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            dict: 数据源信息
        """
        path_str = str(file_path).replace("\\", "/")

        # 检查是否属于此插件下载的文件
        if not self._plugin_dir:
            return {"source_type": None, "source_url": None, "source_id": None}

        plugin_dir_str = str(self._plugin_dir).replace("\\", "/")
        if plugin_dir_str not in path_str:
            return {"source_type": None, "source_url": None, "source_id": None}

        # 从文件内容提取原始 URL
        source_url = None
        source_id = None

        # yuque-dl 下载的文件包含原始链接信息
        # 格式示例: "原文: <https://www.yuque.com/org/repo/doc>"
        yuque_patterns = [
            r'原文:\s*<(https://www\.yuque\.com/[^>]+)>',
            r'Source:\s*<(https://www\.yuque\.com/[^>]+)>',
            r'originalUrl["\s:]+(https://www\.yuque\.com/[^"\s>]+)',
        ]

        for pattern in yuque_patterns:
            match = re.search(pattern, content)
            if match:
                source_url = match.group(1).strip()
                # 从 URL 中提取文档 ID
                # 语雀 URL 格式: https://www.yuque.com/org/repo/doc_id
                parts = source_url.rstrip('/').split('/')
                if len(parts) >= 5:
                    source_id = parts[-1]
                break

        return {
            "source_type": "yuque",
            "source_url": source_url,
            "source_id": source_id,
            "source_metadata": {
                "plugin_id": "yuque",
                "download_time": None  # 可以从文件修改时间推断
            }
        }

    def get_sync_directories(self) -> List[str]:
        """获取插件同步的本地目录列表

        Returns:
            list: 本地目录路径列表
        """
        if not self._repos:
            return []

        directories = []
        for repo in self._repos:
            download_dir = repo.get("_download_dir")
            if download_dir:
                directories.append(str(download_dir))

        return directories

    async def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态信息

        Returns:
            dict: 同步状态
        """
        total_files = sum(
            result.get("stats", {}).get("files", 0)
            for result in self._sync_results.values()
        )
        total_errors = sum(
            1 for result in self._sync_results.values()
            if not result.get("success", False)
        )

        return {
            "last_sync_time": None,  # TODO: 记录同步时间
            "total_repos": len(self._repos),
            "synced_repos": len(self._sync_results),
            "total_files": total_files,
            "failed_repos": total_errors,
            "is_syncing": False,
            "yuque_dl_path": self._yuque_dl_path
        }

    async def cleanup(self):
        """清理插件资源"""
        logger.debug("语雀数据源插件清理完成")
        self._sync_results.clear()
