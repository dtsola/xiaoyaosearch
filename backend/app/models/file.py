"""
文件索引数据模型
定义文件索引的数据库表结构（软外键模式）
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Boolean, Float
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
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="文件创建时间")
    modified_at = Column(DateTime, nullable=False, default=datetime.now, comment="文件修改时间")
    indexed_at = Column(DateTime, nullable=False, default=datetime.now, comment="索引时间")
    content_hash = Column(String(64), nullable=False, comment="文件内容哈希(用于变更检测)")
    # 文件处理状态
    is_indexed = Column(Boolean, default=False, comment="是否已索引")
    is_content_parsed = Column(Boolean, default=False, comment="是否已解析内容")
    index_status = Column(String(20), default="pending", comment="索引状态(pending/processing/completed/failed)")

    # 元数据字段
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    title = Column(String(500), nullable=True, comment="文档标题")
    author = Column(String(200), nullable=True, comment="作者")
    keywords = Column(Text, nullable=True, comment="关键词，逗号分隔")

    # 内容统计
    content_length = Column(Integer, default=0, comment="内容长度（字符数）")
    word_count = Column(Integer, default=0, comment="词汇数量")

    # 处理质量评估
    parse_confidence = Column(Float, default=0.0, comment="解析置信度(0-1)")
    index_quality_score = Column(Float, default=0.0, comment="索引质量评分(0-1)")

    # 最后处理信息
    last_error = Column(Text, nullable=True, comment="最后错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")

    # 索引版本控制
    index_version = Column(String(20), default="1.0", comment="索引版本")
    needs_reindex = Column(Boolean, default=False, comment="是否需要重新索引")

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
            "is_indexed": self.is_indexed,
            "is_content_parsed": self.is_content_parsed,
            "index_status": self.index_status,
            "mime_type": self.mime_type,
            "title": self.title,
            "author": self.author,
            "keywords": self.keywords,
            "content_length": self.content_length,
            "word_count": self.word_count,
            "parse_confidence": self.parse_confidence,
            "index_quality_score": self.index_quality_score,
            "last_error": self.last_error,
            "retry_count": self.retry_count,
            "index_version": self.index_version,
            "needs_reindex": self.needs_reindex,
            # v2.0分块支持字段
            "is_chunked": self.is_chunked,
            "total_chunks": self.total_chunks,
            "chunk_strategy": self.chunk_strategy,
            "avg_chunk_size": self.avg_chunk_size
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

    def update_index_status(self, status: str, error_message: str = None) -> None:
        """
        更新索引状态

        Args:
            status: 新的索引状态
            error_message: 错误信息（可选）
        """
        self.index_status = status
        if error_message:
            self.last_error = error_message

        if status == "completed":
            self.is_indexed = True
            self.needs_reindex = False
        elif status == "processing":
            self.is_indexed = False
        elif status == "failed":
            self.is_indexed = False
            self.retry_count += 1

    def mark_for_reindex(self) -> None:
        """标记文件需要重新索引"""
        self.needs_reindex = True
        self.index_status = "pending"

    def calculate_quality_score(self) -> float:
        """
        计算文件质量评分

        Returns:
            float: 质量评分 (0-1)
        """
        score = 0.0

        # 解析置信度权重 40%
        score += self.parse_confidence * 0.4

        # 内容长度权重 30% (越长越好，但有上限)
        if self.content_length > 0:
            length_score = min(self.content_length / 10000, 1.0)  # 10000字符为满分
            score += length_score * 0.3

        # 索引完整性权重 20%
        completeness_score = 0.0
        if self.title:
            completeness_score += 0.5
        if self.content_length > 0:
            completeness_score += 0.5
        score += completeness_score * 0.2

        # 错误率权重 10%
        error_penalty = min(self.retry_count * 0.1, 0.1)
        score -= error_penalty

        # 确保分数在0-1范围内
        return max(0.0, min(1.0, score))

    def get_file_size_mb(self) -> float:
        """
        获取文件大小（MB）

        Returns:
            float: 文件大小（MB）
        """
        return self.file_size / (1024 * 1024)

    def get_file_extension_display(self) -> str:
        """
        获取显示用的文件扩展名

        Returns:
            str: 文件扩展名（不包含点号）
        """
        return self.file_extension.lstrip('.').upper() if self.file_extension else ""

    def get_keyword_list(self) -> list:
        """
        获取关键词列表

        Returns:
            list: 关键词列表
        """
        if not self.keywords:
            return []

        return [kw.strip() for kw in self.keywords.split(',') if kw.strip()]

    @classmethod
    def get_index_statuses(cls) -> list:
        """
        获取支持的索引状态

        Returns:
            list: 支持的索引状态列表
        """
        return ["pending", "processing", "completed", "failed"]

    @classmethod
    def get_supported_mime_types(cls) -> dict:
        """
        获取支持的MIME类型映射

        Returns:
            dict: 扩展名到MIME类型的映射
        """
        return {
            # 文档类型
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.rtf': 'application/rtf',
            # 音频类型
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            # 视频类型
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            # 图片类型
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            # 代码类型
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.ts': 'application/typescript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.java': 'text/x-java-source',
            '.cpp': 'text/x-c++src',
            '.c': 'text/x-csrc',
            '.go': 'text/x-go',
            '.rs': 'text/x-rust',
        }

    # 分块相关字段 (v2.0新增)
    is_chunked = Column(Boolean, default=False, comment="是否已分块处理")
    total_chunks = Column(Integer, default=1, comment="总分块数量")
    chunk_strategy = Column(String(50), default='500+50', comment="分块策略")
    avg_chunk_size = Column(Integer, default=500, comment="平均分块大小")

    # 注意：软外键模式下不定义SQLAlchemy relationship
    # 关联关系由应用层通过file_id字段手动维护

    def mark_as_chunked(self, total_chunks: int, chunk_strategy: str = '500+50') -> None:
        """
        标记文件为已分块处理

        Args:
            total_chunks: 分块总数
            chunk_strategy: 分块策略
        """
        self.is_chunked = True
        self.total_chunks = total_chunks
        self.chunk_strategy = chunk_strategy
        self.avg_chunk_size = total_chunks if total_chunks > 0 else 500

    def get_chunk_info(self) -> dict:
        """
        获取分块信息

        Returns:
            dict: 分块相关信息
        """
        return {
            "is_chunked": self.is_chunked,
            "total_chunks": self.total_chunks,
            "chunk_strategy": self.chunk_strategy,
            "avg_chunk_size": self.avg_chunk_size
        }

    @classmethod
    def get_supported_chunk_strategies(cls) -> list:
        """
        获取支持的分块策略

        Returns:
            list: 支持的分块策略列表
        """
        return [
            "500+50",    # 500字符块，50字符重叠
            "1000+100",  # 1000字符块，100字符重叠
            "2000+200",  # 2000字符块，200字符重叠
            "custom"     # 自定义策略
        ]

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<FileModel(id={self.id}, file_name={self.file_name}, file_type={self.file_type}, status={self.index_status})>"