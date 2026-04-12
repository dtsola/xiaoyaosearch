# backend/app/api/glossary_terms.py
"""
术语管理API接口
提供术语的增删改查和CSV导入导出功能
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Header, Depends, UploadFile, File

from app.services.glossary_term_service import GlossaryTermService
from app.schemas.glossary import (
    GlossaryTermCreate,
    GlossaryTermUpdate,
    GlossaryTermResponse,
    GlossaryTermListResponse,
    GlossaryImportResponse
)
from app.core.i18n import get_locale_from_header, i18n
from fastapi.responses import Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/glossary/terms", tags=["术语管理"])


def get_service() -> GlossaryTermService:
    """获取术语服务实例"""
    return GlossaryTermService()


def get_locale(accept_language: Optional[str] = Header(None)) -> str:
    """从请求头获取语言设置"""
    return get_locale_from_header(accept_language)


@router.get("/", response_model=GlossaryTermListResponse)
async def get_terms(
    collection_id: int = Query(..., description="术语库ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    获取术语列表（分页）

    Args:
        collection_id: 术语库ID
        page: 页码（从1开始）
        page_size: 每页数量
        is_enabled: 是否启用（None=全部）

    Returns:
        GlossaryTermListResponse: 术语列表响应
    """
    return service.get_terms(collection_id, page, page_size, is_enabled, locale)


@router.get("/{term_id}", response_model=GlossaryTermResponse)
async def get_term(
    term_id: int,
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    根据ID获取术语

    Args:
        term_id: 术语ID

    Returns:
        GlossaryTermResponse: 术语响应
    """
    return service.get_term_by_id(term_id, locale)


@router.post("/", response_model=GlossaryTermResponse)
async def create_term(
    collection_id: int = Query(..., description="术语库ID"),
    data: GlossaryTermCreate = None,
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    创建术语

    Args:
        collection_id: 术语库ID
        data: 创建术语请求

    Returns:
        GlossaryTermResponse: 创建的术语响应
    """
    return service.create_term(collection_id, data, locale)


@router.put("/{term_id}", response_model=GlossaryTermResponse)
async def update_term(
    term_id: int,
    collection_id: int = Query(..., description="术语库ID"),
    data: GlossaryTermUpdate = None,
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    更新术语

    Args:
        term_id: 术语ID
        collection_id: 术语库ID
        data: 更新数据

    Returns:
        GlossaryTermResponse: 更新后的术语响应
    """
    return service.update_term(collection_id, term_id, data, locale)


@router.delete("/{term_id}")
async def delete_term(
    term_id: int,
    collection_id: int = Query(..., description="术语库ID"),
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    删除术语

    Args:
        term_id: 术语ID
        collection_id: 术语库ID

    Returns:
        dict: 删除结果
    """
    service.delete_term(collection_id, term_id, locale)
    return {"success": True, "message": i18n.t('glossary.term.delete_success', locale)}


@router.post("/import", response_model=GlossaryImportResponse)
async def import_terms_from_csv(
    collection_id: int = Query(..., description="术语库ID"),
    file: UploadFile = File(..., description="CSV文件"),
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    从CSV导入术语

    Args:
        collection_id: 术语库ID
        file: CSV文件

    Returns:
        GlossaryImportResponse: 导入结果响应
    """
    # 验证文件类型
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail=i18n.t('glossary.term.csv_format_only', locale)
        )

    # 读取文件内容
    content = await file.read()
    csv_content = content.decode('utf-8')

    return service.import_from_csv(collection_id, csv_content, locale)


@router.get("/export/{collection_id}")
async def export_terms_to_csv(
    collection_id: int,
    locale: str = Depends(get_locale),
    service: GlossaryTermService = Depends(get_service)
):
    """
    导出术语为CSV

    Args:
        collection_id: 术语库ID

    Returns:
        Response: CSV文件响应
    """
    csv_content = service.export_to_csv(collection_id, locale)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=glossary_{collection_id}.csv"
        }
    )
