# backend/app/api/glossary.py
"""
术语扩展API接口
提供查询词的术语扩展功能
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from app.services.glossary_service import GlossaryService
from app.schemas.glossary import (
    GlossaryExpandRequest,
    GlossaryExpandResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/glossary", tags=["术语扩展"])


def get_service() -> GlossaryService:
    """获取术语服务实例"""
    return GlossaryService()


@router.post("/expand", response_model=GlossaryExpandResponse)
async def expand_query(
    request: GlossaryExpandRequest,
    service: GlossaryService = Depends(get_service)
):
    """
    扩展查询词

    根据查询词匹配术语库中的术语，返回扩展后的查询词列表。

    Args:
        request: 查询扩展请求

    Returns:
        GlossaryExpandResponse: 查询扩展响应
    """
    return service.expand_query(request.query, request.collection_ids)
