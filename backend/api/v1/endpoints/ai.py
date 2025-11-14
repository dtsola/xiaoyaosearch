"""
AI服务API端点 - LLM查询理解、语音转文字、图像分析等AI功能。
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from services.llm.query_understanding_service import QueryUnderstandingService
from services.llm.models.llm_response import LLMProvider
from dao.query_intent_dao import QueryIntentDAO
from dao.llm_cache_dao import LLMCacheDAO

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局服务实例（在生产环境中应该通过依赖注入管理）
_query_understanding_service = None
_intent_dao = QueryIntentDAO()
_cache_dao = LLMCacheDAO()


def get_query_understanding_service() -> QueryUnderstandingService:
    """获取查询理解服务实例。"""
    global _query_understanding_service
    if _query_understanding_service is None:
        _query_understanding_service = QueryUnderstandingService(
            provider_type=LLMProvider.MOCK,  # 默认使用mock provider
            enable_caching=True
        )
    return _query_understanding_service


# 请求/响应模型
class QueryAnalysisRequest(BaseModel):
    """查询分析请求。"""
    query: str = Field(..., min_length=1, max_length=1000, description="要分析的查询")
    options: Dict[str, Any] = Field(default_factory=dict, description="分析选项")
    analyze_intent: bool = Field(True, description="是否分析意图")
    extract_keywords: bool = Field(True, description="是否提取关键词")
    parse_time: bool = Field(True, description="是否解析时间")
    expand_query: bool = Field(True, description="是否扩展查询")
    context: Optional[Dict[str, Any]] = Field(None, description="查询上下文")


class QueryAnalysisResponse(BaseModel):
    """查询分析响应。"""
    original_query: str
    processing_time_ms: int
    cached: bool
    success: bool
    error: Optional[str] = None
    language: Optional[str] = None
    language_confidence: Optional[float] = None
    is_mixed_language: bool = False
    components: Dict[str, Any]
    parsed_query: Optional[Dict[str, Any]] = None


class QuerySuggestionRequest(BaseModel):
    """查询建议请求。"""
    query: str = Field(..., min_length=1, max_length=500, description="原始查询")
    max_suggestions: int = Field(5, ge=1, le=20, description="最大建议数量")


class QuerySuggestion(BaseModel):
    """查询建议。"""
    text: str
    type: str = Field(..., pattern="^(completion|correction|expansion|related)$")
    score: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None


class QuerySuggestionResponse(BaseModel):
    """查询建议响应。"""
    query: str
    suggestions: List[QuerySuggestion]


class LLMProviderConfig(BaseModel):
    """LLM提供商配置。"""
    provider: str = Field(..., pattern="^(openai|ollama|mock)$")
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = Field(0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(500, ge=1, le=4000)
    timeout: Optional[int] = Field(30, ge=5, le=300)


class ProviderStatusResponse(BaseModel):
    """提供商状态响应。"""
    provider: str
    model: str
    available: bool
    connection_test: bool
    statistics: Dict[str, Any]


@router.post("/query-analysis", response_model=QueryAnalysisResponse)
async def analyze_query(
    request: QueryAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分析用户查询，提供智能理解服务。

    - 查询意图识别（文档、图片、音频、视频搜索）
    - 关键词提取和时间范围解析
    - 查询扩展和同义词建议
    - 多语言支持和语义理解
    """
    try:
        service = get_query_understanding_service()

        # 转换为内部模型
        from services.llm.models.query_intent import QueryAnalysisRequest as InternalRequest
        internal_request = InternalRequest(
            query=request.query,
            options=request.options,
            analyze_intent=request.analyze_intent,
            extract_keywords=request.extract_keywords,
            parse_time=request.parse_time,
            expand_query=request.expand_query
        )

        # 执行查询分析
        result = await service.understand_query(internal_request)

        # 保存分析结果到数据库（如果成功）
        if result['success'] and 'parsed_query' in result:
            parsed_query = result['parsed_query']
            intent = parsed_query.get('intent', {})

            await _intent_dao.create_intent(
                db=db,
                original_query=result['original_query'],
                intent_type=intent.get('intent_type', 'unknown'),
                confidence=intent.get('confidence', 0.0),
                normalized_query=parsed_query.get('normalized_query'),
                keywords=intent.get('keywords', []),
                entities=intent.get('entities', {}),
                file_types=intent.get('file_types', []),
                language=result.get('language'),
                time_range_start=intent.get('time_range', {}).get('start_date'),
                time_range_end=intent.get('time_range', {}).get('end_date'),
                time_expression=intent.get('time_range', {}).get('relative_expression'),
                semantic_description=intent.get('semantic_description'),
                query_complexity=parsed_query.get('query_complexity', 'simple'),
                llm_provider=service.provider_type.value,
                llm_model=service._provider.config.model if service._provider else None,
                processing_time_ms=result['processing_time_ms'],
                expanded_query=parsed_query.get('expanded_query', [])
            )

        return QueryAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"查询分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询分析失败: {str(e)}")


