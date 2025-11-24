"""
搜索历史数据模型
定义用户搜索历史的数据库表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class SearchHistoryModel(Base):
    """
    搜索历史表模型

    记录用户的搜索查询历史和结果统计
    """
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    search_query = Column(String(500), nullable=False, comment="搜索查询")
    input_type = Column(String(20), nullable=False, comment="输入类型(voice/text/image)")
    search_type = Column(String(20), nullable=False, comment="搜索类型(semantic/fulltext/hybrid)")
    ai_model_used = Column(String(100), nullable=True, comment="使用的AI模型")
    result_count = Column(Integer, nullable=False, default=0, comment="结果数量")
    response_time = Column(Float, nullable=False, comment="响应时间(秒)")
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="搜索时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 搜索历史记录字典
        """
        return {
            "id": self.id,
            "search_query": self.search_query,
            "input_type": self.input_type,
            "search_type": self.search_type,
            "ai_model_used": self.ai_model_used,
            "result_count": self.result_count,
            "response_time": self.response_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_input_types(cls) -> list:
        """
        获取支持的输入类型

        Returns:
            list: 支持的输入类型列表
        """
        return ["text", "voice", "image"]

    @classmethod
    def get_search_types(cls) -> list:
        """
        获取支持的搜索类型

        Returns:
            list: 支持的搜索类型列表
        """
        return ["semantic", "fulltext", "hybrid"]

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<SearchHistoryModel(id={self.id}, query={self.search_query[:50]}..., type={self.search_type})>"