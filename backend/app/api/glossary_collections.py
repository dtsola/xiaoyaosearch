# backend/app/api/glossary_collections.py
"""
术语库管理API接口
提供术语库的增删改查功能
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Header, Depends

from app.services.glossary_collection_service import GlossaryCollectionService
from app.schemas.glossary import (
    GlossaryCollectionCreate,
    GlossaryCollectionUpdate,
    GlossaryCollectionResponse,
    GlossaryCollectionListResponse
)
from app.core.i18n import get_locale_from_header, i18n

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/glossary/collections", tags=["术语库管理"])


def get_service() -> GlossaryCollectionService:
    """获取术语库服务实例"""
    return GlossaryCollectionService()


def get_locale(accept_language: Optional[str] = Header(None)) -> str:
    """从请求头获取语言设置"""
    return get_locale_from_header(accept_language)


@router.get("/", response_model=GlossaryCollectionListResponse)
async def get_collections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    获取术语库列表（分页）

    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        is_enabled: 是否启用（None=全部）

    Returns:
        GlossaryCollectionListResponse: 术语库列表响应
    """
    return service.get_collections(page, page_size, is_enabled, locale)


@router.get("/{collection_id}", response_model=GlossaryCollectionResponse)
async def get_collection(
    collection_id: int,
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    根据ID获取术语库

    Args:
        collection_id: 术语库ID

    Returns:
        GlossaryCollectionResponse: 术语库响应
    """
    return service.get_collection_by_id(collection_id, locale)


@router.post("/", response_model=GlossaryCollectionResponse)
async def create_collection(
    data: GlossaryCollectionCreate,
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    创建术语库

    Args:
        data: 创建术语库请求

    Returns:
        GlossaryCollectionResponse: 创建的术语库响应
    """
    return service.create_collection(data, locale)


@router.put("/{collection_id}", response_model=GlossaryCollectionResponse)
async def update_collection(
    collection_id: int,
    data: GlossaryCollectionUpdate,
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    更新术语库

    Args:
        collection_id: 术语库ID
        data: 更新数据

    Returns:
        GlossaryCollectionResponse: 更新后的术语库响应
    """
    return service.update_collection(collection_id, data, locale)


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: int,
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    删除术语库

    Args:
        collection_id: 术语库ID

    Returns:
        dict: 删除结果
    """
    service.delete_collection(collection_id, locale)
    return {"success": True, "message": i18n.t('glossary.collection.delete_success', locale)}


@router.get("/enabled/list", response_model=list[GlossaryCollectionResponse])
async def get_enabled_collections(
    locale: str = Depends(get_locale),
    service: GlossaryCollectionService = Depends(get_service)
):
    """
    获取所有启用的术语库

    Returns:
        List[GlossaryCollectionResponse]: 启用的术语库列表
    """
    return service.get_enabled_collections(locale)
