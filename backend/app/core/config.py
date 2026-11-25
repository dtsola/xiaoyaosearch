"""
应用配置管理

使用Pydantic Settings管理应用配置，支持环境变量和配置文件。
已优化删除所有未使用的配置项，保留的配置项都是项目中实际使用的。

配置类结构：
- IndexConfig: 索引相关配置
- ChunkConfig: 分块功能配置
- DatabaseConfig: 数据库配置
- LoggingConfig: 日志配置
- APIConfig: API相关配置（重新创建，统一管理硬编码值）
- ProcessingConfig: 内容处理和性能配置
- AIConfig: AI模型配置
- DefaultConfig: 默认文件类型配置
"""
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pathlib import Path
from typing import List, Optional, Dict, Any
import os


class IndexConfig(BaseSettings):
    """索引相关配置"""
    # 基础路径配置
    data_root: str = Field(default="../data", description="数据根目录")
    faiss_index_path: Optional[str] = Field(default=None, description="Faiss索引文件路径")
    whoosh_index_path: Optional[str] = Field(default=None, description="Whoosh索引目录路径")

    # 索引构建配置
    use_chinese_analyzer: bool = Field(default=True, description="是否使用中文分析器")
    max_content_length: int = Field(default=1024*1024, description="最大内容长度(字符)")
    index_batch_size: int = Field(default=100, description="索引构建批处理大小")
    vector_dimension: int = Field(default=512, description="向量维度")

    # 文件处理配置
    max_file_size: int = Field(default=100*1024*1024, description="最大文件大小(字节)")
    scanner_max_workers: int = Field(default=4, description="文件扫描最大工作线程数")
    chunk_size: int = Field(default=1024*1024, description="文件哈希计算块大小")

    # 支持的文件格式
    supported_extensions: List[str] = Field(
        default=[
            # 文档类型
            ".pdf", ".txt", ".md", ".rtf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            # 代码类型
            ".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".swift", ".kt",
            # 音频类型
            ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
            # 视频类型
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
            # 图片类型
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg",
            # 压缩包
            ".zip", ".rar", ".7z", ".tar", ".gz"
        ],
        description="支持的文件扩展名列表"
    )

    class Config:
        env_prefix = "INDEX_"


