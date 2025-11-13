"""
Directory model for storing directory information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class Directory(Base):
    """Directory information model."""

    __tablename__ = "directories"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("directories.id"))

    # Directory timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    last_scanned = Column(DateTime)

    # Directory configuration
    is_indexed = Column(Boolean, default=True)
    scan_depth = Column(Integer, default=10)  # Maximum depth to scan
    exclude_patterns = Column(String)  # Comma-separated patterns to exclude

    # Scanning status
    scan_status = Column(String, default="pending")  # pending, scanning, completed, failed
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)

    # Relationships
    parent = relationship("Directory", remote_side=[id])
    files = relationship("File", back_populates="directory")

    def __repr__(self):
        return f"<Directory(id={self.id}, name={self.name}, path={self.path})>"