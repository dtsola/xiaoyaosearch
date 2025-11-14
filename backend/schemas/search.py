"""
Search schemas for API request/response validation with AI enhancements.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class SearchFilter(BaseModel):
    """Search filter schema."""
    file_types: Optional[List[str]] = Field(None, description="File extensions to include")
    exclude_types: Optional[List[str]] = Field(None, description="File extensions to exclude")
    min_size: Optional[int] = Field(None, ge=0, description="Minimum file size in bytes")
    max_size: Optional[int] = Field(None, ge=0, description="Maximum file size in bytes")
    date_from: Optional[datetime] = Field(None, description="Search files from this date")
    date_to: Optional[datetime] = Field(None, description="Search files until this date")
    directories: Optional[List[str]] = Field(None, description="Directory paths to include")
    exclude_directories: Optional[List[str]] = Field(None, description="Directory paths to exclude")


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., description="Search query text")
    query_type: str = Field("text", pattern="^(text|voice|image)$", description="Query type")
    search_mode: str = Field("hybrid", pattern="^(hybrid|vector|fulltext)$", description="Search mode")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Result offset for pagination")
    filters: Optional[SearchFilter] = None
    include_content: bool = Field(False, description="Include file content in results")
    highlight: bool = Field(True, description="Highlight matching terms in results")
    use_ai_understanding: bool = Field(False, description="Whether to use AI query understanding")


class SearchSuggestion(BaseModel):
    """Search suggestion schema."""
    text: str
    type: str = Field(..., pattern="^(history|completion|correction|related|expansion)$")
    score: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None


class QueryUnderstandingInfo(BaseModel):
    """Query understanding information from AI analysis."""
    intent_type: Optional[str] = None
    confidence: Optional[float] = None
    keywords: Optional[List[str]] = None
    file_types: Optional[List[str]] = None
    time_range: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    is_mixed_language: Optional[bool] = None
    semantic_description: Optional[str] = None
    processing_time_ms: Optional[int] = None
    expanded_query: Optional[List[str]] = None


class SearchResponse(BaseModel):
    """Search response schema with AI enhancements."""
    results: List["FileSearchResult"]
    total: int
    query: str
    search_time_ms: int
    search_mode: str
    filters_applied: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[SearchSuggestion]] = None
    query_understanding: Optional[Dict[str, Any]] = None
    ai_enhanced: bool = Field(False, description="Whether AI was used to enhance the search")

    @validator("search_time_ms", pre=True, always=True)
    def ensure_search_time(cls, v):
        """Ensure search time is always set."""
        return v or 0


class SearchHistory(BaseModel):
    """Search history schema."""
    id: int
    query_text: str
    query_type: str
    search_mode: str
    result_count: int
    search_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class AISearchResponse(BaseModel):
    """AI-enhanced search response for detailed analysis."""
    original_query: str
    enhanced_query: Optional[str]
    query_understanding: QueryUnderstandingInfo
    search_results: List[Dict[str, Any]]
    total_results: int
    processing_time_ms: int
    suggestions: List[SearchSuggestion]
    confidence_score: float


# Import here to avoid circular imports
from schemas.file import FileSearchResult
SearchResponse.update_forward_refs()