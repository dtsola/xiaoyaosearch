"""
应用配置设置
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 基础设置
    PROJECT_NAME: str = "小遥搜索API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # 服务器设置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库设置
    DATABASE_URL: str = "sqlite:///./xiaoyao_search.db"

    # 数据库连接池设置
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # SQLite特定设置
    SQLITE_TIMEOUT: int = 30
    SQLITE_ISOLATION_LEVEL: str = "IMMEDIATE"

    # 安全设置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS设置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 文件存储设置
    UPLOAD_DIR: str = "./uploads"
    DATA_DIR: str = "./data"
    MODELS_DIR: str = "./models"
    CACHE_DIR: str = "./cache"

    # 索引设置
    INDEX_DIR: str = "./data/indexes"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FILE_TYPES: List[str] = [
        ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".mp3", ".wav", ".mp4", ".avi", ".mov"
    ]

    # AI模型设置
    EMBEDDING_MODEL: str = "BAAI/bge-base-zh-v1.5"
    WHISPER_MODEL: str = "base"
    CLIP_MODEL: str = "OFA-Sys/chinese-clip-vit-base-patch16"

    # 搜索设置
    DEFAULT_SEARCH_LIMIT: int = 20
    MAX_SEARCH_LIMIT: int = 100
    VECTOR_WEIGHT: float = 0.6
    TEXT_WEIGHT: float = 0.4

    # 缓存设置
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5分钟

    # 日志设置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # OpenAI API设置（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的字段


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


settings = get_settings()