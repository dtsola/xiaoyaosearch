"""
Query intent models for LLM-powered query understanding.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class IntentType(str, Enum):
    """Query intent types."""
    DOCUMENT_SEARCH = "document_search"
    IMAGE_SEARCH = "image_search"
    AUDIO_SEARCH = "audio_search"
    VIDEO_SEARCH = "video_search"
    MIXED_SEARCH = "mixed_search"
    SEMANTIC_SEARCH = "semantic_search"
    FACTUAL_SEARCH = "factual_search"
    UNKNOWN = "unknown"


class QueryIntent(BaseModel):
    """Query intent analysis result."""
    intent_type: IntentType = Field(..., description="Primary intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for intent classification")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Named entities and their types")
    time_range: Optional[Dict[str, Any]] = Field(None, description="Time range extracted from query")
    file_types: List[str] = Field(default_factory=list, description="File types mentioned in query")
    language: Optional[str] = Field(None, description="Detected language code")
    sentiment: Optional[str] = Field(None, description="Query sentiment if applicable")
    semantic_description: Optional[str] = Field(None, description="Semantic description of the query")
    sub_intents: List[IntentType] = Field(default_factory=list, description="Secondary intents")

    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    @validator('language')
    def validate_language(cls, v):
        """Validate language code."""
        if v is not None and len(v) not in [2, 3]:
            raise ValueError("Language code must be 2 or 3 characters")
        return v


class TimeRange(BaseModel):
    """Time range extracted from query."""
    start_date: Optional[datetime] = Field(None, description="Start date of the range")
    end_date: Optional[datetime] = Field(None, description="End date of the range")
    relative_expression: Optional[str] = Field(None, description="Original relative time expression")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in time extraction")

    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class QueryContext(BaseModel):
    """Context information for query understanding."""
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    previous_queries: List[str] = Field(default_factory=list, description="Previous queries in session")
    search_history: List[str] = Field(default_factory=list, description="Relevant search history")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User search preferences")
    current_directory: Optional[str] = Field(None, description="Current working directory")


class QueryAnalysisRequest(BaseModel):
    """Request for query analysis."""
    query: str = Field(..., min_length=1, max_length=1000, description="Query to analyze")
    context: Optional[QueryContext] = Field(None, description="Query context")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")
    analyze_intent: bool = Field(True, description="Whether to analyze intent")
    extract_keywords: bool = Field(True, description="Whether to extract keywords")
    parse_time: bool = Field(True, description="Whether to parse time expressions")
    detect_language: bool = Field(True, description="Whether to detect language")
    expand_query: bool = Field(True, description="Whether to expand the query")