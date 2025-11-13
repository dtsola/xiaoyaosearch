"""
Tag model for file tagging system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Tag(Base):
    """Tag model for categorizing files."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    color = Column(String, default="#007bff")  # Hex color code

    # Tag metadata
    is_system_tag = Column(Boolean, default=False)  # System-generated vs user-created
    category = Column(String, index=True)  # content, format, priority, etc.
    usage_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category}')>"