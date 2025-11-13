"""
User settings model for storing application preferences.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from db.base import Base


class UserSettings(Base):
    """User settings model."""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text)
    description = Column(Text)

    # Settings category
    category = Column(String, index=True)  # search, indexing, ui, ai, etc.
    data_type = Column(String, default="string")  # string, integer, boolean, json

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings(key='{self.key}', value='{self.value}', category='{self.category}')>"