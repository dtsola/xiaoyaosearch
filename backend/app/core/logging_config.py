"""
日志配置模块
配置应用的结构化日志记录系统
"""
import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import json


class JSONFormatter(logging.Formatter):
    """
    JSON格式的日志格式化器
    将日志记录格式化为JSON格式，便于日志分析和监控
    """

    def format(self, record):
        """格式化日志记录为JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # 添加异常信息（如果有）
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 添加额外的字段
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'file_path'):
            log_entry["file_path"] = record.file_path
        if hasattr(record, 'model_type'):
            log_entry["model_type"] = record.model_type

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging():
    """
    配置应用日志系统
    """
    # 获取配置
    log_level = os.getenv("LOG_LEVEL", "info").upper()
    log_file = os.getenv("LOG_FILE", "../data/logs/app.log")

    # 确保日志目录存在
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 控制台处理器 - 修复编码问题
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))

    # 设置编码流处理器，解决Windows控制台中文显示问题
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    # 开发环境使用彩色格式，生产环境使用JSON格式
    if os.getenv("NODE_ENV") == "production":
        console_formatter = JSONFormatter()
    else:
        # 简化格式，避免特殊字符导致的编码问题
        console_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（按时间轮转）
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # 保留30天的日志
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)  # 文件日志至少记录INFO级别

    # 文件日志使用JSON格式
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # 错误日志单独文件
    error_log_file = log_file.replace(".log", "_error.log")
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=error_log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    # 设置特定日志记录器的级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info(f"日志系统配置完成 - 级别: {log_level}, 文件: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志记录器混入类
    为类提供日志记录功能
    """

    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        return logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_function_call(func):
    """
    函数调用日志装饰器

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        # 记录函数调用
        logger.debug(f"调用函数: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"函数异常: {func.__name__} - {str(e)}")
            raise

    return wrapper


def log_async_function_call(func):
    """
    异步函数调用日志装饰器

    Args:
        func: 要装饰的异步函数

    Returns:
        装饰后的异步函数
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        # 记录函数调用
        logger.debug(f"调用异步函数: {func.__name__}")

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"异步函数完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"异步函数异常: {func.__name__} - {str(e)}")
            raise

    return wrapper