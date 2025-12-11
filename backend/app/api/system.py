"""
系统管理API路由
提供系统健康检查API接口
"""
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, get_database_info
from app.core.logging_config import get_logger
from app.schemas.responses import HealthResponse

router = APIRouter(prefix="/api/system", tags=["系统管理"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse, summary="系统健康检查")
async def health_check(db: Session = Depends(get_db)):
    """
    系统健康检查

    检查数据库连接、AI模型状态、索引状态等
    """
    logger.info("执行系统健康检查")

    try:
        # 数据库状态检查
        db_status = get_database_info()

        # 系统资源状态
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)

        # 获取真实的AI模型状态
        ai_models_status = {}
        try:
            # 尝试获取AI模型服务状态
            from app.services.ai_model_manager import ai_model_service
            ai_models_status = await ai_model_service.get_model_status()
        except Exception as e:
            logger.warning(f"无法获取AI模型状态: {str(e)}")
            # 提供默认状态
            ai_models_status = {
                "error": f"AI模型服务不可用: {str(e)}",
                "bge_m3": {"status": "unknown", "error": "模型服务不可用"},
                "faster_whisper": {"status": "unknown", "error": "模型服务不可用"},
                "cn_clip": {"status": "unknown", "error": "模型服务不可用"}
            }

        # 获取真实的索引状态
        indexes_status = {}
        try:
            # 获取分块搜索服务实例
            from app.services.chunk_search_service import get_chunk_search_service
            search_service = get_chunk_search_service()
            index_info = search_service.get_index_info()

            # 转换索引状态格式
            indexes_status = {
                "faiss_index": {
                    "status": "ready" if index_info.get('faiss_available') else "not_available",
                    "document_count": index_info.get('faiss_doc_count', 0),
                    "index_size": f"{index_info.get('faiss_doc_count', 0) * 150}KB",  # 估算大小
                    "dimension": index_info.get('faiss_dimension', 'unknown'),
                    "last_updated": datetime.now().isoformat()
                },
                "whoosh_index": {
                    "status": "ready" if index_info.get('whoosh_available') else "not_available",
                    "document_count": index_info.get('whoosh_doc_count', 0),
                    "index_size": f"{index_info.get('whoosh_doc_count', 0) * 50}KB",  # 估算大小
                    "last_updated": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.warning(f"无法获取索引状态: {str(e)}")
            indexes_status = {
                "faiss_index": {"status": "error", "error": str(e)},
                "whoosh_index": {"status": "error", "error": str(e)}
            }

        # 服务状态
        services_status = {
            "fastapi": {
                "status": "running",
                "uptime": "2h 15m",
                "version": "1.0.0"
            },
            "database": {
                "status": db_status["status"],
                "connection_pool": "1/1"
            }
        }

        # 计算整体健康状态
        overall_status = "healthy"
        if db_status["status"] != "connected":
            overall_status = "unhealthy"
        elif memory.percent > 90:
            overall_status = "warning"
        elif disk.percent > 95:
            overall_status = "warning"

        health_data = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": f"{memory.total / (1024**3):.1f}GB",
                    "used": f"{memory.used / (1024**3):.1f}GB",
                    "percent": memory.percent
                },
                "disk": {
                    "total": f"{disk.total / (1024**3):.1f}GB",
                    "used": f"{disk.used / (1024**3):.1f}GB",
                    "percent": disk.percent
                }
            },
            "database": db_status,
            "ai_models": ai_models_status,
            "indexes": indexes_status,
            "services": services_status
        }

        logger.info(f"健康检查完成: status={overall_status}")

        return HealthResponse(
            data=health_data,
            message="系统健康检查完成"
        )

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthResponse(
            data={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            message="健康检查失败"
        )


@router.get("/running-status", summary="获取系统运行状态")
async def get_running_status(db: Session = Depends(get_db)):
    """
    获取系统运行状态

    专为前端底部状态栏设计的接口，返回简化的系统状态信息
    """
    logger.info("获取系统运行状态")

    try:
        # 获取索引文件数量
        index_count = 0
        try:
            from app.services.chunk_search_service import get_chunk_search_service
            search_service = get_chunk_search_service()
            index_info = search_service.get_index_info()
            # 取两个索引的最大文档数量
            faiss_count = index_info.get('faiss_doc_count', 0)
            whoosh_count = index_info.get('whoosh_doc_count', 0)
            index_count = max(faiss_count, whoosh_count)
        except Exception as e:
            logger.warning(f"获取索引状态失败: {str(e)}")

        # 获取数据总大小（从files表计算）
        data_size = 0
        try:
            from app.models.file import FileModel
            from sqlalchemy import func

            # 计算所有已索引文件的总大小
            total_size_result = db.query(func.sum(FileModel.file_size)).filter(
                FileModel.is_indexed == True
            ).scalar()

            if total_size_result:
                data_size = total_size_result
        except Exception as e:
            logger.warning(f"获取数据大小失败: {str(e)}")

        # 获取今日搜索次数
        today_searches = 0
        try:
            from datetime import date
            from app.models.search_history import SearchHistoryModel

            # 查询今日搜索次数
            today = date.today()
            today_searches = db.query(SearchHistoryModel).filter(
                func.date(SearchHistoryModel.created_at) == today
            ).count()
        except Exception as e:
            logger.warning(f"获取今日搜索次数失败: {str(e)}")

        # 获取最近索引任务完成时间
        last_update = datetime.now()
        try:
            from app.models.index_job import IndexJobModel

            # 查询最近完成的索引任务
            last_completed_job = db.query(IndexJobModel).filter(
                IndexJobModel.status == 'completed'
            ).order_by(IndexJobModel.completed_at.desc()).first()

            if last_completed_job and last_completed_job.completed_at:
                last_update = last_completed_job.completed_at
        except Exception as e:
            logger.warning(f"获取最后更新时间失败: {str(e)}")

        # 判断系统状态
        system_status = "正常"
        system_color = "green"

        # 检查数据库连接
        db_status = get_database_info()
        if db_status["status"] != "connected":
            system_status = "异常"
            system_color = "red"

        # 检查是否有索引
        if index_count == 0:
            system_status = "待索引"
            system_color = "orange"

        response_data = {
            "success": True,
            "data": {
                "index_status": system_status,
                "data_count": index_count,
                "today_searches": today_searches,
                "system_status": system_status,
                "last_update": last_update.isoformat()
            }
        }

        logger.info(f"运行状态获取成功: index_count={index_count}, today_searches={today_searches}, data_size={data_size}")

        return response_data

    except Exception as e:
        logger.error(f"获取运行状态失败: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "SYSTEM_STATUS_ERROR",
                "message": f"获取系统运行状态失败: {str(e)}",
                "type": "SystemError"
            }
        }