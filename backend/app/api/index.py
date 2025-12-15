"""
索引管理API路由
提供文件索引管理相关的API接口
"""
import os
import asyncio
import threading
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.core.config import get_settings
from app.schemas.requests import IndexCreateRequest, IndexUpdateRequest
from app.schemas.responses import (
    IndexJobInfo, IndexCreateResponse, IndexListResponse, SuccessResponse
)
from app.schemas.enums import JobType, JobStatus
from app.models.index_job import IndexJobModel
from app.utils.enum_helpers import get_enum_value
from app.models.file import FileModel
from app.services.file_index_service import FileIndexService, get_file_index_service as get_global_file_index_service

router = APIRouter(prefix="/api/index", tags=["索引管理"])
logger = get_logger(__name__)
settings = get_settings()

# 全局文件索引服务实例（单例）
_file_index_service: Optional[FileIndexService] = None


def get_file_index_service() -> FileIndexService:
    """获取文件索引服务实例（单例模式）"""
    global _file_index_service
    if _file_index_service is None:
        faiss_path, whoosh_path = settings.get_index_paths()
        _file_index_service = FileIndexService(
            data_root=settings.index.data_root,
            faiss_index_path=faiss_path,
            whoosh_index_path=whoosh_path,
            use_chinese_analyzer=settings.index.use_chinese_analyzer,
            scanner_config={
                'max_workers': settings.index.scanner_max_workers,
                'max_file_size': settings.index.max_file_size,
                'supported_extensions': set(settings.index.supported_extensions)
            },
            parser_config={
                'max_content_length': settings.index.max_content_length
            }
        )
    return get_global_file_index_service()


@router.post("/create", response_model=IndexCreateResponse, summary="创建索引")
async def create_index(
    request: IndexCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    创建文件索引

    对指定文件夹进行文件扫描和索引创建

    - **folder_path**: 索引文件夹路径
    - **file_types**: 支持文件类型（可选，使用配置的默认值）
    - **recursive**: 是否递归搜索子文件夹
    """
    logger.info(f"创建索引请求: folder='{request.folder_path}', recursive={request.recursive}")

    try:
        # 验证文件夹路径
        if not os.path.exists(request.folder_path):
            raise ValidationException(f"文件夹不存在: {request.folder_path}")

        if not os.path.isdir(request.folder_path):
            raise ValidationException(f"路径不是文件夹: {request.folder_path}")

        # 检查是否有正在运行的索引任务
        existing_job = db.query(IndexJobModel).filter(
            IndexJobModel.folder_path == request.folder_path,
            IndexJobModel.status.in_([get_enum_value(JobStatus.PENDING), get_enum_value(JobStatus.PROCESSING)])
        ).first()

        if existing_job:
            logger.info(f"文件夹已在索引中: {request.folder_path}")
            return IndexCreateResponse(
                data=IndexJobInfo(**existing_job.to_dict()),
                message="文件夹正在索引中"
            )

        # 创建新的索引任务
        index_job = IndexJobModel(
            folder_path=request.folder_path,
            job_type=JobType.CREATE,
            status=get_enum_value(JobStatus.PENDING)
        )
        db.add(index_job)
        db.commit()
        db.refresh(index_job)

        # 添加后台任务
        background_tasks.add_task(
            run_full_index_task,
            index_job.id,
            request.folder_path,
            request.recursive,
            request.file_types
        )

        logger.info(f"索引任务已创建: id={index_job.id}")

        return IndexCreateResponse(
            data=IndexJobInfo(**index_job.to_dict()),
            message="索引任务已创建并开始执行"
        )

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建索引失败: {str(e)}")


@router.post("/update", response_model=IndexCreateResponse, summary="更新索引")
async def update_index(
    request: IndexUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    增量更新文件索引

    对已索引的文件夹进行增量更新，只处理新增或修改的文件

    - **folder_path**: 索引文件夹路径
    - **recursive**: 是否递归搜索子文件夹
    """
    logger.info(f"更新索引请求: folder='{request.folder_path}'")

    try:
        # 验证文件夹路径
        if not os.path.exists(request.folder_path):
            raise ValidationException(f"文件夹不存在: {request.folder_path}")

        # 检查是否有正在运行的索引任务
        existing_job = db.query(IndexJobModel).filter(
            IndexJobModel.folder_path == request.folder_path,
            IndexJobModel.status.in_([get_enum_value(JobStatus.PENDING), get_enum_value(JobStatus.PROCESSING)])
        ).first()

        if existing_job:
            logger.info(f"文件夹正在索引中: {request.folder_path}")
            return IndexCreateResponse(
                data=IndexJobInfo(**existing_job.to_dict()),
                message="文件夹正在索引中"
            )

        # 创建更新任务
        index_job = IndexJobModel(
            folder_path=request.folder_path,
            job_type=JobType.UPDATE,
            status=get_enum_value(JobStatus.PENDING)
        )
        db.add(index_job)
        db.commit()
        db.refresh(index_job)

        # 添加后台任务
        background_tasks.add_task(
            run_incremental_index_task,
            index_job.id,
            request.folder_path,
            request.recursive,
            request.file_types
        )

        logger.info(f"增量索引任务已创建: id={index_job.id}")

        return IndexCreateResponse(
            data=IndexJobInfo(**index_job.to_dict()),
            message="增量索引任务已创建并开始执行"
        )

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"创建增量索引失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建增量索引失败: {str(e)}")


