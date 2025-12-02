"""
应用设置数据模型
用于存储应用的全局配置设置
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class AppSettingsModel(Base):
    """
    应用设置模型

    存储应用的全局配置设置，支持不同类型的配置值
    """
    __tablename__ = "app_settings"

    # 主键字段
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键，唯一标识设置项"
    )

    # 设置标识字段
    setting_key = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="设置键名，唯一标识配置项"
    )

    # 设置值字段
    setting_value = Column(
        Text,
        nullable=True,
        comment="设置值，支持JSON格式的复杂配置"
    )

    # 设置类型字段
    setting_type = Column(
        String(20),
        nullable=False,
        comment="值类型：string/integer/boolean/json"
    )

    # 描述字段
    description = Column(
        Text,
        nullable=True,
        comment="设置说明，描述配置项的作用和用法"
    )

    # 时间戳字段
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="设置更新时间"
    )

    def __repr__(self) -> str:
        """返回设置的字符串表示"""
        return f"<AppSettingsModel(key='{self.setting_key}', type='{self.setting_type}')>"

    def to_dict(self) -> dict:
        """
        将模型转换为字典格式

        Returns:
            dict: 包含所有字段信息的字典
        """
        return {
            "id": self.id,
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "setting_type": self.setting_type,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_default_settings(cls) -> list:
        """
        获取默认设置列表

        Returns:
            list: 默认设置的配置项列表
        """
        return [
            {
                "setting_key": "search.default_limit",
                "setting_value": "20",
                "setting_type": "integer",
                "description": "默认搜索结果数量限制"
            },
            {
                "setting_key": "search.default_threshold",
                "setting_value": "0.7",
                "setting_type": "float",
                "description": "默认搜索相似度阈值"
            },
            {
                "setting_key": "search.max_file_size",
                "setting_value": "52428800",
                "setting_type": "integer",
                "description": "支持的最大文件大小（字节）"
            },
            {
                "setting_key": "indexing.auto_rebuild",
                "setting_value": "false",
                "setting_type": "boolean",
                "description": "是否自动重建索引"
            },
            {
                "setting_key": "indexing.scan_interval",
                "setting_value": "3600",
                "setting_type": "integer",
                "description": "自动扫描间隔（秒）"
            },
            {
                "setting_key": "ai_models.embedding_model",
                "setting_value": "BAAI/bge-m3",
                "setting_type": "string",
                "description": "默认文本嵌入模型"
            },
            {
                "setting_key": "ai_models.speech_model",
                "setting_value": "faster-whisper",
                "setting_type": "string",
                "description": "默认语音识别模型"
            },
            {
                "setting_key": "ai_models.vision_model",
                "setting_value": "OFA-Sys/chinese-clip-vit-base-patch16",
                "setting_type": "string",
                "description": "默认图像理解模型"
            },
            {
                "setting_key": "ai_models.llm_model",
                "setting_value": "qwen-turbo",
                "setting_type": "string",
                "description": "默认大语言模型"
            },
            {
                "setting_key": "ai_models.prefer_local",
                "setting_value": "true",
                "setting_type": "boolean",
                "description": "优先使用本地AI模型"
            },
            {
                "setting_key": "ui.theme",
                "setting_value": "light",
                "setting_type": "string",
                "description": "界面主题：light/dark"
            },
            {
                "setting_key": "ui.language",
                "setting_value": "zh-CN",
                "setting_type": "string",
                "description": "界面语言"
            },
            {
                "setting_key": "logging.level",
                "setting_value": "info",
                "setting_type": "string",
                "description": "日志级别：debug/info/warning/error"
            },
            {
                "setting_key": "security.enable_cors",
                "setting_value": "true",
                "setting_type": "boolean",
                "description": "是否启用CORS跨域支持"
            }
        ]

    def get_parsed_value(self):
        """
        根据设置类型解析值

        Returns:
            解析后的值，保持原始类型
        """
        if self.setting_value is None:
            return None

        if self.setting_type == "boolean":
            return self.setting_value.lower() in ("true", "1", "yes", "on")
        elif self.setting_type == "integer":
            try:
                return int(self.setting_value)
            except ValueError:
                return 0
        elif self.setting_type == "float":
            try:
                return float(self.setting_value)
            except ValueError:
                return 0.0
        elif self.setting_type == "json":
            try:
                import json
                return json.loads(self.setting_value)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:  # string
            return self.setting_value

    @classmethod
    def parse_value_to_string(cls, value, setting_type: str) -> str:
        """
        将值转换为字符串存储

        Args:
            value: 要转换的值
            setting_type: 设置类型

        Returns:
            str: 转换后的字符串值
        """
        if value is None:
            return ""

        if setting_type == "boolean":
            return "true" if value else "false"
        elif setting_type == "json":
            try:
                import json
                return json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
                return "{}"
        else:
            return str(value)

    def update_value(self, new_value):
        """
        更新设置值

        Args:
            new_value: 新的设置值
        """
        self.setting_value = self.parse_value_to_string(new_value, self.setting_type)
        self.updated_at = datetime.now()