class ChunkConfig(BaseSettings):
    """分块功能配置"""
    # 默认分块策略配置
    default_chunk_size: int = Field(default=500, description="默认分块大小（字符数）")
    default_chunk_overlap: int = Field(default=50, description="默认重叠大小（字符数）")
    default_chunk_strategy: str = Field(default="500+50", description="默认分块策略字符串")

    # 分块索引优化配置
    chunk_search_multiplier: float = Field(default=3.0, description="分块搜索结果倍数")
    chunk_min_relevance: float = Field(default=0.3, description="最小分块相关性阈值")

    # 流式构建配置
    embedding_batch_size: int = Field(default=256, description="单次向量推理的批大小（GPU 建议 256，CPU 建议 32）")
    pipeline_batch_chunks: int = Field(default=4096, description="流式构建时每批处理的分块数上限")

    class Config:
        env_prefix = "CHUNK_"

    def parse_chunk_strategy(self, strategy: str = None) -> tuple[int, int]:
        """解析分块策略

        Args:
            strategy: 策略字符串，如 "500+50"，如果为None则使用默认策略

        Returns:
            tuple[int, int]: (分块大小, 重叠大小)
        """
        if not strategy:
            strategy = self.default_chunk_strategy

        try:
            if '+' in strategy:
                parts = strategy.split('+')
                chunk_size = int(parts[0])
                overlap = int(parts[1])
            else:
                chunk_size = int(strategy)
                overlap = min(self.default_chunk_overlap, chunk_size // 10)

            # 验证参数范围（使用固定限制）
            min_size = 100
            max_size = 2000
            max_overlap_ratio = 0.5

            chunk_size = max(min_size, min(chunk_size, max_size))
            overlap = max(0, min(overlap, int(chunk_size * max_overlap_ratio)))

            return chunk_size, overlap

        except Exception:
            # 解析失败时使用默认值
            return self.default_chunk_size, self.default_chunk_overlap

    def should_auto_chunk(self, file_type: str, file_extension: str = None) -> bool:
        """判断文件是否应该自动分块

        Args:
            file_type: 文件类型（如 'document', 'image' 等）
            file_extension: 文件扩展名（如 'txt', 'pdf' 等）

        Returns:
            bool: 是否应该自动分块
        """
        # 目前只对文档类型进行自动分块
        if file_type != 'document':
            return False

        # 检查扩展名是否在自动分块列表中（使用固定列表）
        auto_chunk_types = {"txt", "md", "pdf", "docx", "doc"}
        if file_extension and file_extension.lower().lstrip('.') in auto_chunk_types:
            return True

        return False


class DatabaseConfig(BaseSettings):
    """数据库相关配置"""
    database_url: str = Field(default="sqlite:///../data/database/xiaoyao_search.db", description="数据库连接URL")
    echo: bool = Field(default=False, description="是否打印SQL语句")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出数")

    class Config:
        env_prefix = "DB_"


class LoggingConfig(BaseSettings):
    """日志相关配置 - 简化版配置"""
    level: str = Field(default="INFO", description="日志级别")
    file_path: Optional[str] = Field(default="../data/logs/app.log", description="日志文件路径")

    # 注意：详细的日志配置在 main.py 中设置，此配置类主要用于核心设置和环境变量覆盖

    class Config:
        env_prefix = "LOG_"


class APIConfig(BaseSettings):
    """API相关配置"""

    # 搜索API配置
    max_search_results: int = Field(default=100, description="最大搜索结果数")
    default_search_results: int = Field(default=20, description="默认搜索结果数")
    max_search_suggestions: int = Field(default=5, description="最大搜索建议数")

    # 文件上传配置
    multimodal_max_file_size: int = Field(default=50*1024*1024, description="多模态文件上传最大大小(字节)")

    # 默认阈值
    default_similarity_threshold: float = Field(default=0.7, description="默认相似度阈值")
    suggestion_threshold: float = Field(default=0.3, description="搜索建议阈值")

    class Config:
        env_prefix = "API_"


class ProcessingConfig(BaseSettings):
    """内容处理和性能配置"""

    # 文件处理配置
    content_max_length: int = Field(default=1024*1024, description="内容提取最大长度(字符)")
    audio_max_duration: int = Field(default=10*60, description="音频处理最大时长(秒)")
    video_max_duration: int = Field(default=10*60, description="视频处理最大时长(秒)")

    # 批处理配置
    index_batch_size: int = Field(default=1000, description="索引批处理大小")
    whisper_batch_num: int = Field(default=6, description="Whisper批量识别数量")

    # 搜索配置
    default_top_k: int = Field(default=10, description="默认相似搜索结果数")

    # 雪花算法配置
    snowflake_machine_id: int = Field(default=1, description="雪花算法机器ID")

    # 音频处理配置
    silence_duration: int = Field(default=1, description="静音检测时长(秒)")

    # 分块配置
    default_avg_chunk_size: int = Field(default=500, description="默认平均分块大小")

    class Config:
        env_prefix = "PROCESSING_"


class AIConfig(BaseSettings):
    """AI模型相关配置"""

    # GPU/CUDA配置
    device: str = Field(default="cuda", description="AI模型运行设备 (cuda/cpu)")
    use_gpu: bool = Field(default=True, description="是否使用GPU加速")
    gpu_memory_fraction: float = Field(default=0.8, description="GPU内存使用比例")

    # 模型加载配置
    enable_mixed_precision: bool = Field(default=True, description="启用混合精度训练")
    enable_compile: bool = Field(default=True, description="启用PyTorch 2.0编译优化")

    class Config:
        env_prefix = "AI_"

    def get_optimal_device(self) -> str:
        """获取最优设备配置"""
        try:
            import torch
            if self.use_gpu and torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        except ImportError:
            return "cpu"


class PluginConfig(BaseSettings):
    """插件系统配置"""

    # 插件目录配置
    plugin_dir: str = Field(default="data/plugins", description="插件根目录")
    plugin_auto_discover: bool = Field(default=True, description="是否自动发现插件")

    # 插件生命周期配置
    auto_sync_on_startup: bool = Field(default=True, description="启动时自动执行数据源同步")
    sync_timeout: int = Field(default=300, description="同步超时时间（秒）")

    # 插件隔离配置
    enable_plugin_sandbox: bool = Field(default=False, description="启用插件沙箱（未实现）")

    class Config:
        env_prefix = "PLUGIN_"


class MCPConfig(BaseSettings):
    """MCP 服务器配置"""

    # 服务器配置
    sse_enabled: bool = Field(default=True, description="是否启用 MCP SSE 服务")
    server_name: str = Field(default="xiaoyao-search", description="MCP 服务器名称")
    server_version: str = Field(default="1.0.0", description="MCP 服务器版本")

    # SSE 配置
    sse_path: str = Field(default="/mcp/sse", description="SSE 端点路径")

    # 搜索配置
    default_limit: int = Field(default=20, ge=1, le=100, description="MCP 默认结果数量")
    default_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="MCP 默认相似度阈值")

    # 语音搜索配置
    voice_enabled: bool = Field(default=True, description="是否启用语音搜索")
    voice_max_duration: int = Field(default=30, ge=1, le=60, description="最大音频时长（秒）")

    class Config:
        env_prefix = "MCP_"


