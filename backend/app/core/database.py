"""
数据库连接配置模块
提供SQLite数据库连接和会话管理
"""
import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# 获取数据库路径
DATABASE_PATH = os.getenv("DATABASE_PATH", "../data/database/xiaoyao_search.db")

# 确保数据库目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# 创建数据库引擎
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={
        "check_same_thread": False,  # SQLite多线程访问
        "timeout": 30  # 查询超时时间
    },
    poolclass=StaticPool,  # 静态连接池
    echo=os.getenv("LOG_LEVEL") == "debug"  # 调试模式下打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明基类
Base = declarative_base()

# 元数据对象
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database() -> None:
    """
    初始化数据库，创建所有表并填充默认数据
    """
    try:
        # 导入所有模型，确保它们被注册到Base.metadata
        from app.models.file import FileModel
        from app.models.file_content import FileContentModel
        from app.models.file_chunk import FileChunkModel
        from app.models.search_history import SearchHistoryModel
        from app.models.ai_model import AIModelModel
        from app.models.index_job import IndexJobModel
        from app.models.app_settings import AppSettingsModel
        from app.models.glossary_collection import GlossaryCollectionModel
        from app.models.glossary_term import GlossaryTermModel

        # 禁用外键约束（SQLite软外键模式）
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF"))
            conn.commit()

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info(f"数据库表创建完成: {DATABASE_PATH}")

        # 初始化默认设置
        _init_default_settings()

        logger.info(f"数据库初始化完成: {DATABASE_PATH}")

    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def _init_default_settings() -> None:
    """
    初始化默认应用设置
    """
    try:
        from app.models.app_settings import AppSettingsModel

        # 创建数据库会话
        db = SessionLocal()

        try:
            # 检查是否已有设置
            existing_count = db.query(AppSettingsModel).count()

            if existing_count == 0:
                # 获取默认设置
                default_settings = AppSettingsModel.get_default_settings()

                # 批量创建默认设置
                for setting_data in default_settings:
                    setting = AppSettingsModel(
                        setting_key=setting_data['setting_key'],
                        setting_value=setting_data['setting_value'],
                        setting_type=setting_data['setting_type'],
                        description=setting_data['description']
                    )
                    db.add(setting)

                db.commit()
                logger.info(f"成功创建 {len(default_settings)} 个默认应用设置")
            else:
                logger.debug(f"应用设置已存在 ({existing_count} 个)，跳过初始化")

        finally:
            db.close()

    except Exception as e:
        logger.warning(f"默认设置初始化失败: {str(e)}")
        # 不抛出异常，允许系统继续运行


def get_database_info() -> dict:
    """
    获取数据库信息

    Returns:
        dict: 数据库连接信息
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # 检查数据库连接
            conn.execute(text("SELECT 1"))

            return {
                "status": "connected",
                "database_path": DATABASE_PATH,
                "driver": "sqlite",
                "connection_pool_size": 1
            }
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e),
            "database_path": DATABASE_PATH
        }