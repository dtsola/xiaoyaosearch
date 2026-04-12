# backend/app/services/glossary_term_service.py
"""
术语服务
提供术语的CRUD操作和CSV导入导出功能
"""
import csv
import io
import json
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.database import SessionLocal
from app.models.glossary_term import GlossaryTermModel
from app.models.glossary_collection import GlossaryCollectionModel
from app.schemas.glossary import (
    GlossaryTermCreate,
    GlossaryTermUpdate,
    GlossaryTermResponse,
    GlossaryTermListResponse,
    GlossaryImportResponse
)

logger = logging.getLogger(__name__)


class GlossaryTermService:
    """术语服务类"""

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

    def get_terms(
        self,
        collection_id: int,
        page: int = 1,
        page_size: int = 20,
        is_enabled: Optional[bool] = None
    ) -> GlossaryTermListResponse:
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
        try:
            db = self._get_db()

            # 获取术语库信息
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(status_code=404, detail=f"术语库 ID={collection_id} 不存在")

            # 查询术语
            query = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id
            )

            if is_enabled is not None:
                query = query.filter(GlossaryTermModel.is_enabled == is_enabled)

            total = query.count()
            items = query.order_by(GlossaryTermModel.term.asc()).offset(
                (page - 1) * page_size
            ).limit(page_size).all()

            return GlossaryTermListResponse(
                collection_id=collection_id,
                collection_name=collection.name,
                items=[GlossaryTermResponse.model_validate(item) for item in items],
                total=total,
                page=page,
                page_size=page_size
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取术语列表失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取术语列表失败: {str(e)}")
        finally:
            self._close_db()

    def get_term_by_id(self, term_id: int) -> GlossaryTermResponse:
        """
        根据ID获取术语

        Args:
            term_id: 术语ID

        Returns:
            GlossaryTermResponse: 术语响应

        Raises:
            HTTPException: 术语不存在
        """
        try:
            db = self._get_db()
            term = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.id == term_id
            ).first()

            if not term:
                raise HTTPException(status_code=404, detail=f"术语 ID={term_id} 不存在")

            return GlossaryTermResponse.model_validate(term)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取术语失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取术语失败: {str(e)}")
        finally:
            self._close_db()

    def create_term(
        self,
        collection_id: int,
        data: GlossaryTermCreate
    ) -> GlossaryTermResponse:
        """
        创建术语

        Args:
            collection_id: 术语库ID
            data: 创建术语请求

        Returns:
            GlossaryTermResponse: 创建的术语响应

        Raises:
            HTTPException: 术语库不存在或术语已存在
        """
        try:
            db = self._get_db()

            # 检查术语库是否存在
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(status_code=404, detail=f"术语库 ID={collection_id} 不存在")

            # 检查术语是否已存在
            existing = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id,
                GlossaryTermModel.term == data.term
            ).first()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"术语 '{data.term}' 在术语库 '{collection.name}' 中已存在"
                )

            term = GlossaryTermModel(
                collection_id=collection_id,
                term=data.term,
                synonyms=json.dumps(data.synonyms, ensure_ascii=False),
                description=data.description,
                examples=json.dumps(data.examples or [], ensure_ascii=False),
                is_enabled=True
            )

            db.add(term)
            db.commit()
            db.refresh(term)

            # 更新术语库的术语计数
            collection.term_count = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id,
                GlossaryTermModel.is_enabled == True
            ).count()
            db.commit()

            logger.info(f"创建术语成功: {term.term} (ID: {term.id})")
            return GlossaryTermResponse.model_validate(term)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建术语失败: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"创建术语失败: {str(e)}")
        finally:
            self._close_db()

    def update_term(
        self,
        collection_id: int,
        term_id: int,
        data: GlossaryTermUpdate
    ) -> GlossaryTermResponse:
        """
        更新术语

        Args:
            collection_id: 术语库ID
            term_id: 术语ID
            data: 更新数据

        Returns:
            GlossaryTermResponse: 更新后的术语响应

        Raises:
            HTTPException: 术语不存在或术语名称冲突
        """
        try:
            db = self._get_db()
            term = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.id == term_id,
                GlossaryTermModel.collection_id == collection_id
            ).first()

            if not term:
                raise HTTPException(status_code=404, detail=f"术语 ID={term_id} 不存在")

            # 如果修改术语名称，检查新名称是否冲突
            if data.term and data.term != term.term:
                existing = db.query(GlossaryTermModel).filter(
                    GlossaryTermModel.collection_id == collection_id,
                    GlossaryTermModel.term == data.term,
                    GlossaryTermModel.id != term_id
                ).first()

                if existing:
                    raise HTTPException(status_code=400, detail=f"术语 '{data.term}' 已存在")

            # 更新字段
            if data.term is not None:
                term.term = data.term
            if data.synonyms is not None:
                term.synonyms = json.dumps(data.synonyms, ensure_ascii=False)
            if data.description is not None:
                term.description = data.description
            if data.examples is not None:
                term.examples = json.dumps(data.examples, ensure_ascii=False)
            if data.is_enabled is not None:
                term.is_enabled = data.is_enabled

            db.commit()
            db.refresh(term)

            # 更新术语库的术语计数
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()
            if collection:
                collection.term_count = db.query(GlossaryTermModel).filter(
                    GlossaryTermModel.collection_id == collection_id,
                    GlossaryTermModel.is_enabled == True
                ).count()
                db.commit()

            logger.info(f"更新术语成功: {term.term} (ID: {term.id})")
            return GlossaryTermResponse.model_validate(term)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新术语失败: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"更新术语失败: {str(e)}")
        finally:
            self._close_db()

    def delete_term(self, collection_id: int, term_id: int) -> bool:
        """
        删除术语

        Args:
            collection_id: 术语库ID
            term_id: 术语ID

        Returns:
            bool: 是否删除成功

        Raises:
            HTTPException: 术语不存在
        """
        try:
            db = self._get_db()
            term = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.id == term_id,
                GlossaryTermModel.collection_id == collection_id
            ).first()

            if not term:
                raise HTTPException(status_code=404, detail=f"术语 ID={term_id} 不存在")

            db.delete(term)
            db.commit()

            # 更新术语库的术语计数
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()
            if collection:
                collection.term_count = db.query(GlossaryTermModel).filter(
                    GlossaryTermModel.collection_id == collection_id,
                    GlossaryTermModel.is_enabled == True
                ).count()
                db.commit()

            logger.info(f"删除术语成功: {term.term} (ID: {term_id})")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除术语失败: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"删除术语失败: {str(e)}")
        finally:
            self._close_db()

    def import_from_csv(
        self,
        collection_id: int,
        csv_content: str
    ) -> GlossaryImportResponse:
        """
        从CSV导入术语

        Args:
            collection_id: 术语库ID
            csv_content: CSV文件内容

        Returns:
            GlossaryImportResponse: 导入结果响应
        """
        try:
            db = self._get_db()

            # 检查术语库是否存在
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(status_code=404, detail=f"术语库 ID={collection_id} 不存在")

            # 解析CSV
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.DictReader(csv_file)

            imported_count = 0
            failed_count = 0
            errors = []

            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    term_name = row.get("术语名称", "").strip()
                    if not term_name:
                        raise ValueError("术语名称不能为空")

                    synonyms_str = row.get("同义词", "")
                    synonyms = [s.strip() for s in synonyms_str.split(";") if s.strip()]
                    if not synonyms:
                        raise ValueError("同义词不能为空")

                    # 检查术语是否已存在
                    existing = db.query(GlossaryTermModel).filter(
                        GlossaryTermModel.collection_id == collection_id,
                        GlossaryTermModel.term == term_name
                    ).first()

                    if existing:
                        errors.append({
                            "row": row_num,
                            "term": term_name,
                            "error": "术语已存在"
                        })
                        failed_count += 1
                        continue

                    # 创建术语
                    term = GlossaryTermModel(
                        collection_id=collection_id,
                        term=term_name,
                        synonyms=json.dumps(synonyms, ensure_ascii=False),
                        description=row.get("描述", "").strip()
                    )
                    db.add(term)
                    imported_count += 1

                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "term": row.get("术语名称", ""),
                        "error": str(e)
                    })
                    failed_count += 1

            db.commit()

            # 更新术语库的术语计数
            collection.term_count = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id,
                GlossaryTermModel.is_enabled == True
            ).count()
            db.commit()

            logger.info(f"CSV导入完成: 成功{imported_count}条, 失败{failed_count}条")
            return GlossaryImportResponse(
                imported_count=imported_count,
                failed_count=failed_count,
                errors=errors
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CSV导入失败: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"CSV导入失败: {str(e)}")
        finally:
            self._close_db()

    def export_to_csv(self, collection_id: int) -> str:
        """
        导出术语为CSV

        Args:
            collection_id: 术语库ID

        Returns:
            str: CSV文件内容

        Raises:
            HTTPException: 术语库不存在
        """
        try:
            db = self._get_db()

            # 检查术语库是否存在
            collection = db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.id == collection_id
            ).first()

            if not collection:
                raise HTTPException(status_code=404, detail=f"术语库 ID={collection_id} 不存在")

            # 查询所有术语
            terms = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id
            ).order_by(GlossaryTermModel.term.asc()).all()

            # 生成CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(["术语名称", "同义词", "描述", "示例"])

            # 写入数据
            for term in terms:
                synonyms = term.get_synonyms_list()
                examples = term.get_examples_list()

                writer.writerow([
                    term.term,
                    ";".join(synonyms),
                    term.description or "",
                    ";".join(examples) if examples else ""
                ])

            csv_content = output.getvalue()
            logger.info(f"CSV导出完成: {collection.name}, 共{len(terms)}条术语")

            return csv_content
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CSV导出失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"CSV导出失败: {str(e)}")
        finally:
            self._close_db()
