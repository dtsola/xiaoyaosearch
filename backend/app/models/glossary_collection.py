# backend/app/models/glossary_collection.py
"""
术语库集合数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class GlossaryCollectionModel(Base):
    """
    术语库集合模型

    存储术语库的基本信息和配置
    """
    __tablename__ = "glossary_collections"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 基础信息
    name = Column(String(100), unique=True, nullable=False, comment="术语库名称")
    description = Column(Text, nullable=True, comment="术语库描述")
    icon = Column(String(50), nullable=True, comment="图标（emoji）")
    color = Column(String(20), nullable=True, comment="颜色代码")

    # 状态字段
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    term_count = Column(Integer, default=0, nullable=False, comment="术语数量")
    is_system = Column(Boolean, default=False, nullable=False, comment="是否系统预置")

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 术语库信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "is_enabled": self.is_enabled,
            "term_count": self.term_count,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<GlossaryCollectionModel(id={self.id}, name={self.name}, term_count={self.term_count})>"
