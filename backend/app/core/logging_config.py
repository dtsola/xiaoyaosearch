"""
Loguru 日志配置模块
提供现代化的日志记录功能，解决多线程环境下的日志写入问题
"""
import os
import sys
from pathlib import Path
from loguru import logger


def setup_ai_logging():
    """
    配置AI模型相关的日志设置，抑制C++库的日志警告

    必须在导入任何AI模型库（tensorflow、transformers等）之前调用
    """
    # 设置环境变量抑制C++库日志
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow日志级别
    os.environ['GRPC_VERBOSITY'] = 'ERROR'    # gRPC日志级别
    os.environ['GLOG_minloglevel'] = '2'      # Google日志最小级别
    os.environ['GLOG_v'] = '0'               # Google日志详细程度
    os.environ['PYTHONWARNINGS'] = 'ignore'  # 忽略Python警告


def setup_logging():
    """
    配置 loguru 日志系统
    """
    # 获取配置
    log_level = os.getenv("LOG_LEVEL", "info").upper()
    log_file = os.getenv("LOG_FILE", "../data/logs/app.log")

    # 确保日志目录存在
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # 添加文件输出（所有日志）
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        catch=True,
    )

    # 添加错误日志单独文件
    error_log_file = log_file.replace(".log", "_error.log")
    logger.add(
        error_log_file,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        catch=True,
    )

    # 记录初始化完成
    logger.info(f"Loguru 日志系统初始化完成 - 级别: {log_level}")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"错误日志: {error_log_file}")


def get_logger(name: str = None):
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logger 实例
    """
    # 使用 bind 添加额外信息
    return logger.bind(name=name) if name else logger


# 为了兼容性，提供 LoggerMixin 类
class LoggerMixin:
    """
    日志记录器混入类
    为类提供日志记录功能
    """
    @property
    def logger(self):
        """获取当前类的日志记录器"""
        return logger.bind(name=self.__class__.__module__ + "." + self.__class__.__name__)


# 导出所有内容
__all__ = ["logger", "setup_logging", "setup_ai_logging", "get_logger", "LoggerMixin"]