@router.post("/query-suggestions", response_model=QuerySuggestionResponse)
async def get_query_suggestions(
    request: QuerySuggestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    获取智能查询建议。

    - 基于AI的查询补全
    - 查询纠正和建议
    - 相关查询推荐
    - 历史搜索建议
    """
    try:
        service = get_query_understanding_service()

        # 获取查询建议
        suggestions = await service.get_query_suggestions(
            query=request.query,
            max_suggestions=request.max_suggestions
        )

        # 转换为响应模型
        suggestion_objects = []
        for suggestion in suggestions:
            suggestion_objects.append(QuerySuggestion(**suggestion))

        return QuerySuggestionResponse(
            query=request.query,
            suggestions=suggestion_objects
        )

    except Exception as e:
        logger.error(f"获取查询建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取查询建议失败: {str(e)}")


@router.get("/provider/status", response_model=ProviderStatusResponse)
async def get_provider_status():
    """
    获取LLM提供商状态和统计信息。
    """
    try:
        service = get_query_understanding_service()

        # 测试连接
        connection_test = await service.test_provider_connection()

        # 获取统计信息
        statistics = service.get_service_statistics()

        return ProviderStatusResponse(
            provider=service.provider_type.value,
            model=service._provider.config.model if service._provider else "unknown",
            available=service._provider is not None,
            connection_test=connection_test,
            statistics=statistics
        )

    except Exception as e:
        logger.error(f"获取提供商状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提供商状态失败: {str(e)}")


@router.post("/provider/configure")
async def configure_provider(
    config: LLMProviderConfig,
    background_tasks: BackgroundTasks
):
    """
    配置LLM提供商。

    - 支持OpenAI、Ollama、Mock提供商
    - 动态切换提供商和模型
    - 配置参数验证
    """
    try:
        global _query_understanding_service

        # 构建提供商配置
        provider_config = {}
        if config.api_key:
            provider_config['api_key'] = config.api_key
        if config.base_url:
            provider_config['base_url'] = config.base_url
        if config.model:
            provider_config['model'] = config.model
        if config.temperature is not None:
            provider_config['temperature'] = config.temperature
        if config.max_tokens is not None:
            provider_config['max_tokens'] = config.max_tokens
        if config.timeout is not None:
            provider_config['timeout'] = config.timeout

        # 创建新的服务实例
        new_service = QueryUnderstandingService(
            provider_type=LLMProvider(config.provider),
            provider_config=provider_config,
            enable_caching=True
        )

        # 测试新提供商连接
        if not await new_service.test_provider_connection():
            raise HTTPException(
                status_code=400,
                detail=f"无法连接到 {config.provider} 提供商"
            )

        # 在后台任务中关闭旧服务并切换到新服务
        async def switch_service():
            global _query_understanding_service
            if _query_understanding_service:
                await _query_understanding_service.close()
            _query_understanding_service = new_service

        background_tasks.add_task(switch_service)

        return {
            "message": f"已成功配置 {config.provider} 提供商",
            "provider": config.provider,
            "model": config.model or "default"
        }

    except Exception as e:
        logger.error(f"配置提供商失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"配置提供商失败: {str(e)}")


@router.get("/cache/statistics")
async def get_cache_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取LLM缓存统计信息。

    - 缓存命中率统计
    - 成本节省分析
    - 提供商使用统计
    - 性能指标
    """
    try:
        stats = await _cache_dao.get_cache_statistics(db, days)
        return stats

    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.post("/cache/cleanup")
async def cleanup_cache(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    清理过期的LLM缓存条目。

    - 异步清理任务
    - 批量处理优化
    - 清理统计报告
    """
    try:
        async def cleanup_task():
            deleted_count = 0
            total_deleted = 0

            # 分批清理以避免长时间锁定
            while True:
                batch_deleted = await _cache_dao.cleanup_expired_cache(db, batch_size=100)
                total_deleted += batch_deleted

                if batch_deleted == 0:
                    break

                await db.commit()

            logger.info(f"缓存清理完成，删除了 {total_deleted} 个过期条目")
            return total_deleted

        # 在后台执行清理
        background_tasks.add_task(cleanup_task)

        return {
            "message": "缓存清理任务已启动",
            "status": "in_progress"
        }

    except Exception as e:
        logger.error(f"启动缓存清理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动缓存清理失败: {str(e)}")


@router.get("/intents/statistics")
async def get_intent_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取查询意图统计信息。

    - 意图类型分布
    - 语言使用统计
    - 处理性能指标
    - 热门关键词分析
    """
    try:
        stats = await _intent_dao.get_intent_statistics(db, days)
        return stats

    except Exception as e:
        logger.error(f"获取意图统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取意图统计失败: {str(e)}")


@router.get("/intents/popular-keywords")
async def get_popular_keywords(
    limit: int = Query(20, ge=1, le=100, description="关键词数量"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热门关键词统计。

    - 基于历史查询分析
    - 关键词频率统计
    - 时间趋势分析
    """
    try:
        keywords = await _intent_dao.get_popular_keywords(db, limit, days)
        return {
            "period_days": days,
            "keywords": keywords
        }

    except Exception as e:
        logger.error(f"获取热门关键词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门关键词失败: {str(e)}")


@router.post("/test/connection")
async def test_ai_service_connection():
    """
    测试AI服务连接。

    - LLM提供商连接测试
    - 响应时间测量
    - 模型可用性检查
    """
    try:
        service = get_query_understanding_service()

        # 测试基本连接
        connection_ok = await service.test_provider_connection()

        # 测试简单查询
        test_start = time.time()
        try:
            from services.llm.models.query_intent import QueryAnalysisRequest as InternalRequest
            test_request = InternalRequest(
                query="测试",
                options={},
                analyze_intent=True,
                extract_keywords=False,
                parse_time=False,
                expand_query=False
            )

            test_result = await service.understand_query(test_request)
            response_time = int((time.time() - test_start) * 1000)

            test_success = test_result['success']

        except Exception as e:
            test_success = False
            response_time = 0
            logger.error(f"测试查询失败: {str(e)}")

        return {
            "provider": service.provider_type.value,
            "connection_test": connection_ok,
            "query_test": test_success,
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"连接测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")