# backend/app/models/glossary_term.py
"""
术语数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class GlossaryTermModel(Base):
    """
    术语模型

    存储术语的详细信息，包括同义词、描述和示例
    """
    __tablename__ = "glossary_terms"
    __table_args__ = (
        UniqueConstraint('collection_id', 'term', name='uq_collection_term'),
    )

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 外键关联
    collection_id = Column(
        Integer,
        ForeignKey('glossary_collections.id', ondelete='CASCADE'),
        nullable=False,
        comment="术语库ID"
    )

    # 术语字段
    term = Column(String(100), nullable=False, comment="术语名称")
    synonyms = Column(Text, nullable=False, comment="同义词（JSON数组）")
    description = Column(Text, nullable=True, comment="术语描述")

    # 状态字段
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 术语信息字典
        """
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "term": self.term,
            "synonyms": self.get_synonyms_list(),
            "description": self.description,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_synonyms_list(self) -> list:
        """
        获取同义词列表

        Returns:
            list: 同义词列表
        """
        try:
            if isinstance(self.synonyms, str):
                return json.loads(self.synonyms)
            return self.synonyms if self.synonyms else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_synonyms(self, synonyms: list):
        """
        设置同义词

        Args:
            synonyms: 同义词列表
        """
        self.synonyms = json.dumps(synonyms, ensure_ascii=False)

    @property
    def synonyms_list(self) -> list:
        """
        同义词列表（供Pydantic使用）

        Returns:
            list: 同义词列表
        """
        return self.get_synonyms_list()

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<GlossaryTermModel(id={self.id}, term={self.term}, collection_id={self.collection_id})>"
