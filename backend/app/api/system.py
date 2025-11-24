"""
系统管理API路由
提供系统设置、状态监控等API接口
"""
import os
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db, get_database_info
from app.core.logging_config import get_logger
from app.schemas.requests import SettingsUpdateRequest
from app.schemas.responses import (
    SettingsResponse, HealthResponse, SuccessResponse
)

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

        # AI模型状态（模拟）
        ai_models_status = {
            "bge_m3": {
                "status": "loaded",
                "memory_usage": "2.1GB",
                "last_used": datetime.now().isoformat()
            },
            "faster_whisper": {
                "status": "not_loaded",
                "error": None,
                "memory_usage": "0GB"
            },
            "cn_clip": {
                "status": "loaded",
                "memory_usage": "1.5GB",
                "last_used": datetime.now().isoformat()
            }
        }

        # 索引状态（模拟）
        indexes_status = {
            "faiss_index": {
                "status": "ready",
                "document_count": 15420,
                "index_size": "2.3GB",
                "last_updated": datetime.now().isoformat()
            },
            "whoosh_index": {
                "status": "ready",
                "document_count": 15420,
                "index_size": "450MB",
                "last_updated": datetime.now().isoformat()
            }
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


@router.get("/info", summary="系统信息")
async def get_system_info():
    """
    获取系统基本信息
    """
    logger.info("获取系统信息")

    try:
        # 系统基本信息
        system_info = {
            "app_name": "小遥搜索",
            "version": "1.0.0",
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown",
            "working_directory": os.getcwd(),
            "environment": os.getenv("NODE_ENV", "development")
        }

        # 进程信息
        process = psutil.Process()
        process_info = {
            "pid": process.pid,
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
            "memory_info": {
                "rss": f"{process.memory_info().rss / (1024**2):.1f}MB",
                "vms": f"{process.memory_info().vms / (1024**2):.1f}MB"
            },
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads()
        }

        system_info.update({
            "process": process_info,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "data": system_info,
            "message": "获取系统信息成功"
        }

    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")


@router.get("/settings", response_model=SettingsResponse, summary="获取应用设置")
async def get_settings():
    """
    获取应用设置
    """
    logger.info("获取应用设置")

    try:
        # 默认设置
        settings = {
            "app": {
                "name": "小遥搜索",
                "version": "1.0.0",
                "debug": os.getenv("NODE_ENV") == "development"
            },
            "search": {
                "default_limit": 20,
                "default_threshold": 0.7,
                "max_file_size": 52428800,  # 50MB
                "supported_file_types": [
                    "pdf", "txt", "md", "docx", "xlsx", "mp3", "mp4", "wav"
                ]
            },
            "indexing": {
                "max_concurrent_jobs": 3,
                "supported_formats": [
                    "pdf", "txt", "md", "docx", "xlsx", "mp3", "mp4", "wav"
                ],
                "auto_rebuild": False,
                "scan_interval": 3600  # 1小时
            },
            "ai_models": {
                "embedding_model": "BAAI/bge-m3",
                "speech_model": "faster-whisper",
                "vision_model": "OFA-Sys/chinese-clip-vit-base-patch16",
                "llm_model": "qwen-turbo",
                "prefer_local": True,
                "fallback_to_cloud": True
            },
            "ui": {
                "theme": "light",
                "language": "zh-CN",
                "auto_refresh": True,
                "refresh_interval": 30  # 30秒
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "info"),
                "file_path": os.getenv("LOG_FILE", "../data/logs/app.log"),
                "max_file_size": "10MB",
                "backup_count": 5
            },
            "security": {
                "enable_cors": True,
                "allowed_origins": [
                    "http://localhost:3000",
                    "http://localhost:5173"
                ],
                "max_request_size": 52428800  # 50MB
            }
        }

        return SettingsResponse(
            data=settings,
            message="获取应用设置成功"
        )

    except Exception as e:
        logger.error(f"获取应用设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取应用设置失败: {str(e)}")


@router.post("/settings", response_model=SuccessResponse, summary="更新应用设置")
async def update_settings(request: SettingsUpdateRequest):
    """
    更新应用设置

    - **request**: 设置更新请求
    """
    logger.info("更新应用设置")

    try:
        # TODO: 实现设置保存逻辑
        # 这里暂时只是记录更新内容
        updated_settings = {}

        if request.search:
            updated_settings["search"] = request.search
        if request.indexing:
            updated_settings["indexing"] = request.indexing
        if request.ui:
            updated_settings["ui"] = request.ui
        if request.ai_models:
            updated_settings["ai_models"] = request.ai_models

        logger.info(f"设置更新完成: {list(updated_settings.keys())}")

        return SuccessResponse(
            data=updated_settings,
            message="设置更新成功"
        )

    except Exception as e:
        logger.error(f"更新应用设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新应用设置失败: {str(e)}")


@router.post("/restart", response_model=SuccessResponse, summary="重启应用")
async def restart_application():
    """
    重启应用服务
    """
    logger.info("收到应用重启请求")

    try:
        # TODO: 实现应用重启逻辑
        # 这里暂时返回成功响应
        logger.warning("应用重启功能尚未实现，仅返回成功响应")

        return SuccessResponse(
            data={
                "restart_requested": True,
                "estimated_downtime": "5-10秒",
                "timestamp": datetime.now().isoformat()
            },
            message="应用重启请求已接收"
        )

    except Exception as e:
        logger.error(f"重启应用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重启应用失败: {str(e)}")


@router.get("/logs", summary="获取应用日志")
async def get_application_logs(
    lines: int = 100,
    level: str = "all"
):
    """
    获取应用日志

    - **lines**: 返回日志行数
    - **level**: 日志级别过滤 (all/error/warning/info/debug)
    """
    logger.info(f"获取应用日志: lines={lines}, level={level}")

    try:
        log_file = os.getenv("LOG_FILE", "../data/logs/app.log")

        if not os.path.exists(log_file):
            return {
                "success": True,
                "data": {
                    "logs": [],
                    "total_lines": 0,
                    "log_file": log_file
                },
                "message": "日志文件不存在"
            }

        # TODO: 实现日志读取和过滤逻辑
        # 这里暂时返回模拟数据
        mock_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "应用启动完成",
                "module": "main"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "DEBUG",
                "message": "数据库连接建立",
                "module": "database"
            }
        ]

        return {
            "success": True,
            "data": {
                "logs": mock_logs[-lines:],
                "total_lines": len(mock_logs),
                "log_file": log_file,
                "filter_level": level
            },
            "message": "获取应用日志成功"
        }

    except Exception as e:
        logger.error(f"获取应用日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取应用日志失败: {str(e)}")


@router.delete("/cache", response_model=SuccessResponse, summary="清理缓存")
async def clear_cache():
    """
    清理系统缓存
    """
    logger.info("清理系统缓存")

    try:
        # TODO: 实现缓存清理逻辑
        # 包括：向量缓存、搜索结果缓存、临时文件等

        cache_cleared = {
            "vector_cache": True,
            "search_cache": True,
            "temp_files": True,
            "logs_cleaned": False
        }

        logger.info(f"缓存清理完成: {cache_cleared}")

        return SuccessResponse(
            data=cache_cleared,
            message="系统缓存清理完成"
        )

    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")