@router.get("/status", summary="获取索引系统状态")
async def get_system_status(
    db: Session = Depends(get_db)
):
    """
    获取索引系统的整体状态

    包括统计信息、支持的格式、服务状态等
    """
    logger.info("获取索引系统状态")

    try:
        # 获取文件索引服务
        index_service = get_file_index_service()

        # 获取索引统计
        index_stats = index_service.get_index_status()

        # 获取支持的格式
        supported_formats = index_service.get_supported_formats()

        # 获取数据库统计
        total_files = db.query(FileModel).count()
        indexed_files = db.query(FileModel).filter(FileModel.is_indexed == True).count()
        pending_files = db.query(FileModel).filter(FileModel.index_status == get_enum_value(JobStatus.PENDING)).count()
        failed_files = db.query(FileModel).filter(FileModel.index_status == get_enum_value(JobStatus.FAILED)).count()

        # 获取最近的任务统计
        recent_jobs = db.query(IndexJobModel).order_by(IndexJobModel.created_at.desc()).limit(10).all()
        job_stats = {
            'total_jobs': len(recent_jobs),
            'completed_jobs': len([j for j in recent_jobs if j.status == get_enum_value(JobStatus.COMPLETED)]),
            'failed_jobs': len([j for j in recent_jobs if j.status == get_enum_value(JobStatus.FAILED)]),
            'processing_jobs': len([j for j in recent_jobs if j.status == get_enum_value(JobStatus.PROCESSING)])
        }

        return {
            "success": True,
            "data": {
                "index_stats": index_stats,
                "supported_formats": supported_formats,
                "database_stats": {
                    "total_files": total_files,
                    "indexed_files": indexed_files,
                    "pending_files": pending_files,
                    "failed_files": failed_files
                },
                "job_stats": job_stats,
                "config": {
                    "max_file_size": settings.index.max_file_size,
                    "use_chinese_analyzer": settings.index.use_chinese_analyzer,
                    "scanner_workers": settings.index.scanner_max_workers
                }
            },
            "message": "获取索引系统状态成功"
        }

    except Exception as e:
        logger.error(f"获取索引系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取索引系统状态失败: {str(e)}")


@router.get("/status/{index_id}", response_model=IndexCreateResponse, summary="查询索引状态")
async def get_index_status(
    index_id: int,
    db: Session = Depends(get_db)
):
    """
    获取索引任务状态

    - **index_id**: 索引任务ID
    """
    logger.info(f"查询索引状态: id={index_id}")

    try:
        # 查询索引任务
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if not index_job:
            raise ResourceNotFoundException("索引任务", str(index_id))

        # 获取模型字典并过滤只保留IndexJobInfo需要的字段
        model_dict = index_job.to_dict()
        job_dict = {
            'index_id': model_dict['index_id'],
            'folder_path': model_dict['folder_path'],
            'status': model_dict['status'],
            'progress': model_dict['progress'],
            'total_files': model_dict['total_files'],
            'processed_files': model_dict['processed_files'],
            'error_count': model_dict['error_count'],
            'started_at': model_dict['started_at'],
            'completed_at': model_dict['completed_at'],
            'error_message': model_dict['error_message']
        }

        logger.info(f"索引状态查询完成: id={index_id}, status={index_job.status}")

        return IndexCreateResponse(
            data=IndexJobInfo(**job_dict),
            message="索引状态查询成功"
        )

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"查询索引状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询索引状态失败: {str(e)}")


