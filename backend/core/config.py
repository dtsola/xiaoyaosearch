"""
Application configuration settings.

Uses Pydantic for type-safe configuration management with environment variable support.
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project metadata
    PROJECT_NAME: str = "XiaoyaoSearch"
    PROJECT_DESCRIPTION: str = "AI-driven desktop search application"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./xiaoyaosearch.db"

    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File storage settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI model settings
    AI_MODEL_DIR: str = "./models"
    OLLAMA_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None

    # Vector search settings
    VECTOR_INDEX_PATH: str = "./data/vector_index.faiss"
    FULLTEXT_INDEX_PATH: str = "./data/fulltext_index"

    # File scanning settings
    WATCH_DIRECTORIES: List[str] = []
    EXCLUDE_PATTERNS: List[str] = [
        "*.tmp", "*.log", "*.cache", ".git", "__pycache__",
        "node_modules", ".vscode", ".idea"
    ]

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("WATCH_DIRECTORIES", pre=True)
    def assemble_watch_directories(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("EXCLUDE_PATTERNS", pre=True)
    def assemble_exclude_patterns(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # 允许额外的字段但忽略它们
    )


# Create settings instance
settings = Settings()