# backend/app/api/glossary_settings.py
"""
术语扩展设置API接口
提供术语扩展功能的配置管理
"""
import logging
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.chunk_search_service import configure_glossary_expansion
from app.services.glossary_collection_service import GlossaryCollectionService
from app.core.i18n import get_locale_from_header, i18n
from app.core.database import SessionLocal
from app.models.app_settings import AppSettingsModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/glossary/settings", tags=["术语扩展设置"])

# 术语扩展配置的数据库键
GLOSSARY_EXPANSION_CONFIG_KEY = "glossary_expansion_config"


def get_glossary_expansion_config_from_db(db: Session) -> dict:
    """
    从数据库读取术语扩展配置

    Args:
        db: 数据库会话

    Returns:
        dict: 配置字典，包含 enable 和 collection_ids
    """
    try:
        setting = db.query(AppSettingsModel).filter(
            AppSettingsModel.setting_key == GLOSSARY_EXPANSION_CONFIG_KEY
        ).first()

        if setting and setting.setting_value:
            return json.loads(setting.setting_value)
        else:
            # 默认配置
            return {
                "enable": False,
                "collection_ids": None
            }
    except Exception as e:
        logger.error(f"读取术语扩展配置失败: {str(e)}")
        return {
            "enable": False,
            "collection_ids": None
        }


def save_glossary_expansion_config_to_db(db: Session, config: dict) -> None:
    """
    保存术语扩展配置到数据库

    Args:
        db: 数据库会话
        config: 配置字典，包含 enable 和 collection_ids
    """
    try:
        setting = db.query(AppSettingsModel).filter(
            AppSettingsModel.setting_key == GLOSSARY_EXPANSION_CONFIG_KEY
        ).first()

        config_json = json.dumps(config, ensure_ascii=False)

        if setting:
            setting.setting_value = config_json
        else:
            new_setting = AppSettingsModel(
                setting_key=GLOSSARY_EXPANSION_CONFIG_KEY,
                setting_value=config_json,
                setting_type="json",
                description="术语扩展配置：enable表示是否启用，collection_ids表示使用的术语库ID列表"
            )
            db.add(new_setting)

        db.commit()
        logger.info(f"术语扩展配置已保存到数据库: {config}")
    except Exception as e:
        logger.error(f"保存术语扩展配置失败: {str(e)}")
        db.rollback()
        raise


class GlossaryExpansionConfig(BaseModel):
    """术语扩展配置"""
    enable: bool = Field(..., description="是否启用术语扩展")
    collection_ids: Optional[List[int]] = Field(None, description="使用的术语库ID列表，null表示全部")


class GlossaryExpansionConfigData(BaseModel):
    """术语扩展配置数据"""
    enable: bool
    collection_ids: Optional[List[int]]
    available_collections: List[dict]


class GlossaryExpansionConfigResponse(BaseModel):
    """术语扩展配置响应"""
    success: bool = True
    data: GlossaryExpansionConfigData


def get_locale(accept_language: Optional[str] = Header(None)) -> str:
    """从请求头获取语言设置"""
    return get_locale_from_header(accept_language)


@router.get("/", response_model=GlossaryExpansionConfigResponse)
async def get_glossary_expansion_config(
    locale: str = Depends(get_locale)
):
    """
    获取术语扩展配置

    Returns:
        GlossaryExpansionConfigResponse: 当前配置
    """
    try:
        db = SessionLocal()
        try:
            # 从数据库读取配置
            config_dict = get_glossary_expansion_config_from_db(db)

            # 获取可用的术语库列表
            service = GlossaryCollectionService()
            collections = service.get_enabled_collections(locale)

            data = GlossaryExpansionConfigData(
                enable=config_dict.get("enable", False),
                collection_ids=config_dict.get("collection_ids"),
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
            return GlossaryExpansionConfigResponse(success=True, data=data)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取术语扩展配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=i18n.t('glossary.settings.get_config_failed', locale).format(error=str(e))
        )


@router.post("/")
async def update_glossary_expansion_config(
    config: GlossaryExpansionConfig,
    locale: str = Depends(get_locale)
):
    """
    更新术语扩展配置

    Args:
        config: 新配置

    Returns:
        dict: 更新结果
    """
    try:
        db = SessionLocal()
        try:
            # 保存配置到数据库
            config_dict = {
                "enable": config.enable,
                "collection_ids": config.collection_ids
            }
            save_glossary_expansion_config_to_db(db, config_dict)

            # 更新搜索服务的配置
            configure_glossary_expansion(
                enable=config.enable,
                collection_ids=config.collection_ids
            )

            logger.info(f"术语扩展配置已更新: enable={config.enable}, collection_ids={config.collection_ids}")

            return {
                "success": True,
                "message": i18n.t('glossary.settings.update_success', locale),
                "data": {
                    "enable": config.enable,
                    "collection_ids": config.collection_ids
                }
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"更新术语扩展配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=i18n.t('glossary.settings.update_config_failed', locale).format(error=str(e))
        )
