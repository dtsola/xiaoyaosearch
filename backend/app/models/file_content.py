"""
文件内容数据模型
定义文件解析后的内容存储结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class FileContentModel(Base):
    """
    文件内容表模型

    存储文件解析后的文本内容和相关元数据
    """
    __tablename__ = "file_contents"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, unique=True, comment="关联文件ID")

    # 解析内容
    title = Column(String(500), nullable=True, comment="提取的标题")
    content = Column(Text, nullable=True, comment="解析的文本内容")
    content_length = Column(Integer, default=0, comment="内容长度（字符数）")
    word_count = Column(Integer, default=0, comment="词汇数量")

    # 解析信息
    language = Column(String(10), nullable=True, comment="检测到的语言(zh/en/unknown)")
    encoding = Column(String(20), nullable=True, comment="文件编码")
    confidence = Column(Float, default=0.0, comment="内容解析置信度(0-1)")
    parse_method = Column(String(50), nullable=True, comment="解析方法")

    # 处理状态
    is_parsed = Column(Boolean, default=False, comment="是否已解析")
    has_error = Column(Boolean, default=False, comment="是否有解析错误")
    error_message = Column(Text, nullable=True, comment="解析错误信息")

    # 时间戳
    parsed_at = Column(DateTime, nullable=True, comment="解析时间")
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    file = relationship("FileModel", back_populates="content")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 文件内容字典
        """
        return {
            "id": self.id,
            "file_id": self.file_id,
            "title": self.title,
            "content": self.content,
            "content_length": self.content_length,
            "word_count": self.word_count,
            "language": self.language,
            "encoding": self.encoding,
            "confidence": self.confidence,
            "parse_method": self.parse_method,
            "is_parsed": self.is_parsed,
            "has_error": self.has_error,
            "error_message": self.error_message,
            "parsed_at": self.parsed_at.isoformat() if self.parsed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_content_summary(self, max_length: int = 200) -> str:
        """
        获取内容摘要

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

    def update_statistics(self) -> None:
        """更新内容统计信息"""
        if self.content:
            self.content_length = len(self.content)
            # 简单的词汇计数（按空格分割）
            self.word_count = len(self.content.split())

    @classmethod
    def get_supported_languages(cls) -> list:
        """
        获取支持的语言列表

        Returns:
            list: 支持的语言代码列表
        """
        return ["zh", "en", "ja", "ko", "unknown"]

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<FileContentModel(id={self.id}, file_id={self.file_id}, language={self.language})>"


# 扩展FileModel以包含content关系
from sqlalchemy.orm import back_populates

# 更新FileModel以包含反向关系
class FileModelExtended(Base):
    """
    扩展的文件模型，用于包含content关系
    注意：这是一个示例，实际应该修改原始的FileModel
    """
    __tablename__ = "files"

    # 这里应该复制原始FileModel的所有字段
    # 然后添加关系
    content = relationship("FileContentModel", back_populates="file", uselist=False)