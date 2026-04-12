# backend/app/services/glossary_service.py
"""
术语匹配和扩展服务
提供查询词的术语匹配和同义词扩展功能
"""
import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.database import SessionLocal
from app.models.glossary_term import GlossaryTermModel
from app.models.glossary_collection import GlossaryCollectionModel
from app.schemas.glossary import (
    GlossaryExpandRequest,
    GlossaryExpandResponse,
    MatchedTerm
)

logger = logging.getLogger(__name__)


class GlossaryService:
    """术语匹配和扩展服务类"""

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

    def expand_query(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> GlossaryExpandResponse:
        """
        扩展查询词

        Args:
            query: 原始查询词
            collection_ids: 术语库ID列表，None表示全部

        Returns:
            GlossaryExpandResponse: 查询扩展响应
        """
        try:
            # 获取匹配的术语
            matched_terms = self._match_terms(query, collection_ids)

            # 收集所有查询词
            expanded_queries = [query]
            collection_names = set()

            for term in matched_terms:
                expanded_queries.extend(term.synonyms)
                collection_names.add(term.collection_name)

            # 去重
            expanded_queries = list(set(expanded_queries))

            return GlossaryExpandResponse(
                original_query=query,
                matched_terms=matched_terms,
                expanded_queries=expanded_queries,
                used_collections=list(collection_names)
            )
        except Exception as e:
            logger.error(f"查询扩展失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"查询扩展失败: {str(e)}")

    def _match_terms(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> List[MatchedTerm]:
        """
        匹配查询中的术语

        Args:
            query: 查询词
            collection_ids: 术语库ID列表，None表示全部

        Returns:
            List[MatchedTerm]: 匹配的术语列表
        """
        try:
            db = self._get_db()

            # 构建查询
            db_query = db.query(
                GlossaryTermModel.id,
                GlossaryTermModel.term,
                GlossaryTermModel.synonyms,
                GlossaryTermModel.collection_id,
                GlossaryCollectionModel.name.label("collection_name")
            ).join(
                GlossaryCollectionModel,
                GlossaryTermModel.collection_id == GlossaryCollectionModel.id
            ).filter(
                GlossaryTermModel.is_enabled == True,
                GlossaryCollectionModel.is_enabled == True
            )

            if collection_ids:
                db_query = db_query.filter(
                    GlossaryTermModel.collection_id.in_(collection_ids)
                )

            # 简化的匹配逻辑：精确匹配或包含匹配
            # 1. 精确匹配：术语等于查询词（如 "PRD" == "PRD"）
            # 2. 包含匹配：术语包含查询词（如 "OpenAI API" 包含 "API"）
            # 3. 同义词匹配：同义词列表包含查询词（JSON 格式）
            from sqlalchemy import or_

            db_query = db_query.filter(
                or_(
                    GlossaryTermModel.term == query,
                    GlossaryTermModel.term.contains(query),
                    GlossaryTermModel.synonyms.contains(f'"{query}"')
                )
            )

            results = db_query.all()

            # 解析结果
            matched_terms = []
            for row in results:
                synonyms = json.loads(row.synonyms) if isinstance(row.synonyms, str) else row.synonyms
                matched_terms.append(MatchedTerm(
                    id=row.id,
                    term=row.term,
                    synonyms=synonyms,
                    collection_id=row.collection_id,
                    collection_name=row.collection_name
                ))

            logger.info(f"术语匹配完成: query='{query}', matched_terms={len(matched_terms)}")
            return matched_terms
        except Exception as e:
            logger.error(f"匹配术语失败: {str(e)}")
            return []
        finally:
            self._close_db()

    def get_enabled_collection_ids(self, selected_ids: Optional[List[int]] = None) -> List[int]:
        """
        获取启用的术语库ID列表

        Args:
            selected_ids: 用户选择的术语库ID列表，None表示全部启用

        Returns:
            List[int]: 启用的术语库ID列表
        """
        try:
            db = self._get_db()

            query = db.query(GlossaryCollectionModel.id).filter(
                GlossaryCollectionModel.is_enabled == True
            )

            if selected_ids:
                query = query.filter(GlossaryCollectionModel.id.in_(selected_ids))

            result = query.all()
            return [row.id for row in result]
        except Exception as e:
            logger.error(f"获取启用术语库ID失败: {str(e)}")
            return []
        finally:
            self._close_db()