@router.get("/list", response_model=IndexListResponse, summary="索引列表")
async def get_index_list(
    status: Optional[JobStatus] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取索引任务列表

    - **status**: 任务状态过滤
    - **limit**: 返回结果数量
    - **offset**: 偏移量
    """
    logger.info(f"获取索引列表: status={status}, limit={limit}, offset={offset}")

    try:
        # 构建查询
        query = db.query(IndexJobModel)

        # 应用过滤条件
        if status:
            query = query.filter(IndexJobModel.status == get_enum_value(status))

        # 获取总数
        total = query.count()

        # 分页查询
        index_jobs = query.order_by(
            IndexJobModel.created_at.desc()
        ).offset(offset).limit(limit).all()

        # 转换为响应格式
        job_list = [
            IndexJobInfo(**job.to_dict())
            for job in index_jobs
        ]

        logger.info(f"返回索引列表: 数量={len(job_list)}, 总计={total}")

        return IndexListResponse(
            data={
                "indexes": [job.dict() for job in job_list],
                "total": total,
                "limit": limit,
                "offset": offset
            },
            message="获取索引列表成功"
        )

    except Exception as e:
        logger.error(f"获取索引列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取索引列表失败: {str(e)}")


@router.delete("/{index_id}", response_model=SuccessResponse, summary="删除索引")
async def delete_index(
    index_id: int,
    db: Session = Depends(get_db)
):
    """
    删除索引任务和相关数据

    - **index_id**: 索引任务ID
    """
    logger.info(f"删除索引: id={index_id}")

    try:
        # 查询索引任务
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if not index_job:
            raise ResourceNotFoundException("索引任务", str(index_id))

        folder_path = index_job.folder_path

        # 如果任务正在运行，标记为失败
        if index_job.status == get_enum_value(JobStatus.PROCESSING):
            index_job.fail_job("任务被手动删除")
            logger.info(f"停止正在运行的索引任务: id={index_id}")

        # 删除相关的文件索引记录
        deleted_files = db.query(FileModel).filter(
            FileModel.file_path.like(f"{folder_path}%")
        ).count()

        # 获取要删除的文件列表，用于清理索引
        files_to_delete = db.query(FileModel).filter(
            FileModel.file_path.like(f"{folder_path}%")
        ).all()

        db.query(FileModel).filter(
            FileModel.file_path.like(f"{folder_path}%")
        ).delete()

        # 清理向量索引和全文索引
        index_service = get_file_index_service()
        index_deleted = 0
        chunk_deleted = 0

        try:
            # 删除文件索引
            for file_record in files_to_delete:
                result = index_service.delete_file_from_index(file_record.file_path)
                if result.get('success', False):
                    index_deleted += 1

            # 清理分块索引
            from app.services.chunk_index_service import get_chunk_index_service
            chunk_service = get_chunk_index_service()
            chunk_result = chunk_service.delete_files_by_folder(folder_path)
            chunk_deleted = chunk_result.get('deleted_count', 0)

            logger.info(f"索引清理完成: 文件索引={index_deleted}, 分块索引={chunk_deleted}")

        except Exception as e:
            logger.warning(f"清理索引时出错: {e}")

        # 删除索引任务
        db.delete(index_job)
        db.commit()

        logger.info(f"索引删除完成: id={index_id}, 数据库文件数={deleted_files}, 文件索引数={index_deleted}, 分块索引数={chunk_deleted}")

        return SuccessResponse(
            data={
                "deleted_index_id": index_id,
                "deleted_files_count": deleted_files,
                "deleted_index_count": index_deleted,
                "deleted_chunk_count": chunk_deleted,
                "folder_path": folder_path
            },
            message="索引删除成功"
        )

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"删除索引失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除索引失败: {str(e)}")


@router.post("/{index_id}/stop", response_model=SuccessResponse, summary="停止索引")
async def stop_index(
    index_id: int,
    db: Session = Depends(get_db)
):
    """
    停止正在运行的索引任务

    - **index_id**: 索引任务ID
    """
    logger.info(f"停止索引任务: id={index_id}")

    try:
        # 查询索引任务
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if not index_job:
            raise ResourceNotFoundException("索引任务", str(index_id))

        if index_job.status != get_enum_value(JobStatus.PROCESSING):
            raise ValidationException("只能停止正在运行的索引任务")

        # 标记任务为失败
        index_job.fail_job("任务被手动停止")
        db.commit()

        logger.info(f"索引任务已停止: id={index_id}")

        return SuccessResponse(
            data={
                "stopped_index_id": index_id,
                "processed_files": index_job.processed_files,
                "total_files": index_job.total_files
            },
            message="索引任务已停止"
        )

    except (ResourceNotFoundException, ValidationException):
        raise
    except Exception as e:
        logger.error(f"停止索引任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止索引任务失败: {str(e)}")


@router.post("/backup", response_model=SuccessResponse, summary="备份索引")
async def backup_index(
    backup_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    备份当前索引

    - **backup_name**: 备份名称（可选，默认使用时间戳）
    """
    logger.info(f"备份索引: name={backup_name}")

    try:
        # 获取文件索引服务
        index_service = get_file_index_service()

        # 执行备份
        backup_result = index_service.backup_indexes(backup_name)

        if backup_result['success']:
            return SuccessResponse(
                data=backup_result,
                message="索引备份成功"
            )
        else:
            raise HTTPException(status_code=500, detail="索引备份失败")

    except Exception as e:
        logger.error(f"备份索引失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"备份索引失败: {str(e)}")


@router.get("/files", summary="已索引文件列表")
async def get_indexed_files(
    folder_path: Optional[str] = None,
    file_type: Optional[str] = None,
    index_status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取已索引的文件列表

    - **folder_path**: 文件夹路径过滤
    - **file_type**: 文件类型过滤
    - **index_status**: 索引状态过滤
    - **limit**: 返回结果数量
    - **offset**: 偏移量
    """
    logger.info(f"获取已索引文件: folder={folder_path}, type={file_type}, status={index_status}")

    try:
        # 构建查询
        query = db.query(FileModel)

        # 应用过滤条件
        if folder_path:
            query = query.filter(FileModel.file_path.like(f"{folder_path}%"))
        if file_type:
            query = query.filter(FileModel.file_type == file_type)
        if index_status:
            query = query.filter(FileModel.index_status == index_status)

        # 获取总数
        total = query.count()

        # 分页查询
        files = query.order_by(
            FileModel.indexed_at.desc()
        ).offset(offset).limit(limit).all()

        # 转换为响应格式
        file_list = [file.to_dict() for file in files]

        logger.info(f"返回已索引文件: 数量={len(file_list)}, 总计={total}")

        return {
            "success": True,
            "data": {
                "files": file_list,
                "total": total,
                "limit": limit,
                "offset": offset
            },
            "message": "获取已索引文件成功"
        }

    except Exception as e:
        logger.error(f"获取已索引文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取已索引文件失败: {str(e)}")


@router.delete("/files/{file_id}", response_model=SuccessResponse, summary="删除文件索引")
async def delete_file_index(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    从索引中删除单个文件

    - **file_id**: 文件ID
    """
    logger.info(f"删除文件索引: file_id={file_id}")

    try:
        # 查询文件
        file_model = db.query(FileModel).filter(
            FileModel.id == file_id
        ).first()

        if not file_model:
            raise ResourceNotFoundException("文件", str(file_id))

        # 从索引服务中删除
        index_service = get_file_index_service()
        delete_result = index_service.delete_file_from_index(file_model.file_path)

        if delete_result['success']:
            # 从数据库中删除记录
            db.delete(file_model)
            db.commit()

            return SuccessResponse(
                data={
                    "deleted_file_id": file_id,
                    "file_path": file_model.file_path
                },
                message="文件索引删除成功"
            )
        else:
            raise HTTPException(status_code=500, detail="从索引中删除文件失败")

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"删除文件索引失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文件索引失败: {str(e)}")


async def run_full_index_task(
    index_id: int,
    folder_path: str,
    recursive: bool = True,
    file_types: Optional[List[str]] = None
):
    """
    执行完整索引任务（后台任务）

    Args:
        index_id: 索引任务ID
        folder_path: 文件夹路径
        recursive: 是否递归搜索
        file_types: 指定文件类型过滤列表，为None时使用默认配置
    """
    # 获取 logger 实例
    from app.core.logging_config import get_logger
    task_logger = get_logger("background_task")

    task_logger.info(f"开始执行完整索引任务: id={index_id}, folder={folder_path}")
    task_logger.debug(f"当前线程ID: {threading.get_ident()}")

    from app.core.database import SessionLocal

    # 获取数据库会话
    db = SessionLocal()
    try:
        # 获取索引任务
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if not index_job or index_job.status != get_enum_value(JobStatus.PENDING):
            task_logger.warning(f"索引任务不存在或状态不正确: id={index_id}")
            return

        # 开始任务
        index_job.start_job()
        db.commit()

        # 定义进度回调
        def progress_callback(message: str, progress: float):
            task_logger.info(f"索引进度[{index_id}]: {message} - {progress:.1f}%")
            # 注意：现在进度由_file_index_service直接更新数据库，这里只记录日志

        # 处理文件类型过滤：如果未指定file_types，则使用DefaultConfig支持的所有类型
        if file_types:
            # 将文件类型扩展名格式统一
            filtered_extensions = set()
            for ext in file_types:
                if not ext.startswith('.'):
                    ext = '.' + ext
                filtered_extensions.add(ext.lower())
            task_logger.info(f"使用指定的文件类型过滤: {filtered_extensions}")
        else:
            # 使用DefaultConfig支持的所有文件类型
            filtered_extensions = settings.default.get_supported_extensions()
            task_logger.info(f"使用DefaultConfig默认支持的所有文件类型: {filtered_extensions}")

        # 使用全局单例索引服务
        temp_index_service = get_global_file_index_service()

        result = await temp_index_service.build_full_index(
            scan_paths=[folder_path],
            progress_callback=progress_callback
        )

        # 更新任务结果
        if result['success']:
            index_job.total_files = result.get('total_files_found', 0)
            index_job.processed_files = result.get('documents_indexed', 0)
            index_job.error_count = result.get('failed_files', 0)
            index_job.complete_job()
            task_logger.info(f"完整索引任务完成: id={index_id}, 成功索引 {index_job.processed_files} 个文件")
        else:
            index_job.fail_job(result.get('error', '未知错误'))
            task_logger.error(f"完整索引任务失败: id={index_id}, 错误: {result.get('error')}")

        db.commit()

    except Exception as e:
        task_logger.error(f"完整索引任务执行异常: {str(e)}")
        if index_job:
            index_job.fail_job(str(e))
            db.commit()
    finally:
        db.close()


async def run_incremental_index_task(
    index_id: int,
    folder_path: str,
    recursive: bool = True,
    file_types: Optional[List[str]] = None
):
    """
    执行增量索引任务（后台任务）

    Args:
        index_id: 索引任务ID
        folder_path: 文件夹路径
        recursive: 是否递归搜索
        file_types: 指定文件类型过滤列表，为None时使用默认配置
    """
    # 获取 logger 实例
    from app.core.logging_config import get_logger
    task_logger = get_logger("background_task")

    task_logger.info(f"开始执行增量索引任务: id={index_id}, folder={folder_path}")

    from app.core.database import SessionLocal

    # 获取数据库会话
    db = SessionLocal()
    try:
        # 获取索引任务
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if not index_job or index_job.status != get_enum_value(JobStatus.PENDING):
            task_logger.warning(f"增量索引任务不存在或状态不正确: id={index_id}")
            return

        # 开始任务
        index_job.start_job()
        db.commit()

        # 处理文件类型过滤：如果未指定file_types，则使用DefaultConfig支持的所有类型
        if file_types:
            # 将文件类型扩展名格式统一
            filtered_extensions = set()
            for ext in file_types:
                if not ext.startswith('.'):
                    ext = '.' + ext
                filtered_extensions.add(ext.lower())
            task_logger.info(f"增量索引使用指定的文件类型过滤: {filtered_extensions}")
        else:
            # 使用DefaultConfig支持的所有文件类型
            filtered_extensions = settings.default.get_supported_extensions()
            task_logger.info(f"增量索引使用DefaultConfig默认支持的所有文件类型: {filtered_extensions}")

        # 使用全局单例索引服务
        temp_index_service = get_global_file_index_service()

        # 定义进度更新回调函数
        def progress_callback(current: int, total: int, stage: str = ""):
            """增量索引进度更新回调"""
            if total > 0:
                progress = (current / total) * 100.0
                index_job.update_progress(int(progress))
                db.commit()
                task_logger.debug(f"增量索引进度更新: {current}/{total} ({progress:.1f}%) - {stage}")

        result = await temp_index_service.update_incremental_index(
            scan_paths=[folder_path],
            progress_callback=progress_callback
        )

        # 更新任务结果
        if result['success']:
            index_job.total_files = result.get('changed_files', 0) + result.get('deleted_files', 0)
            index_job.processed_files = result.get('changed_files', 0)
            index_job.error_count = 0  # 增量更新通常不会有错误
            index_job.complete_job()
            task_logger.info(f"增量索引任务完成: id={index_id}, 处理 {index_job.processed_files} 个变更文件")
        else:
            index_job.fail_job(result.get('error', '未知错误'))
            task_logger.error(f"增量索引任务失败: id={index_id}, 错误: {result.get('error')}")

        db.commit()

    except Exception as e:
        task_logger.error(f"增量索引任务执行异常: {str(e)}")
        if index_job:
            index_job.fail_job(str(e))
            db.commit()
    finally:
        db.close()