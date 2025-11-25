"""
应用配置管理

使用Pydantic Settings管理应用配置，支持环境变量和配置文件。
"""
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pathlib import Path
from typing import List, Optional
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

    # 索引质量配置
    min_content_length: int = Field(default=10, description="最小内容长度要求")
    min_parse_confidence: float = Field(default=0.3, description="最小解析置信度")
    auto_reindex_threshold: int = Field(default=7, description="自动重新索引的重试次数阈值")

    class Config:
        env_prefix = "INDEX_"


class DatabaseConfig(BaseSettings):
    """数据库相关配置"""
    database_url: str = Field(default="sqlite:///../data/database/xiaoyao_search.db", description="数据库连接URL")
    echo: bool = Field(default=False, description="是否打印SQL语句")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出数")

    class Config:
        env_prefix = "DB_"


class APIConfig(BaseSettings):
    """API相关配置"""
    host: str = Field(default="127.0.0.1", description="API服务主机")
    port: int = Field(default=8000, description="API服务端口")
    reload: bool = Field(default=True, description="是否启用热重载")
    workers: int = Field(default=1, description="工作进程数")

    # API限制配置
    max_search_results: int = Field(default=100, description="最大搜索结果数")
    default_search_results: int = Field(default=20, description="默认搜索结果数")
    max_upload_size: int = Field(default=50*1024*1024, description="最大上传文件大小")

    class Config:
        env_prefix = "API_"


class LoggingConfig(BaseSettings):
    """日志相关配置"""
    level: str = Field(default="INFO", description="日志级别")
    file_path: Optional[str] = Field(default="../data/logs/app.log", description="日志文件路径")
    max_file_size: int = Field(default=10*1024*1024, description="单个日志文件最大大小")
    backup_count: int = Field(default=5, description="日志文件备份数量")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )

    class Config:
        env_prefix = "LOG_"


class AIConfig(BaseSettings):
    """AI模型相关配置"""
    # 默认模型配置
    default_clip_model: str = Field(default="OFA-Sys/chinese-clip-vit-base-patch16", description="默认CLIP模型")
    default_bge_model: str = Field(default="BAAI/bge-m3", description="默认BGE模型")
    default_whisper_model: str = Field(default="base", description="默认Whisper模型")

    # 模型路径配置
    models_cache_dir: str = Field(default="../data/models", description="模型缓存目录")

    # GPU/CUDA配置
    device: str = Field(default="cuda", description="AI模型运行设备 (cuda/cpu)")
    use_gpu: bool = Field(default=True, description="是否使用GPU加速")
    gpu_memory_fraction: float = Field(default=0.8, description="GPU内存使用比例")

    # 模型加载配置
    enable_mixed_precision: bool = Field(default=True, description="启用混合精度训练")
    enable_compile: bool = Field(default=True, description="启用PyTorch 2.0编译优化")

    # 云端API配置（环境变量）
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    aliyun_access_key_id: Optional[str] = Field(default=None, description="阿里云AccessKey ID")
    aliyun_access_key_secret: Optional[str] = Field(default=None, description="阿里云AccessKey Secret")

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


class SecurityConfig(BaseSettings):
    """安全相关配置"""
    secret_key: str = Field(default="xiaoyao-search-secret-key-change-in-production", description="应用密钥")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], description="允许的主机列表")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], description="允许的CORS源")

    class Config:
        env_prefix = "SECURITY_"


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
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

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
            self.ai.models_cache_dir,
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

        # 验证文件大小限制
        if self.index.max_file_size <= 0:
            errors.append("最大文件大小必须大于0")

        if self.api.max_upload_size <= 0:
            errors.append("最大上传大小必须大于0")

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
settings = AppConfig()


def get_settings() -> AppConfig:
    """获取应用配置实例"""
    return settings


def reload_settings():
    """重新加载配置"""
    global settings
    settings = AppConfig()
    return settings


# 环境变量配置示例
def create_sample_env_file():
    """创建示例环境变量文件"""
    sample_env = """
# 小遥搜索 - 环境变量配置示例

# 应用配置
APP_NAME=小遥搜索
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# 索引配置
INDEX_DATA_ROOT=../data
INDEX_USE_CHINESE_ANALYZER=True
INDEX_MAX_FILE_SIZE=104857600
INDEX_SCANNER_MAX_WORKERS=4

# 数据库配置
DB_DATABASE_URL=sqlite:///../data/database/xiaoyao_search.db
DB_ECHO=False

# API配置
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=../data/logs/app.log

# AI配置
AI_DEFAULT_CLIP_MODEL=OFA-Sys/chinese-clip-vit-base-patch16
AI_DEFAULT_BGE_MODEL=BAAI/bge-m3
AI_MODELS_CACHE_DIR=../data/models

# 云端API配置（可选）
# AI_OPENAI_API_KEY=your_openai_api_key
# AI_ALIYUN_ACCESS_KEY_ID=your_access_key_id
# AI_ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 安全配置
SECURITY_SECRET_KEY=your-secret-key-change-in-production
SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    try:
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(sample_env.strip())
        print("示例环境变量文件已创建: .env.example")
    except Exception as e:
        print(f"创建示例环境变量文件失败: {e}")


if __name__ == "__main__":
    # 创建示例环境变量文件
    create_sample_env_file()

    # 测试配置加载
    config = get_settings()
    print("配置加载成功:")
    print(f"  应用名称: {config.app_name}")
    print(f"  数据根目录: {config.index.data_root}")
    print(f"  数据库URL: {config.database.database_url}")

    # 验证配置
    errors = config.validate_config()
    if errors:
        print("\n配置验证错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n配置验证通过")