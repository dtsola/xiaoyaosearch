# backend/app/services/glossary_collection_service.py
"""
术语库集合服务
提供术语库的CRUD操作
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.database import SessionLocal
from app.core.i18n import i18n
from app.models.glossary_collection import GlossaryCollectionModel
from app.models.glossary_term import GlossaryTermModel
from app.schemas.glossary import (
    GlossaryCollectionCreate,
    GlossaryCollectionUpdate,
    GlossaryCollectionResponse,
    GlossaryCollectionListResponse
)

logger = logging.getLogger(__name__)


class GlossaryCollectionService:
    """术语库集合服务类"""

    def __init__(self):
        self._db: Optional[Session] = None

    def _get_db(self) -> Session:
        """获取数据库会话"""
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def _close_db(self):
        """关闭数据库会话"""
        if self._db is not None:
            self._db.close()
            self._db = None

    def get_collections(
        self,
        page: int = 1,
        page_size: int = 20,
        is_enabled: Optional[bool] = None,
        locale: str = "zh_CN"
    ) -> GlossaryCollectionListResponse:
        """
        获取术语库列表（分页）

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            is_enabled: 是否启用（None=全部）
            locale: 语言代码

        Returns:
            GlossaryCollectionListResponse: 术语库列表响应
        """
        try:
            db = self._get_db()
            query = db.query(GlossaryCollectionModel)

            if is_enabled is not None:
                query = query.filter(GlossaryCollectionModel.is_enabled == is_enabled)

            total = query.count()
            items = query.order_by(GlossaryCollectionModel.id.desc()).offset(
                (page - 1) * page_size
            ).limit(page_size).all()

            return GlossaryCollectionListResponse(
                items=[GlossaryCollectionResponse.model_validate(item) for item in items],
                total=total,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            logger.error(f"获取术语库列表失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.get_list_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()

    def get_collection_by_id(self, collection_id: int, locale: str = "zh_CN") -> GlossaryCollectionResponse:
        """
        根据ID获取术语库

        Args:
            collection_id: 术语库ID
            locale: 语言代码

        Returns:
            GlossaryCollectionResponse: 术语库响应

        Raises:
            HTTPException: 术语库不存在
        """
        try:
            db = self._get_db()
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(
                    status_code=404,
                    detail=i18n.t('glossary.collection.not_found', locale).format(id=collection_id)
                )

            return GlossaryCollectionResponse.model_validate(collection)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取术语库失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.get_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()

    def create_collection(self, data: GlossaryCollectionCreate, locale: str = "zh_CN") -> GlossaryCollectionResponse:
        """
        创建术语库

        Args:
            data: 创建术语库请求
            locale: 语言代码

        Returns:
            GlossaryCollectionResponse: 创建的术语库响应

        Raises:
            HTTPException: 名称已存在
        """
        try:
            db = self._get_db()

            # 检查名称是否已存在
            existing = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.name == data.name
            ).first()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=i18n.t('glossary.collection.name_exists', locale).format(name=data.name)
                )

            collection = GlossaryCollectionModel(
                name=data.name,
                description=data.description,
                icon=data.icon,
                color=data.color,
                is_enabled=True,
                term_count=0,
                is_system=False
            )

            db.add(collection)
            db.commit()
            db.refresh(collection)

            logger.info(f"创建术语库成功: {collection.name} (ID: {collection.id})")
            return GlossaryCollectionResponse.model_validate(collection)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建术语库失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.create_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()

    def update_collection(
        self,
        collection_id: int,
        data: GlossaryCollectionUpdate,
        locale: str = "zh_CN"
    ) -> GlossaryCollectionResponse:
        """
        更新术语库

        Args:
            collection_id: 术语库ID
            data: 更新数据
            locale: 语言代码

        Returns:
            GlossaryCollectionResponse: 更新后的术语库响应

        Raises:
            HTTPException: 术语库不存在或名称冲突
        """
        try:
            db = self._get_db()
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(
                    status_code=404,
                    detail=i18n.t('glossary.collection.not_found', locale).format(id=collection_id)
                )

            # 如果修改名称，检查新名称是否冲突
            if data.name and data.name != collection.name:
                existing = db.query(GlossaryCollectionModel).filter(
                    GlossaryCollectionModel.name == data.name,
                    GlossaryCollectionModel.id != collection_id
                ).first()

                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail=i18n.t('glossary.collection.name_exists', locale).format(name=data.name)
                    )

            # 更新字段
            if data.name is not None:
                collection.name = data.name
            if data.description is not None:
                collection.description = data.description
            if data.icon is not None:
                collection.icon = data.icon
            if data.color is not None:
                collection.color = data.color
            if data.is_enabled is not None:
                collection.is_enabled = data.is_enabled

            db.commit()
            db.refresh(collection)

            logger.info(f"更新术语库成功: {collection.name} (ID: {collection.id})")
            return GlossaryCollectionResponse.model_validate(collection)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新术语库失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.update_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()

    def delete_collection(self, collection_id: int, locale: str = "zh_CN") -> bool:
        """
        删除术语库

        Args:
            collection_id: 术语库ID
            locale: 语言代码

        Returns:
            bool: 是否删除成功

        Raises:
            HTTPException: 术语库不存在或为系统预置
        """
        try:
            db = self._get_db()
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(
                    status_code=404,
                    detail=i18n.t('glossary.collection.not_found', locale).format(id=collection_id)
                )

            if collection.is_system:
                raise HTTPException(
                    status_code=400,
                    detail=i18n.t('glossary.collection.system_cannot_delete', locale)
                )

            # 手动删除关联术语（外键被禁用）
            db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id
            ).delete()

            db.delete(collection)
            db.commit()

            logger.info(f"删除术语库成功: {collection.name} (ID: {collection_id})")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除术语库失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.delete_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()

    def get_enabled_collections(self, locale: str = "zh_CN") -> List[GlossaryCollectionResponse]:
        """
        获取所有启用的术语库

        Args:
            locale: 语言代码

        Returns:
            List[GlossaryCollectionResponse]: 启用的术语库列表
        """
        try:
            db = self._get_db()
            collections = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.is_enabled == True
            ).order_by(GlossaryCollectionModel.id.asc()).all()

            return [GlossaryCollectionResponse.model_validate(c) for c in collections]
        except Exception as e:
            logger.error(f"获取启用术语库失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=i18n.t('glossary.collection.get_enabled_failed', locale).format(error=str(e))
            )
        finally:
            self._close_db()
