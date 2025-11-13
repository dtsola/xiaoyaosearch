"""
File model for storing file metadata.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship

from db.base import Base


class File(Base):
    """File metadata model."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, index=True, nullable=False)
    extension = Column(String, index=True, nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String, index=True)

    # File timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    # File content information
    content_type = Column(String, index=True)  # text, image, audio, video, document
    content_text = Column(Text)  # Extracted text content
    content_hash = Column(String, index=True)  # For duplicate detection

    # AI processing results
    text_vector = Column(String)  # Reference to vector index
    image_tags = Column(Text)  # JSON string of image tags
    audio_transcript = Column(Text)  # Audio transcription
    ocr_text = Column(Text)  # OCR extracted text

    # Search relevance
    search_score = Column(Float, default=0.0)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Directory relationship
    directory_id = Column(Integer, ForeignKey("directories.id"))
    directory = relationship("Directory", back_populates="files")

    # File status
    is_deleted = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed

    # Additional metadata
    metadata_json = Column(Text)  # JSON string for additional metadata

    # Create indexes for common search patterns
    __table_args__ = (
        Index('idx_files_content_type_created', 'content_type', 'created_at'),
        Index('idx_files_extension_size', 'extension', 'size'),
        Index('idx_files_search_score', 'search_score'),
        Index('idx_files_directory_filename', 'directory_id', 'filename'),
    )

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, path={self.path})>"