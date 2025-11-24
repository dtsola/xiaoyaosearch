"""
索引管理API路由
提供文件索引管理相关的API接口
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.schemas.requests import IndexCreateRequest, IndexUpdateRequest
from app.schemas.responses import (
    IndexJobInfo, IndexCreateResponse, IndexListResponse, SuccessResponse
)
from app.schemas.enums import JobType, JobStatus
from app.models.index_job import IndexJobModel
from app.models.file import FileModel

router = APIRouter(prefix="/api/index", tags=["索引管理"])
logger = get_logger(__name__)


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
    - **file_types**: 支持文件类型
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
            IndexJobModel.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
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
            status=JobStatus.PENDING
        )
        db.add(index_job)
        db.commit()
        db.refresh(index_job)

        # 添加后台任务
        background_tasks.add_task(
            run_index_task,
            index_job.id,
            request.folder_path,
            request.file_types,
            request.recursive
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

        logger.info(f"索引状态查询完成: id={index_id}, status={index_job.status}")

        return IndexCreateResponse(
            data=IndexJobInfo(**index_job.to_dict()),
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
            query = query.filter(IndexJobModel.status == status.value)

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
        if index_job.status == JobStatus.PROCESSING:
            index_job.fail_job("任务被手动删除")
            logger.info(f"停止正在运行的索引任务: id={index_id}")

        # 删除相关的文件索引记录
        deleted_files = db.query(FileModel).filter(
            FileModel.file_path.like(f"{folder_path}%")
        ).count()
        db.query(FileModel).filter(
            FileModel.file_path.like(f"{folder_path}%")
        ).delete()

        # 删除索引任务
        db.delete(index_job)
        db.commit()

        logger.info(f"索引删除完成: id={index_id}, 删除文件数={deleted_files}")

        return SuccessResponse(
            data={
                "deleted_index_id": index_id,
                "deleted_files_count": deleted_files,
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

        if index_job.status != JobStatus.PROCESSING:
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


@router.get("/files", summary="已索引文件列表")
async def get_indexed_files(
    folder_path: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取已索引的文件列表

    - **folder_path**: 文件夹路径过滤
    - **file_type**: 文件类型过滤
    - **limit**: 返回结果数量
    - **offset**: 偏移量
    """
    logger.info(f"获取已索引文件: folder={folder_path}, type={file_type}")

    try:
        # 构建查询
        query = db.query(FileModel)

        # 应用过滤条件
        if folder_path:
            query = query.filter(FileModel.file_path.like(f"{folder_path}%"))
        if file_type:
            query = query.filter(FileModel.file_type == file_type)

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


async def run_index_task(
    index_id: int,
    folder_path: str,
    file_types: List[str],
    recursive: bool
):
    """
    执行索引任务（后台任务）

    Args:
        index_id: 索引任务ID
        folder_path: 文件夹路径
        file_types: 支持的文件类型
        recursive: 是否递归搜索
    """
    logger.info(f"开始执行索引任务: id={index_id}, folder={folder_path}")

    # TODO: 实现实际的索引逻辑
    # 这里暂时只是模拟任务执行
    import asyncio
    from app.core.database import SessionLocal

    await asyncio.sleep(5)  # 模拟处理时间

    # 更新任务状态
    db = SessionLocal()
    try:
        index_job = db.query(IndexJobModel).filter(
            IndexJobModel.id == index_id
        ).first()

        if index_job and index_job.status == JobStatus.PENDING:
            index_job.start_job()
            index_job.total_files = 100
            index_job.processed_files = 95
            index_job.error_count = 2
            index_job.complete_job()
            db.commit()

        logger.info(f"索引任务完成: id={index_id}")

    except Exception as e:
        logger.error(f"索引任务执行失败: {str(e)}")
        if index_job:
            index_job.fail_job(str(e))
            db.commit()
    finally:
        db.close()