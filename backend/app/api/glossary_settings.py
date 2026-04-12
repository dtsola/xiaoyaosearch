# backend/app/api/glossary_settings.py
"""
术语扩展设置API接口
提供术语扩展功能的配置管理
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chunk_search_service import configure_glossary_expansion
from app.services.glossary_collection_service import GlossaryCollectionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/glossary/settings", tags=["术语扩展设置"])


class GlossaryExpansionConfig(BaseModel):
    """术语扩展配置"""
    enable: bool = Field(..., description="是否启用术语扩展")
    collection_ids: Optional[List[int]] = Field(None, description="使用的术语库ID列表，null表示全部")


class GlossaryExpansionConfigResponse(BaseModel):
    """术语扩展配置响应"""
    enable: bool
    collection_ids: Optional[List[int]]
    available_collections: List[dict]


@router.get("/", response_model=GlossaryExpansionConfigResponse)
async def get_glossary_expansion_config():
    """
    获取术语扩展配置

    Returns:
        GlossaryExpansionConfigResponse: 当前配置
    """
    try:
        service = GlossaryCollectionService()
        collections = service.get_enabled_collections()

        return GlossaryExpansionConfigResponse(
            enable=False,  # 默认禁用
            collection_ids=None,
            available_collections=[
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "icon": c.icon,
                    "color": c.color,
                    "term_count": c.term_count
                }
                for c in collections
            ]
        )
    except Exception as e:
        logger.error(f"获取术语扩展配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/")
async def update_glossary_expansion_config(config: GlossaryExpansionConfig):
    """
    更新术语扩展配置

    Args:
        config: 新配置

    Returns:
        dict: 更新结果
    """
    try:
        configure_glossary_expansion(
            enable=config.enable,
            collection_ids=config.collection_ids
        )

        logger.info(f"术语扩展配置已更新: enable={config.enable}, collection_ids={config.collection_ids}")

        return {
            "success": True,
            "message": "术语扩展配置已更新",
            "config": {
                "enable": config.enable,
                "collection_ids": config.collection_ids
            }
        }
    except Exception as e:
        logger.error(f"更新术语扩展配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")
