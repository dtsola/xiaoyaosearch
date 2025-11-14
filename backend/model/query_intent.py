"""
Query intent model for storing LLM-powered query analysis results.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class QueryIntent(Base):
    """Query intent analysis result model."""

    __tablename__ = "query_intents"

    id = Column(Integer, primary_key=True, index=True)
    original_query = Column(String, index=True, nullable=False)
    normalized_query = Column(String, index=True)

    # Intent classification
    intent_type = Column(String, index=True, nullable=False)  # document_search, image_search, etc.
    confidence = Column(Float, default=0.0)  # Confidence score 0.0-1.0

    # Extracted information
    keywords = Column(JSON)  # List of extracted keywords
    entities = Column(JSON)  # Named entities and their types
    file_types = Column(JSON)  # Detected file types
    language = Column(String, index=True)  # Detected language code
    sentiment = Column(String)  # Query sentiment if applicable

    # Time range information
    time_range_start = Column(DateTime)  # Start date of time range
    time_range_end = Column(DateTime)    # End date of time range
    time_expression = Column(String)     # Original time expression

    # Semantic analysis
    semantic_description = Column(Text)  # Semantic description of query
    sub_intents = Column(JSON)          # Secondary intents
    query_complexity = Column(String, default="simple")  # simple, moderate, complex

    # Processing metadata
    llm_provider = Column(String)       # Which LLM provider was used
    llm_model = Column(String)          # Which model was used
    processing_time_ms = Column(Integer)  # Processing time in milliseconds
    expanded_query = Column(JSON)       # Query expansion results

    # Relationships to search history
    search_history_id = Column(Integer, ForeignKey("search_history.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<QueryIntent(id={self.id}, intent='{self.intent_type}', confidence={self.confidence})>"

    @property
    def has_time_range(self):
        """Check if intent has time range information."""
        return self.time_range_start is not None and self.time_range_end is not None

    @property
    def is_high_confidence(self):
        """Check if intent has high confidence."""
        return self.confidence >= 0.8

    @property
    def is_complex_query(self):
        """Check if query is complex."""
        return self.query_complexity in ["moderate", "complex"]