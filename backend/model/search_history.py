"""
Search history model for tracking user searches.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class SearchHistory(Base):
    """Search history model."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, index=True, nullable=False)
    query_type = Column(String, index=True, default="text")  # text, voice, image
    query_embedding = Column(String)  # Reference to query vector

    # Search parameters
    filters_json = Column(Text)  # JSON string of search filters
    limit = Column(Integer, default=20)
    search_mode = Column(String, default="hybrid")  # hybrid, vector, fulltext

    # Search results
    result_count = Column(Integer, default=0)
    search_time_ms = Column(Integer)  # Search execution time in milliseconds
    results_json = Column(Text)  # JSON string of search result IDs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, query='{self.query_text}', type={self.query_type})>"