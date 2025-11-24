"""
核心模块包初始化
导出核心功能模块
"""

from app.core.database import get_db, init_database, get_database_info
from app.core.exceptions import (
    XiaoyaoSearchException,
    ValidationException,
    DatabaseException,
    AIServiceException,
    IndexException,
    SearchException,
    FileOperationException,
    ModelLoadException,
    ConfigurationException,
    ResourceNotFoundException,
    PermissionDeniedException,
    RateLimitExceededException,
    InsufficientResourceException
)
from app.core.error_handlers import setup_exception_handlers
from app.core.logging_config import setup_logging, get_logger, LoggerMixin

__all__ = [
    # 数据库相关
    "get_db",
    "init_database",
    "get_database_info",

    # 异常类
    "XiaoyaoSearchException",
    "ValidationException",
    "DatabaseException",
    "AIServiceException",
    "IndexException",
    "SearchException",
    "FileOperationException",
    "ModelLoadException",
    "ConfigurationException",
    "ResourceNotFoundException",
    "PermissionDeniedException",
    "RateLimitExceededException",
    "InsufficientResourceException",

    # 异常处理
    "setup_exception_handlers",

    # 日志相关
    "setup_logging",
    "get_logger",
    "LoggerMixin"
]