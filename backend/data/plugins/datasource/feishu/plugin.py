"""
飞书文档数据源插件

功能：识别从飞书导出的 Markdown 文档并提取元数据信息
特点：零配置、自动识别、性能优化（仅解析文件末尾）
"""
import re
from typing import Dict, Any
from pathlib import Path

from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class FeishuDataSource(DataSourcePlugin):
    """
    飞书文档数据源插件

    核心功能：
    1. 识别飞书导出的 Markdown 文档
    2. 提取元数据（来源类型、原文链接）
    3. 为索引服务提供数据源信息

    设计特点：
    - 无需配置文件（零配置）
    - 无需外部同步（用户手动导出）
    - 自动识别（元数据匹配）
    - 性能优化（仅读取文件末尾500字符）
    """

    # 飞书元数据正则表达式模式
    FEISHU_METADATA_PATTERNS = [
        # 标准格式（中文）
        r'>\s*来源类型:\s*feishu\s*>?\s*原文:\s*<(https://[^\s>]+)>',
        # 兼容格式（英文）
        r'>\s*Source:\s*feishu\s*>?\s*URL:\s*<(https://[^\s>]+)>',
    ]

    def __init__(self):
        super().__init__()
        self._plugin_dir: Path = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "id": "feishu",
            "name": "飞书文档",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "识别飞书导出的 Markdown 文档并提取元数据",
            "datasource_type": "feishu",
            "dependencies": [],  # 无外部依赖
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        飞书插件无需初始化配置，直接返回成功
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent
            self._set_ready()
            logger.info("飞书数据源插件初始化成功")
            return True
        except Exception as e:
            logger.error(f"飞书数据源插件初始化失败: {e}")
            self._set_error(str(e))
            return False

    @classmethod
    def requires_config(cls) -> bool:
        """飞书插件为零配置插件。"""
        return False

    async def sync(self) -> bool:
        """
        同步方法（飞书无需同步）

        飞书文档由用户手动导出，无需外部同步逻辑
        """
        logger.info("飞书文档由用户手动导出，无需外部同步")
        return True

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        获取文件的数据源信息（核心方法）

        从飞书导出的 Markdown 文档末尾提取元数据：
        - 来源类型: feishu
        - 原文链接: 飞书文档 URL

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - source_type: "feishu" 或 None
                - source_url: 飞书原文 URL 或 None
        """
        try:
            # 优化：只读取文件末尾 500 字符
            content_tail = content[-500:] if len(content) > 500 else content

            # 遍历所有匹配模式
            for pattern in self.FEISHU_METADATA_PATTERNS:
                match = re.search(pattern, content_tail, re.IGNORECASE | re.DOTALL)
                if match:
                    source_url = match.group(1).strip()
                    logger.debug(f"检测到飞书文档: {file_path}")
                    return {
                        "source_type": "feishu",
                        "source_url": source_url
                    }

            # 未检测到飞书元数据
            return {"source_type": None, "source_url": None}

        except Exception as e:
            logger.warning(f"解析飞书元数据失败 {file_path}: {e}")
            return {"source_type": None, "source_url": None}

    async def cleanup(self):
        """清理资源（无需清理）"""
        pass
