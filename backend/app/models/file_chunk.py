"""
文件分块数据模型
定义文件分块索引的数据库表结构（软外键模式）
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class FileChunkModel(Base):
    """
    文件分块表模型

    存储文件分块后的内容和索引信息，支持精确搜索定位
    """
    __tablename__ = "file_chunks"

    # 主键和关联
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    file_id = Column(Integer, nullable=False, comment="关联文件ID（软外键，应用层维护）")
    chunk_index = Column(Integer, nullable=False, comment="分块索引（从0开始）")

    # 分块内容
    content = Column(Text, nullable=False, comment="分块文本内容")
    content_length = Column(Integer, default=0, comment="分块内容长度（字符数）")
    start_position = Column(Integer, nullable=False, comment="在原文件中的起始位置")
    end_position = Column(Integer, nullable=False, comment="在原文件中的结束位置")

    # 索引关联
    faiss_index_id = Column(Integer, nullable=True, comment="关联Faiss向量索引ID")
    whoosh_doc_id = Column(String(64), nullable=True, comment="关联Whoosh文档ID")

    # 处理状态
    is_indexed = Column(Boolean, default=False, comment="是否已索引")
    index_status = Column(String(20), default="pending", comment="索引状态(pending/processing/completed/failed)")

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    indexed_at = Column(DateTime, nullable=True, comment="索引完成时间")

    # 注意：软外键模式下不定义SQLAlchemy relationship
    # 关联关系由应用层通过file_id字段手动维护

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 分块信息字典
        """
        return {
            "id": self.id,
            "file_id": self.file_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "content_length": self.content_length,
            "start_position": self.start_position,
            "end_position": self.end_position,
            "faiss_index_id": self.faiss_index_id,
            "whoosh_doc_id": self.whoosh_doc_id,
            "is_indexed": self.is_indexed,
            "index_status": self.index_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None
        }

    def get_content_summary(self, max_length: int = 200) -> str:
        """
        获取分块内容摘要

        Args:
            max_length: 最大摘要长度

        Returns:
            str: 内容摘要
        """
        if not self.content:
            return ""

        content = self.content.strip()
        if len(content) <= max_length:
            return content

        return content[:max_length] + "..."

    def update_index_status(self, status: str) -> None:
        """
        更新索引状态

        Args:
            status: 新的索引状态
        """
        self.index_status = status

        if status == "completed":
            self.is_indexed = True
            self.indexed_at = datetime.now()
        elif status == "processing":
            self.is_indexed = False
        elif status == "failed":
            self.is_indexed = False

    def get_chunk_size_info(self) -> dict:
        """
        获取分块大小信息

        Returns:
            dict: 分块大小统计
        """
        return {
            "content_length": self.content_length,
            "character_count": len(self.content) if self.content else 0,
            "span": self.end_position - self.start_position,
            "chunk_index": self.chunk_index
        }

    def contains_position(self, position: int) -> bool:
        """
        检查指定位置是否在分块范围内

        Args:
            position: 字符位置

        Returns:
            bool: 是否在分块范围内
        """
        return self.start_position <= position < self.end_position

    def get_relevance_score(self, query_positions: list) -> float:
        """
        根据查询位置计算相关性评分

        Args:
            query_positions: 查询词在原文件中的位置列表

        Returns:
            float: 相关性评分 (0-1)
        """
        if not query_positions:
            return 0.0

        # 计算查询位置在分块中的覆盖率
        matched_positions = sum(1 for pos in query_positions if self.contains_position(pos))
        coverage = matched_positions / len(query_positions)

        # 考虑分块长度因素，避免过长分块获得不公平的高分
        length_factor = min(self.content_length / 500, 1.0)  # 500字符为基准

        # 综合评分
        return coverage * 0.7 + length_factor * 0.3

    @classmethod
    def get_index_statuses(cls) -> list:
        """
        获取支持的索引状态

        Returns:
            list: 支持的索引状态列表
        """
        return ["pending", "processing", "completed", "failed"]

    @classmethod
    def get_default_chunk_size(cls) -> int:
        """
        获取默认分块大小

        Returns:
            int: 默认分块大小（字符数）
        """
        return 500

    @classmethod
    def get_default_overlap(cls) -> int:
        """
        获取默认重叠大小

        Returns:
            int: 默认重叠大小（字符数）
        """
        return 50

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<FileChunkModel(id={self.id}, file_id={self.file_id}, chunk_index={self.chunk_index}, status={self.index_status})>"