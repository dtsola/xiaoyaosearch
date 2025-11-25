"""
系统管理API路由
提供系统设置、状态监控等API接口
"""
import os
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
            # 获取搜索服务实例
            from app.services.search_service import get_search_service
            search_service = get_search_service()
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

    执行优雅的应用重启，包括：
    - 停止接受新请求
    - 完成正在处理的请求
    - 清理资源
    - 重启服务进程
    """
    logger.info("收到应用重启请求")

    try:
        import os
        import signal
        import threading
        import time
        from fastapi import FastAPI

        # 获取当前进程信息
        current_pid = os.getpid()
        logger.info(f"准备重启应用，当前PID: {current_pid}")

        # 检查是否有正在运行的索引任务
        from app.core.database import SessionLocal
        from app.models.index_job import IndexJobModel
        from app.utils.enum_helpers import get_enum_value
        from app.schemas.enums import JobStatus

        db = SessionLocal()
        try:
            running_jobs = db.query(IndexJobModel).filter(
                IndexJobModel.status == get_enum_value(JobStatus.PROCESSING)
            ).count()

            if running_jobs > 0:
                logger.warning(f"检测到{running_jobs}个正在运行的索引任务，重启将中断这些任务")
        finally:
            db.close()

        # 定义重启函数（延迟执行，确保响应返回给客户端）
        def delayed_restart():
            """延迟执行重启操作"""
            try:
                logger.info("开始执行应用重启流程...")

                # 等待一段时间，确保响应已发送给客户端
                time.sleep(2)

                # 优雅关闭：发送SIGTERM信号
                if os.name == 'nt':  # Windows
                    import subprocess
                    # 在Windows上，我们使用subprocess来重启
                    logger.info("Windows系统：准备重启应用...")

                    # 构建重启命令
                    restart_command = [
                        "cmd", "/c",
                        "taskkill /F /PID " + str(current_pid) + " && "
                        "cd /d " + os.getcwd() + " && "
                        "start /B .\\venv\\Scripts\\python.exe main.py"
                    ]

                    logger.info(f"执行重启命令: {' '.join(restart_command)}")

                    # 在新进程中执行重启命令
                    subprocess.Popen(
                        restart_command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.DETACHED_PROCESS
                    )

                else:  # Unix/Linux/macOS
                    logger.info("Unix系统：发送SIGTERM信号进行优雅关闭...")
                    # 发送SIGTERM信号进行优雅关闭
                    os.kill(current_pid, signal.SIGTERM)

                logger.info("重启命令已执行，应用将重新启动")

            except Exception as restart_error:
                logger.error(f"执行重启时发生错误: {str(restart_error)}")
                # 如果重启失败，强制退出，让进程管理器重启
                try:
                    os._exit(1)
                except:
                    pass

        # 启动重启线程
        restart_thread = threading.Thread(target=delayed_restart, daemon=True)
        restart_thread.start()

        logger.info(f"应用重启请求已接受，PID: {current_pid}")

        return SuccessResponse(
            data={
                "restart_requested": True,
                "current_pid": current_pid,
                "estimated_downtime": "5-15秒",
                "timestamp": datetime.now().isoformat(),
                "message": "应用将在几秒钟后重启"
            },
            message="应用重启请求已接收，服务将重新启动"
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

        # 读取真实日志文件
        real_logs = []
        try:
            if os.path.exists(log_file):
                # 读取日志文件最后N行
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()

                # 过滤日志级别
                filtered_lines = []
                if level.lower() == 'all':
                    filtered_lines = all_lines
                else:
                    level_upper = level.upper()
                    for line in all_lines:
                        if level_upper in line:
                            filtered_lines.append(line)
                        elif 'DEBUG' in line and level_upper in ['INFO', 'WARNING', 'ERROR']:
                            filtered_lines.append(line)
                        elif 'INFO' in line and level_upper in ['WARNING', 'ERROR']:
                            filtered_lines.append(line)
                        elif 'WARNING' in line and level_upper == 'ERROR':
                            filtered_lines.append(line)

                # 取最后N行
                recent_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines

                # 解析日志格式
                for line in recent_lines:
                    try:
                        # 尝试解析标准日志格式：时间戳 - 模块名 - 级别 - 消息
                        if ' - ' in line:
                            parts = line.strip().split(' - ', 3)
                            if len(parts) >= 4:
                                timestamp_str = parts[0]
                                module = parts[1]
                                level_str = parts[2]
                                message = parts[3]

                                real_logs.append({
                                    "timestamp": timestamp_str,
                                    "level": level_str,
                                    "message": message,
                                    "module": module
                                })
                            else:
                                # 简单格式处理
                                real_logs.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "level": "INFO",
                                    "message": line.strip(),
                                    "module": "unknown"
                                })
                        else:
                            real_logs.append({
                                "timestamp": datetime.now().isoformat(),
                                "level": "INFO",
                                "message": line.strip(),
                                "module": "unknown"
                            })
                    except Exception as e:
                        # 解析失败时保留原始内容
                        real_logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": line.strip(),
                            "module": "unknown"
                        })
            else:
                real_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "WARNING",
                    "message": f"日志文件不存在: {log_file}",
                    "module": "system"
                })

        except Exception as e:
            logger.error(f"读取日志文件失败: {str(e)}")
            real_logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"读取日志失败: {str(e)}",
                "module": "system"
            })

        return {
            "success": True,
            "data": {
                "logs": real_logs,
                "total_lines": len(real_logs),
                "log_file": log_file,
                "filter_level": level,
                "file_exists": os.path.exists(log_file),
                "file_size": os.path.getsize(log_file) if os.path.exists(log_file) else 0
            },
            "message": "获取应用日志成功"
        }

    except Exception as e:
        logger.error(f"获取应用日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取应用日志失败: {str(e)}")


@router.get("/logs/download", summary="下载日志文件")
async def download_log_file(
    date: str = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    下载日志文件

    - **date**: 指定日期的日志文件 (格式: YYYY-MM-DD)，不指定则下载当前日志文件
    """
    logger.info(f"下载日志文件请求: date={date}")

    try:
        from fastapi.responses import FileResponse
        import datetime

        # 确定要下载的日志文件路径
        if date:
            try:
                # 验证日期格式
                datetime.datetime.strptime(date, "%Y-%m-%d")
                log_file = f"../data/logs/xiaoyao-search-{date}.log"
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式无效，请使用YYYY-MM-DD格式")
        else:
            log_file = os.getenv("LOG_FILE", "../data/logs/app.log")

        # 检查文件是否存在
        if not os.path.exists(log_file):
            raise HTTPException(status_code=404, detail="指定的日志文件不存在")

        # 检查文件大小，限制最大50MB
        file_size = os.path.getsize(log_file)
        max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"日志文件过大({file_size/1024/1024:.1f}MB)，超过最大限制(50MB)"
            )

        # 确定下载文件名
        if date:
            filename = f"xiaoyao-search-{date}.log"
        else:
            filename = "xiaoyao-search-app.log"

        logger.info(f"日志文件下载开始: file={log_file}, size={file_size}, filename={filename}")

        # 返回文件下载响应
        return FileResponse(
            path=log_file,
            filename=filename,
            media_type="text/plain"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载日志文件失败: date={date}, 错误={str(e)}")
        raise HTTPException(status_code=500, detail=f"下载日志文件失败: {str(e)}")


@router.delete("/cache", response_model=SuccessResponse, summary="清理缓存")
async def clear_cache():
    """
    清理系统缓存

    清理各种类型的缓存：
    - 向量搜索缓存
    - 全文搜索缓存
    - AI模型缓存
    - 临时文件
    - 日志文件
    """
    logger.info("开始清理系统缓存")

    try:
        import os
        import shutil
        import glob
        from pathlib import Path
        from datetime import datetime, timedelta

        cache_cleared = {
            "vector_cache": False,
            "search_cache": False,
            "ai_model_cache": False,
            "temp_files": False,
            "log_files": False,
            "session_cache": False,
            "total_freed_space": 0
        }

        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        data_root = project_root / "data"

        # 1. 清理向量搜索缓存（Faiss索引内存缓存）
        try:
            from app.services.search_service import get_search_service
            search_service = get_search_service()

            # 清理搜索服务内部缓存
            if hasattr(search_service, 'clear_cache'):
                search_service.clear_cache()
                cache_cleared["vector_cache"] = True
                logger.info("向量搜索缓存清理完成")
            elif hasattr(search_service, '_search_cache'):
                search_service._search_cache.clear()
                cache_cleared["vector_cache"] = True
                logger.info("向量搜索缓存清理完成")

        except Exception as e:
            logger.warning(f"清理向量搜索缓存失败: {str(e)}")
            cache_cleared["vector_cache"] = False

        # 2. 清理全文搜索缓存（Whoosh查询缓存）
        try:
            whoosh_cache_path = data_root / "indexes" / "whoosh_cache"
            if whoosh_cache_path.exists():
                shutil.rmtree(whoosh_cache_path)
                whoosh_cache_path.mkdir(parents=True, exist_ok=True)
                cache_cleared["search_cache"] = True
                logger.info("全文搜索缓存清理完成")

        except Exception as e:
            logger.warning(f"清理全文搜索缓存失败: {str(e)}")
            cache_cleared["search_cache"] = False

        # 3. 清理AI模型缓存
        try:
            ai_model_cache_path = data_root / "models" / "cache"
            if ai_model_cache_path.exists():
                # 清理transformers缓存
                transformers_cache = ai_model_cache_path / "transformers"
                if transformers_cache.exists():
                    shutil.rmtree(transformers_cache)
                    cache_cleared["ai_model_cache"] = True

                # 清理其他模型缓存文件
                for cache_file in ai_model_cache_path.glob("**/*.cache"):
                    try:
                        cache_file.unlink()
                        cache_cleared["ai_model_cache"] = True
                    except Exception:
                        pass

                logger.info("AI模型缓存清理完成")

        except Exception as e:
            logger.warning(f"清理AI模型缓存失败: {str(e)}")
            cache_cleared["ai_model_cache"] = False

        # 4. 清理临时文件
        try:
            temp_paths = [
                data_root / "temp",
                data_root / "uploads" / "temp",
                project_root / "temp",
                Path.cwd() / "temp"
            ]

            total_temp_size = 0
            for temp_path in temp_paths:
                if temp_path.exists():
                    # 计算临时文件夹大小
                    for file_path in temp_path.rglob("*"):
                        if file_path.is_file():
                            try:
                                total_temp_size += file_path.stat().st_size
                                file_path.unlink()
                            except Exception:
                                pass

                    # 删除空的子目录
                    for dir_path in sorted(temp_path.rglob("*"), reverse=True):
                        if dir_path.is_dir() and not any(dir_path.iterdir()):
                            try:
                                dir_path.rmdir()
                            except Exception:
                                pass

            if total_temp_size > 0:
                cache_cleared["temp_files"] = True
                cache_cleared["total_freed_space"] += total_temp_size
                logger.info(f"临时文件清理完成，释放空间: {total_temp_size / (1024*1024):.2f}MB")

        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
            cache_cleared["temp_files"] = False

        # 5. 清理旧的日志文件（保留最近7天）
        try:
            log_path = data_root / "logs"
            if log_path.exists():
                cutoff_date = datetime.now() - timedelta(days=7)
                total_log_size = 0

                for log_file in log_path.glob("*.log*"):
                    try:
                        # 检查文件修改时间
                        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_mtime < cutoff_date:
                            total_log_size += log_file.stat().st_size
                            log_file.unlink()
                    except Exception:
                        pass

                if total_log_size > 0:
                    cache_cleared["log_files"] = True
                    cache_cleared["total_freed_space"] += total_log_size
                    logger.info(f"旧日志文件清理完成，释放空间: {total_log_size / (1024*1024):.2f}MB")

        except Exception as e:
            logger.warning(f"清理日志文件失败: {str(e)}")
            cache_cleared["log_files"] = False

        # 6. 清理会话缓存和应用运行时缓存
        try:
            import tempfile
            import sys

            # 清理Python缓存文件
            python_cache_patterns = [
                project_root / "**/__pycache__",
                project_root / "**/*.pyc",
                project_root / "**/*.pyo"
            ]

            for pattern in python_cache_patterns:
                for cache_item in project_root.glob(str(pattern)):
                    try:
                        if cache_item.is_dir():
                            shutil.rmtree(cache_item)
                        else:
                            cache_item.unlink()
                        cache_cleared["session_cache"] = True
                    except Exception:
                        pass

            # 清理系统临时目录中的应用缓存
            system_temp = Path(tempfile.gettempdir())
            app_temp_files = list(system_temp.glob("xiaoyao_search_*"))
            for temp_file in app_temp_files:
                try:
                    if temp_file.is_dir():
                        shutil.rmtree(temp_file)
                    else:
                        temp_file.unlink()
                    cache_cleared["session_cache"] = True
                except Exception:
                    pass

            logger.info("会话缓存清理完成")

        except Exception as e:
            logger.warning(f"清理会话缓存失败: {str(e)}")
            cache_cleared["session_cache"] = False

        # 计算清理状态
        cleared_items = sum(1 for k, v in cache_cleared.items() if k.endswith("_cache") and v)
        total_items = sum(1 for k in cache_cleared.keys() if k.endswith("_cache"))

        cache_cleared["clearance_rate"] = cleared_items / total_items if total_items > 0 else 0
        cache_cleared["total_cleared_items"] = cleared_items
        cache_cleared["total_cache_items"] = total_items

        # 转换空间大小为MB
        if cache_cleared["total_freed_space"] > 0:
            cache_cleared["freed_space_mb"] = round(cache_cleared["total_freed_space"] / (1024 * 1024), 2)
        else:
            cache_cleared["freed_space_mb"] = 0

        logger.info(f"系统缓存清理完成: 清理项目 {cleared_items}/{total_items}, 释放空间 {cache_cleared['freed_space_mb']}MB")

        return SuccessResponse(
            data=cache_cleared,
            message=f"系统缓存清理完成，清理率 {cache_cleared['clearance_rate']:.1%}，释放空间 {cache_cleared['freed_space_mb']}MB"
        )

    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")