class DefaultConfig(BaseSettings):
    """默认配置"""
    # 默认模式控制
    default_mode: bool = Field(default=True, description="是否启用默认模式")

    # 默认支持的文件扩展名（PRD P0要求）
    supported_extensions: List[str] = Field(
        default=[
            # 视频类 - P0要求
            ".mp4", ".avi",
            # 音频类 - P0要求
            ".mp3", ".wav",
            # 图片类 - P0要求
            ".png", ".jpg", ".jpeg",
            # 文档类 - P0要求
            # Office文档 (支持现代格式和经典格式)
            ".pdf", ".docx", ".xlsx", ".pptx",  # 现代Office格式
            ".doc", ".xls", ".ppt",  # 经典Office格式
            # 文本文档
            ".txt", ".md",
        ],
        description="默认支持的文件扩展名"
    )

    # 文件类型分类
    file_types: Dict[str, str] = Field(
        default={
            ".mp4": "video",
            ".avi": "video",
            ".mp3": "audio",
            ".wav": "audio",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".pdf": "document",
            ".docx": "document",
            ".xlsx": "document",
            ".pptx": "document",
            ".doc": "document",
            ".xls": "document",
            ".ppt": "document",
            ".txt": "document",
            ".md": "document",
        },
        description="文件扩展名到类型的映射"
    )

    # 格式友好显示名称
    format_display_names: Dict[str, str] = Field(
        default={
            ".mp4": "MP4视频",
            ".avi": "AVI视频",
            ".mp3": "MP3音频",
            ".wav": "WAV音频",
            ".png": "PNG图片",
            ".jpg": "JPEG图片",
            ".jpeg": "JPEG图片",
            ".pdf": "PDF文档",
            ".docx": "Word文档",
            ".xlsx": "Excel表格",
            ".pptx": "PowerPoint演示文稿",
            ".doc": "Word文档(经典)",
            ".xls": "Excel表格(经典)",
            ".ppt": "PowerPoint演示文稿(经典)",
            ".txt": "文本文件",
            ".md": "Markdown文档",
        },
        description="文件格式友好显示名称"
    )

    class Config:
        env_prefix = "DEFAULT_"

    def get_supported_extensions(self) -> set:
        """获取默认支持的文件扩展名"""
        return set(self.supported_extensions) if self.default_mode else set()

    def get_file_type(self, extension: str) -> str:
        """根据扩展名获取文件类型"""
        file_type = self.file_types.get(extension.lower())
        if file_type is None:
            raise ValueError(f"不支持的文件类型: {extension}")
        return file_type

    def get_format_display_name(self, extension: str) -> str:
        """获取格式友好显示名称"""
        return self.format_display_names.get(extension.lower(), extension.upper())

    def get_content_config(self, file_type: str) -> Dict[str, Any]:
        """根据文件类型获取内容提取配置"""
        # 默认配置（如果需要可以扩展）
        default_config = {
            'document': {
                'extract_content': True,
                'priority': 1,
                'max_content_length': 1024 * 1024,
            },
            'audio': {
                'extract_content': True,
                'extract_metadata': True,
                'priority': 2,
                'max_duration': 15 * 60,
                'whisper_model': 'base',
                'language': 'zh',
                'metadata_fields': ['duration', 'bitrate', 'sample_rate', 'title', 'artist', 'album'],
            },
            'video': {
                'extract_content': True,
                'extract_metadata': True,
                'priority': 2,
                'max_duration': 15 * 60,
                'whisper_model': 'base',
                'language': 'zh',
                'ffmpeg_audio_codec': 'pcm_s16le',
                'ffmpeg_sample_rate': 16000,
                'ffmpeg_channels': 1,
                'metadata_fields': ['duration', 'resolution', 'fps', 'codec', 'title'],
            },
            'image': {
                'extract_content': True,
                'extract_metadata': True,
                'priority': 2,
                'clip_model': 'chinese-clip-vit-base-patch16',
                'max_image_size': 512,
                'metadata_fields': ['width', 'height', 'format', 'mode'],
            },
        }
        return default_config.get(file_type, {})

    def get_parser_method(self, extension: str) -> str:
        """根据扩展名获取解析器方法名"""
        # 默认解析器方法映射
        parser_methods = {
            # Office文档解析
            '.pdf': '_parse_pdf',
            '.docx': '_parse_docx',
            '.xlsx': '_parse_excel',
            '.pptx': '_parse_pptx',
            '.doc': '_parse_doc',
            '.xls': '_parse_excel',
            '.ppt': '_parse_ppt',
            # 文本文档解析
            '.txt': '_parse_text',
            '.md': '_parse_markdown',
            # 音视频元数据解析
            '.mp3': '_parse_audio_metadata',
            '.wav': '_parse_audio_metadata',
            '.mp4': '_parse_video_metadata',
            '.avi': '_parse_video_metadata',
            '.png': '_parse_image_content',
            '.jpg': '_parse_image_content',
            '.jpeg': '_parse_image_content',
        }
        return parser_methods.get(extension.lower(), '')

    def is_default_mode(self) -> bool:
        """检查是否处于默认模式"""
        return self.default_mode


