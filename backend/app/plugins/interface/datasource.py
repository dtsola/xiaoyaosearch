"""
数据源插件接口

定义数据源插件必须实现的接口规范。
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..base import BasePlugin, PluginType

logger = logging.getLogger(__name__)


class DataSourcePlugin(BasePlugin):
    """数据源插件接口

    数据源插件用于将外部数据源同步到本地文件系统，
    供索引服务处理和搜索。

    工作流程：
    1. 应用启动时自动加载插件
    2. 调用 initialize() 进行初始化
    3. 调用 sync() 同步数据到本地
    4. 索引时调用 get_file_source_info() 提取元数据
    """

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据（基类默认实现）"""
        return {
            "id": "base_datasource",
            "name": "基础数据源插件",
            "version": "1.0.0",
            "type": PluginType.DATASOURCE.value,
            "author": "XiaoyaoSearch Team",
            "description": "数据源插件基类",
        }

    # 重写父类抽象方法，提供默认实现
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件（默认实现）

        子类可以重写此方法提供自定义初始化逻辑。

        Returns:
            bool: 默认返回 True
        """
        self._config = config
        self._set_ready()
        return True

    async def cleanup(self):
        """清理插件资源（默认实现）

        子类可以重写此方法提供自定义清理逻辑。
        """
        self._config = None
        self._sync_results = {}
        logger.debug(f"{self.__class__.__name__} 插件清理完成")

    @abstractmethod
    async def sync(self) -> bool:
        """同步外部数据到本地文件系统（核心方法，子类必须实现）

        这是数据源插件的核心方法，负责：
        - 从外部数据源获取数据
        - 将数据转换为本地文件
        - 保存到指定的下载目录

        Returns:
            bool: 同步是否成功
                - True: 同步成功（包括部分成功）
                - False: 同步完全失败

        注意：
            - 支持增量同步：只下载变更的文件
            - 错误处理：单个文件失败不应中断整体同步
            - 日志记录：记录同步的文件数量、成功/失败数量
        """
        pass

    @classmethod
    def requires_config(cls) -> bool:
        """是否要求提供 config.yaml

        默认返回 True, 保持对需要敏感配置的数据源插件兼容。
        零配置插件可重写为 False。
        """
        return True

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """获取文件的数据源信息（索引时调用）

        在索引构建过程中，索引服务会调用此方法获取文件的原始数据源信息。

        Args:
            file_path: 文件路径
            content: 文件内容（可选，用于提取元数据）

        Returns:
            dict: 数据源信息，包含以下字段：
                - source_type (str): 数据源类型（如 "yuque", "feishu"）
                - source_url (Optional[str]): 原始文档URL
                - source_id (Optional[str]): 原始文档ID
                - source_metadata (Optional[dict]): 其他元数据

            如果文件不属于此数据源，返回：
                {"source_type": None, "source_url": None}

        默认实现：
            默认返回空数据源信息，子类应重写此方法。

        注意：
            - 必须快速执行，不应进行网络请求或文件IO
            - 通过文件路径或内容特征判断是否属于此数据源
        """
        return {
            "source_type": None,
            "source_url": None,
            "source_id": None,
            "source_metadata": None
        }

    def get_sync_directories(self) -> List[str]:
        """获取插件同步的本地目录列表

        返回此插件同步数据到本地的目录路径，
        用于用户选择索引目录时识别。

        Returns:
            list[str]: 本地目录路径列表

        默认实现：
            从配置中读取 download_dir 字段
        """
        if self._config:
            download_dir = self._config.get("download_dir", "./data")
            plugin_dir = Path(__file__).parent.parent.parent
            full_path = plugin_dir / "datasource" / self.get_metadata().get("id", "") / download_dir
            return [str(full_path)]
        return []

    async def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态信息（可选实现）

        Returns:
            dict: 同步状态信息，包含以下字段：
                - last_sync_time (datetime): 最后同步时间
                - total_files (int): 总文件数
                - synced_files (int): 已同步文件数
                - failed_files (int): 失败文件数
                - is_syncing (bool): 是否正在同步
        """
        return {
            "last_sync_time": None,
            "total_files": 0,
            "synced_files": 0,
            "failed_files": 0,
            "is_syncing": False
        }
