"""
搜索服务API路由
提供文件搜索相关的API接口，集成AI模型功能
"""
import time
from typing import List, Optional
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
from app.utils.enum_helpers import get_enum_value, is_semantic_search, is_hybrid_search, is_text_input, is_voice_input, is_image_input
# AI模型服务导入状态
AI_MODEL_SERVICE_AVAILABLE = False
ai_model_service = None
from app.services.search_service import get_search_service

router = APIRouter(prefix="/api/search", tags=["搜索服务"])
logger = get_logger(__name__)

# 在logger定义后导入AI模型服务
try:
    from app.services.ai_model_manager import ai_model_service
    AI_MODEL_SERVICE_AVAILABLE = True
    logger.info("AI模型服务导入成功")
except ImportError as e:
    AI_MODEL_SERVICE_AVAILABLE = False
    ai_model_service = None
    logger.warning(f"AI模型服务不可用: {e}")


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
    # 使用枚举辅助函数确保类型安全
    search_type_str = get_enum_value(request.search_type)
    logger.info(f"收到搜索请求: query='{request.query}', type={search_type_str}")

    try:
        # 获取搜索服务
        search_service = get_search_service()

        # 检查搜索服务是否就绪
        if not search_service.is_ready():
            logger.warning("搜索服务未就绪，返回空结果")
            return SearchResponse(
                data={
                    "results": [],
                    "total": 0,
                    "search_time": 0,
                    "query_used": request.query,
                    "input_processed": not is_text_input(request.input_type),
                    "ai_models_used": [],
                    "error": "搜索服务未就绪，请先构建索引"
                },
                message="搜索服务未就绪"
            )

        # 执行真正的搜索
        search_result = await search_service.search(
            query=request.query,
            search_type=search_type_str,  # 使用转换后的字符串
            limit=request.limit,
            offset=0,
            threshold=request.threshold,
            filters=request.file_types
        )

        # 转换搜索结果为SearchResult格式
        results = []
        for item in search_result.get('results', []):
            search_result_item = SearchResult(
                file_id=item.get('id', 0),
                file_name=item.get('file_name', ''),
                file_path=item.get('file_path', ''),
                file_type=item.get('file_type', ''),
                relevance_score=item.get('relevance_score', 0.0),
                preview_text=item.get('preview_text', ''),
                highlight=item.get('highlight', ''),
                created_at=item.get('modified_time', ''),
                modified_at=item.get('modified_time', ''),
                file_size=item.get('file_size', 0),
                match_type=item.get('match_type', '')
            )
            results.append(search_result_item)

        # 计算响应时间和使用的AI模型
        response_time = search_result.get('search_time', 0)
        ai_models_used = []

        # 根据搜索类型记录使用的AI模型
        if is_semantic_search(request.search_type) or is_hybrid_search(request.search_type):
            ai_models_used.append("BGE-M3")

        # 如果是混合搜索，还有全文搜索
        if is_hybrid_search(search_type_str):  # 使用转换后的字符串
            ai_models_used.append("Whoosh")

        # 保存搜索历史
        input_type_str = get_enum_value(request.input_type)
        history_record = SearchHistoryModel(
            search_query=request.query,
            input_type=input_type_str,
            search_type=search_type_str,
            ai_model_used=",".join(ai_models_used) if ai_models_used else "none",
            result_count=len(results),
            response_time=response_time
        )
        db.add(history_record)
        db.commit()

        logger.info(f"搜索完成: 结果数量={len(results)}, 耗时={response_time:.2f}秒")

        return SearchResponse(
            data={
                "results": [result.dict() for result in results],
                "total": search_result.get('total', 0),
                "search_time": round(response_time, 2),
                "query_used": request.query,
                "input_processed": not is_text_input(request.input_type),
                "ai_models_used": ai_models_used
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
    # 使用枚举辅助函数确保类型安全
    input_type_str = get_enum_value(input_type)
    search_type_str = get_enum_value(search_type)
    logger.info(f"收到多模态搜索请求: type={input_type_str}, file={file.filename}")

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

        # 使用AI模型服务处理多模态输入
        converted_text = ""
        confidence = 0.0
        ai_models_used = []

        if is_voice_input(input_type):
            # 语音转文字
            if not AI_MODEL_SERVICE_AVAILABLE:
                raise HTTPException(status_code=503, detail="AI模型服务不可用，无法处理语音输入")

            logger.info("使用FasterWhisper进行语音识别")
            transcription_result = await ai_model_service.speech_to_text(
                file_content,
                language="zh"
            )
            converted_text = transcription_result.get("text", "")
            confidence = transcription_result.get("avg_confidence", 0.0)
            ai_models_used.append("FasterWhisper")

        elif is_image_input(input_type):
            # 图像理解生成搜索查询
            if not AI_MODEL_SERVICE_AVAILABLE:
                raise HTTPException(status_code=503, detail="AI模型服务不可用，无法处理图像输入")

            logger.info("使用CN-CLIP进行图像理解")
            texts = [
                "描述这张图片的内容",
                "这张图片展示了什么",
                "图片中的主要元素",
                "图片的整体主题"
            ]
            vision_result = await ai_model_service.image_understanding(
                file_content,
                texts
            )
            converted_text = vision_result.get("best_match", {}).get("text", "")
            confidence = vision_result.get("best_match", {}).get("similarity", 0.0)
            ai_models_used.append("CN-CLIP")

        # 如果成功转换，进行搜索
        if converted_text:
            # 获取搜索查询的嵌入向量
            if (is_semantic_search(search_type) or is_hybrid_search(search_type)) and AI_MODEL_SERVICE_AVAILABLE:
                await ai_model_service.text_embedding(converted_text, normalize_embeddings=True)
                ai_models_used.append("BGE-M3")

        # 模拟搜索结果
        mock_results = [
            SearchResult(
                file_id=2,
                file_name="匹配的文件.pdf",
                file_path="/path/to/matching_file.pdf",
                file_type="document",
                relevance_score=0.88,
                preview_text="匹配文件的内容预览...",
                highlight="匹配<em>文件</em>的内容预览",
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
            search_query=converted_text or "转换失败",
            input_type=input_type_str,
            search_type=search_type_str,
            ai_model_used=",".join(ai_models_used) if ai_models_used else "none",
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
                "search_time": round(response_time, 2),
                "ai_models_used": ai_models_used
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
            search_type_str = get_enum_value(search_type)
            query = query.filter(SearchHistoryModel.search_type == search_type_str)
        if input_type:
            input_type_str = get_enum_value(input_type)
            query = query.filter(SearchHistoryModel.input_type == input_type_str)

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