class AppConfig(BaseSettings):
    """应用总配置"""
    # 应用基础信息
    app_name: str = Field(default="小遥搜索", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")

    # 环境配置
    environment: str = Field(default="development", description="运行环境(development/testing/production)")

    # 子配置
    index: IndexConfig = Field(default_factory=IndexConfig)
    chunk: ChunkConfig = Field(default_factory=ChunkConfig)
    default: DefaultConfig = Field(default_factory=DefaultConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    plugin: PluginConfig = Field(default_factory=PluginConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    # SecurityConfig 已移除 - 桌面应用无需安全认证配置

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # 允许额外字段

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_directories()

    def _setup_directories(self):
        """创建必要的目录"""
        directories = [
            self.index.data_root,
            os.path.dirname(self.index.faiss_index_path) if self.index.faiss_index_path else None,
            self.index.whoosh_index_path,
            os.path.dirname(self.database.database_url.replace("sqlite:///", "")) if self.database.database_url.startswith("sqlite") else None,
            os.path.dirname(self.logging.file_path) if self.logging.file_path else None,
        ]

        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)

    def get_index_paths(self) -> tuple[str, str]:
        """获取索引文件路径"""
        data_root = Path(self.index.data_root)

        if not self.index.faiss_index_path:
            faiss_path = str(data_root / "indexes" / "faiss" / "document_index.faiss")
        else:
            faiss_path = self.index.faiss_index_path

        if not self.index.whoosh_index_path:
            whoosh_path = str(data_root / "indexes" / "whoosh")
        else:
            whoosh_path = self.index.whoosh_index_path

        return faiss_path, whoosh_path

    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.environment.lower() == "development"

    def validate_config(self) -> List[str]:
        """验证配置的有效性"""
        errors = []

        # 验证数据目录
        data_root = Path(self.index.data_root)
        if not data_root.exists():
            try:
                data_root.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建数据目录 {self.index.data_root}: {e}")

        # 验证文件大小限制（统一使用 IndexConfig.max_file_size）
        if self.index.max_file_size <= 0:
            errors.append("最大文件大小必须大于0")

        # 验证索引配置
        if self.index.vector_dimension <= 0:
            errors.append("向量维度必须大于0")

        if self.index.index_batch_size <= 0:
            errors.append("批处理大小必须大于0")

        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level.upper() not in valid_log_levels:
            errors.append(f"无效的日志级别: {self.logging.level}")

        return errors


# 全局配置实例
# 获取 backend 目录的绝对路径，确保 .env 文件能被正确找到
# 无论从哪里运行，都从 backend/ 目录加载 .env 配置
_backend_dir = Path(__file__).parent.parent.parent
_env_file = _backend_dir / ".env"
settings = AppConfig(_env_file=str(_env_file) if _env_file.exists() else None)


def get_settings() -> AppConfig:
    """获取应用配置实例"""
    return settings


def reload_settings():
    """重新加载配置"""
    global settings
    # 从 backend 目录加载 .env 配置
    _backend_dir = Path(__file__).parent.parent.parent
    _env_file = _backend_dir / ".env"
    settings = AppConfig(_env_file=str(_env_file) if _env_file.exists() else None)
    return settings
