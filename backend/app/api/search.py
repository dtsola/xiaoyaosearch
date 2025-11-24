"""
搜索服务API路由
提供文件搜索相关的API接口
"""
import time
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.schemas.requests import SearchRequest, MultimodalRequest, SearchHistoryRequest
from app.schemas.responses import (
    SearchResponse, MultimodalResponse, SearchHistoryInfo,
    SearchHistoryResponse, SearchResult, FileInfo
)
from app.schemas.enums import InputType, SearchType
from app.models.search_history import SearchHistoryModel

router = APIRouter(prefix="/api/search", tags=["搜索服务"])
logger = get_logger(__name__)


@router.post("/", response_model=SearchResponse, summary="文本搜索")
async def search_files(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    执行文件搜索

    支持语义搜索、全文搜索和混合搜索三种模式

    - **query**: 搜索查询词 (1-500字符)
    - **input_type**: 输入类型 (text/voice/image)
    - **search_type**: 搜索类型 (semantic/fulltext/hybrid)
    - **limit**: 返回结果数量 (1-100)
    - **threshold**: 相似度阈值 (0.0-1.0)
    - **file_types**: 文件类型过滤
    """
    start_time = time.time()
    logger.info(f"收到搜索请求: query='{request.query}', type={request.search_type}")

    try:
        # TODO: 实现实际的搜索逻辑
        # 这里暂时返回模拟数据
        mock_results = [
            SearchResult(
                file_id=1,
                file_name="示例文档.pdf",
                file_path="/path/to/example.pdf",
                file_type="document",
                relevance_score=0.95,
                preview_text="这是一个示例文档的预览文本...",
                highlight="这是<em>示例</em>文档的预览文本",
                created_at="2024-01-15T10:30:00Z",
                modified_at="2024-01-15T10:30:00Z",
                file_size=1024000,
                match_type=request.search_type.value
            )
        ]

        # 计算响应时间
        response_time = time.time() - start_time

        # 保存搜索历史
        history_record = SearchHistoryModel(
            search_query=request.query,
            input_type=request.input_type.value,
            search_type=request.search_type.value,
            ai_model_used="mock_model",
            result_count=len(mock_results),
            response_time=response_time
        )
        db.add(history_record)
        db.commit()

        logger.info(f"搜索完成: 结果数量={len(mock_results)}, 耗时={response_time:.2f}秒")

        return SearchResponse(
            data={
                "results": [result.dict() for result in mock_results],
                "total": len(mock_results),
                "search_time": round(response_time, 2),
                "query_used": request.query,
                "input_processed": request.input_type != InputType.TEXT
            },
            message="搜索完成"
        )

    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/multimodal", response_model=MultimodalResponse, summary="多模态搜索")
async def multimodal_search(
    input_type: InputType = Form(...),
    file: UploadFile = File(...),
    search_type: SearchType = Form(SearchType.HYBRID),
    limit: int = Form(20),
    threshold: float = Form(0.7),
    db: Session = Depends(get_db)
):
    """
    多模态文件搜索

    支持语音输入和图片输入进行搜索

    - **input_type**: 输入类型 (voice/image)
    - **file**: 上传的文件 (语音或图片)
    - **search_type**: 搜索类型 (semantic/fulltext/hybrid)
    - **limit**: 返回结果数量
    - **threshold**: 相似度阈值
    """
    start_time = time.time()
    logger.info(f"收到多模态搜索请求: type={input_type}, file={file.filename}")

    try:
        # 验证文件大小
        max_size = 50 * 1024 * 1024  # 50MB
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置文件指针

        if file_size > max_size:
            raise HTTPException(status_code=400, detail="文件大小超过50MB限制")

        # 读取文件内容
        file_content = await file.read()

        # TODO: 实现实际的多模态处理逻辑
        # 这里暂时返回模拟数据
        converted_text = "这是从语音/图片转换的搜索查询"
        confidence = 0.95

        # 模拟搜索结果
        mock_results = [
            SearchResult(
                file_id=2,
                file_name="匹配的音频文件.mp3",
                file_path="/path/to/matching_audio.mp3",
                file_type="audio",
                relevance_score=0.88,
                preview_text="音频文件内容预览...",
                highlight="音频<em>文件</em>内容预览",
                created_at="2024-01-10T09:20:00Z",
                modified_at="2024-01-10T09:20:00Z",
                file_size=2048000,
                match_type="semantic"
            )
        ]

        # 计算响应时间
        response_time = time.time() - start_time

        # 保存搜索历史
        history_record = SearchHistoryModel(
            search_query=converted_text,
            input_type=input_type.value,
            search_type=search_type.value,
            ai_model_used=f"{input_type.value}_model",
            result_count=len(mock_results),
            response_time=response_time
        )
        db.add(history_record)
        db.commit()

        logger.info(f"多模态搜索完成: 转换文本='{converted_text}', 结果数量={len(mock_results)}")

        return MultimodalResponse(
            data={
                "converted_text": converted_text,
                "confidence": confidence,
                "search_results": [result.dict() for result in mock_results],
                "file_info": {
                    "filename": file.filename,
                    "size": file_size,
                    "content_type": file.content_type
                },
                "search_time": round(response_time, 2)
            },
            message="多模态搜索完成"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"多模态搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"多模态搜索失败: {str(e)}")


@router.get("/history", response_model=SearchHistoryResponse, summary="搜索历史")
async def get_search_history(
    limit: int = 20,
    offset: int = 0,
    search_type: SearchType = None,
    input_type: InputType = None,
    db: Session = Depends(get_db)
):
    """
    获取搜索历史记录

    - **limit**: 返回结果数量 (1-100)
    - **offset**: 偏移量
    - **search_type**: 搜索类型过滤
    - **input_type**: 输入类型过滤
    """
    logger.info(f"获取搜索历史: limit={limit}, offset={offset}")

    try:
        # 构建查询
        query = db.query(SearchHistoryModel)

        # 应用过滤条件
        if search_type:
            query = query.filter(SearchHistoryModel.search_type == search_type.value)
        if input_type:
            query = query.filter(SearchHistoryModel.input_type == input_type.value)

        # 获取总数
        total = query.count()

        # 分页查询
        history_records = query.order_by(
            SearchHistoryModel.created_at.desc()
        ).offset(offset).limit(limit).all()

        # 转换为响应格式
        history_list = [
            SearchHistoryInfo(
                id=record.id,
                search_query=record.search_query,
                input_type=record.input_type,
                search_type=record.search_type,
                ai_model_used=record.ai_model_used,
                result_count=record.result_count,
                response_time=record.response_time,
                created_at=record.created_at
            )
            for record in history_records
        ]

        logger.info(f"返回搜索历史: 数量={len(history_list)}, 总计={total}")

        return SearchHistoryResponse(
            data={
                "history": [item.dict() for item in history_list],
                "total": total,
                "limit": limit,
                "offset": offset
            },
            message="获取搜索历史成功"
        )

    except Exception as e:
        logger.error(f"获取搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取搜索历史失败: {str(e)}")


@router.delete("/history", summary="清除搜索历史")
async def clear_search_history(
    db: Session = Depends(get_db)
):
    """
    清除所有搜索历史记录
    """
    logger.info("清除搜索历史")

    try:
        # 删除所有历史记录
        deleted_count = db.query(SearchHistoryModel).count()
        db.query(SearchHistoryModel).delete()
        db.commit()

        logger.info(f"搜索历史清除完成: 删除数量={deleted_count}")

        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count
            },
            "message": "搜索历史清除成功"
        }

    except Exception as e:
        logger.error(f"清除搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除搜索历史失败: {str(e)}")


@router.get("/suggestions", summary="搜索建议")
async def get_search_suggestions(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    获取搜索建议

    基于历史搜索记录提供搜索建议

    - **query**: 部分搜索词
    - **limit**: 建议数量
    """
    logger.info(f"获取搜索建议: query='{query}', limit={limit}")

    try:
        # TODO: 实现智能搜索建议逻辑
        # 这里暂时返回模拟数据
        suggestions = [
            f"{query}完整建议1",
            f"{query}完整建议2",
            f"{query}相关建议3"
        ]

        return {
            "success": True,
            "data": {
                "suggestions": suggestions[:limit],
                "query": query
            },
            "message": "获取搜索建议成功"
        }

    except Exception as e:
        logger.error(f"获取搜索建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取搜索建议失败: {str(e)}")