"""
文件索引数据模型
定义文件索引的数据库表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class FileModel(Base):
    """
    文件索引表模型

    存储所有被索引文件的基本信息和元数据
    """
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    file_path = Column(String(1000), unique=True, nullable=False, comment="文件绝对路径")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_extension = Column(String(10), nullable=False, comment="文件扩展名")
    file_type = Column(String(20), nullable=False, comment="文件类型(video/audio/document/image)")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    created_at = Column(DateTime, nullable=False, comment="文件创建时间")
    modified_at = Column(DateTime, nullable=False, comment="文件修改时间")
    indexed_at = Column(DateTime, nullable=False, default=func.now(), comment="索引时间")
    content_hash = Column(String(64), nullable=False, comment="文件内容哈希(用于变更检测)")
    faiss_index_id = Column(Integer, nullable=True, comment="关联Faiss向量索引ID")
    whoosh_doc_id = Column(String(64), nullable=True, comment="关联Whoosh文档ID")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 文件信息字典
        """
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "content_hash": self.content_hash,
            "faiss_index_id": self.faiss_index_id,
            "whoosh_doc_id": self.whoosh_doc_id
        }

    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        获取支持的文件扩展名列表

        Returns:
            list: 支持的文件扩展名
        """
        return {
            # 文档类型
            ".pdf", ".txt", ".md", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            # 音频类型
            ".mp3", ".wav", ".flac", ".m4a", ".aac",
            # 视频类型
            ".mp4", ".avi", ".mkv", ".mov", ".wmv",
            # 图片类型
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"
        }

    @classmethod
    def classify_file_type(cls, extension: str) -> str:
        """
        根据文件扩展名分类文件类型

        Args:
            extension: 文件扩展名（包含点号）

        Returns:
            str: 文件类型分类
        """
        extension = extension.lower()

        if extension in {".pdf", ".txt", ".md", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
            return "document"
        elif extension in {".mp3", ".wav", ".flac", ".m4a", ".aac"}:
            return "audio"
        elif extension in {".mp4", ".avi", ".mkv", ".mov", ".wmv"}:
            return "video"
        elif extension in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
            return "image"
        else:
            return "other"

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<FileModel(id={self.id}, file_name={self.file_name}, file_type={self.file_type})>"