"""
File-Tag relationship model for many-to-many relationship.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class FileTag(Base):
    """File-Tag relationship model for many-to-many relationship."""

    __tablename__ = "file_tags"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    # Tag application metadata
    confidence = Column(Integer, default=100)  # Confidence score 0-100
    source = Column(String, default="manual")  # manual, ai_system, user_preference

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    file = relationship("File", backref="file_tags")
    tag = relationship("Tag", backref="tag_files")

    def __repr__(self):
        return f"<FileTag(file_id={self.file_id}, tag_id={self.tag_id})>"