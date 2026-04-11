# data/plugins/datasource/dingding/plugin.py
"""
钉钉文档数据源插件

识别钉钉导出工具生成的 .xyddjson 元数据文件并提取文档信息。

元数据文件格式：
{
  "version": "1.0.0",
  "source": "dingtalk-docs",
  "exportTool": "xiaoyaosearch-dingding-export",
  "exportToolVersion": "1.0.0",
  "exportTime": "2026-04-08T15:30:00.000Z",
  "file": {
    "fileName": "项目报告.docx",
    "originalName": "项目报告",
    "dentryUuid": "A1B2C3D4E5F6G7H8",
    "url": "https://alidocs.dingtalk.com/i/nodes/A1B2C3D4E5F6G7H8"
  }
}
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class DingdingDataSource(DataSourcePlugin):
    """
    钉钉文档数据源插件

    核心功能：
    1. 识别钉钉导出工具生成的元数据文件（.xyddjson）
    2. 提取元数据（dentryUuid、url、exportTime）
    3. 为索引服务提供数据源信息

    设计特点：
    - 无需配置文件（零配置）
    - 无需外部同步（下载工具自动生成）
    - 自动识别（同名元数据文件）
    - 标准JSON格式（可靠、高效、可扩展）
    """

    # 元数据文件扩展名
    METADATA_FILE_EXT = '.xyddjson'

    def __init__(self):
        super().__init__()
        self._plugin_dir: Optional[Path] = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "id": "dingding",
            "name": "钉钉文档",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "识别钉钉导出工具生成的 .xyddjson 元数据文件",
            "datasource_type": "dingding",
            "dependencies": [],  # 无外部依赖
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        钉钉插件无需初始化配置，直接返回成功
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent
            self._set_ready()
            logger.info("钉钉数据源插件初始化成功")
            return True
        except Exception as e:
            logger.error(f"钉钉数据源插件初始化失败: {e}")
            self._set_error(str(e))
            return False

    @classmethod
    def requires_config(cls) -> bool:
        """钉钉插件为零配置插件。"""
        return False

    async def sync(self) -> bool:
        """
        同步方法（钉钉无需同步）

        钉钉文档由下载工具自动生成元数据文件，无需外部同步逻辑
        """
        logger.info("钉钉文档由下载工具自动生成元数据文件，无需外部同步")
        return True

    def get_file_source_info(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        获取文件的数据源信息（核心方法）

        从钉钉导出的元数据文件（.xyddjson）中提取信息：
        - 来源类型: dingding
        - 原文链接: 钉钉文档 URL
        - 文档ID: dentryUuid

        Args:
            file_path: 文件路径
            content: 文件内容（钉钉插件不使用此参数）

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - source_type: "dingding" 或 None
                - source_url: 钉钉原文 URL 或 None
                - source_id: dentryUuid 或 None
                - export_time: 导出时间 或 None
                - original_name: 原始文件名 或 None
        """
        try:
            # 读取元数据文件
            metadata = self._read_metadata_file(file_path)

            if not metadata:
                return {"source_type": None, "source_url": None, "source_id": None}

            # 提取关键字段
            file_info = metadata.get("file", {})

            logger.debug(f"检测到钉钉文档: {file_path}")
            return {
                "source_type": "dingding",
                "source_url": file_info.get("url"),
                "source_id": file_info.get("dentryUuid"),
                "export_time": metadata.get("exportTime"),
                "original_name": file_info.get("originalName")
            }

        except Exception as e:
            logger.warning(f"解析钉钉元数据失败 {file_path}: {e}")
            return {"source_type": None, "source_url": None, "source_id": None}

    def _read_metadata_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        读取 .xyddjson 元数据文件

        Args:
            file_path: 原文件路径

        Returns:
            元数据字典，读取失败返回 None
        """
        # 构造元数据文件路径
        metadata_path = Path(str(file_path) + self.METADATA_FILE_EXT)

        # 检查文件是否存在
        if not metadata_path.exists():
            return None

        try:
            # 读取并解析 JSON
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 验证元数据格式
            if metadata.get('source') != 'dingtalk-docs':
                logger.debug(f"元数据文件 source 字段不匹配: {metadata_path}")
                return None

            return metadata

        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析失败 {metadata_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"读取元数据文件失败 {metadata_path}: {e}")
            return None

    async def cleanup(self):
        """清理资源（无需清理）"""
        pass
