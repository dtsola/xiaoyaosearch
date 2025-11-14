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
    AI_MODEL_DIR: str = "./ai-models"
    OLLAMA_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None

    # LLM Query Understanding Service Settings
    LLM_PROVIDER: str = "mock"  # openai, ollama, mock
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 500
    LLM_TIMEOUT: int = 30
    LLM_CACHE_TTL: int = 3600  # Cache TTL in seconds
    LLM_ENABLE_CACHING: bool = True

    # OpenAI specific settings
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None

    # Ollama specific settings
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_TIMEOUT: int = 60
    OLLAMA_MAX_RETRIES: int = 3

    # Query Understanding Settings
    QUERY_UNDERSTANDING_ENABLED: bool = True
    QUERY_ANALYZE_INTENT: bool = True
    QUERY_EXTRACT_KEYWORDS: bool = True
    QUERY_PARSE_TIME: bool = True
    QUERY_EXPAND_QUERY: bool = True

    # AI Service Performance Settings
    AI_CONCURRENT_REQUESTS: int = 3
    AI_RATE_LIMIT_REQUESTS: int = 60
    AI_RATE_LIMIT_PERIOD: int = 60  # seconds

  
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

    @validator("LLM_TEMPERATURE")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0")
        return v

    @validator("LLM_MAX_TOKENS")
    def validate_max_tokens(cls, v):
        if v < 1 or v > 4000:
            raise ValueError("LLM_MAX_TOKENS must be between 1 and 4000")
        return v

    @validator("LLM_TIMEOUT")
    def validate_timeout(cls, v):
        if v < 5 or v > 300:
            raise ValueError("LLM_TIMEOUT must be between 5 and 300 seconds")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # 允许额外的字段但忽略它们
    )


# Create settings instance
settings = Settings()