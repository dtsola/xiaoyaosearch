"""
Search query models for LLM-enhanced query processing.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .query_intent import QueryIntent, IntentType


class ParsedQuery(BaseModel):
    """Parsed query with enhanced understanding."""
    original_query: str = Field(..., description="Original user query")
    normalized_query: str = Field(..., description="Normalized/cleaned query")
    expanded_query: Optional[str] = Field(None, description="Expanded query with synonyms")
    intent: QueryIntent = Field(..., description="Query intent analysis")
    search_terms: List[str] = Field(default_factory=list, description="Main search terms")
    exclude_terms: List[str] = Field(default_factory=list, description="Terms to exclude")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Extracted filters")
    boost_terms: List[str] = Field(default_factory=list, description="Terms to boost in ranking")
    semantic_embedding: Optional[List[float]] = Field(None, description="Query embedding vector")
    query_complexity: str = Field(..., pattern="^(simple|moderate|complex)$", description="Query complexity level")

    @validator('search_terms')
    def validate_search_terms(cls, v):
        """Validate search terms are not empty."""
        if len(v) == 0:
            raise ValueError("Search terms cannot be empty")
        return v


class QueryExpansion(BaseModel):
    """Query expansion results."""
    synonyms: List[str] = Field(default_factory=list, description="Synonym expansions")
    related_terms: List[str] = Field(default_factory=list, description="Related terms")
    translations: Dict[str, str] = Field(default_factory=dict, description="Multi-language translations")
    semantic_variations: List[str] = Field(default_factory=list, description="Semantic variations")
    expansion_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in expansions")

    @validator('expansion_confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class QueryFilter(BaseModel):
    """Query filter extracted from natural language."""
    filter_type: str = Field(..., description="Type of filter (file_type, size, date, etc.)")
    value: Any = Field(..., description="Filter value")
    operator: str = Field("eq", description="Comparison operator")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in filter extraction")

    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class EnhancedSearchRequest(BaseModel):
    """Enhanced search request with LLM processing."""
    query: str = Field(..., min_length=1, max_length=1000, description="Original search query")
    parsed_query: Optional[ParsedQuery] = Field(None, description="Parsed query with analysis")
    query_type: str = Field("text", pattern="^(text|voice|image)$", description="Query input type")
    search_mode: str = Field("hybrid", pattern="^(hybrid|vector|fulltext)$", description="Search mode")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Result offset for pagination")
    filters: Optional[Dict[str, Any]] = Field(None, description="Explicit filters")
    include_content: bool = Field(False, description="Include file content in results")
    highlight: bool = Field(True, description="Highlight matching terms in results")
    explain_results: bool = Field(False, description="Include result explanations")
    llm_processed: bool = Field(False, description="Whether query was processed by LLM")
    processing_time_ms: Optional[int] = Field(None, description="Query processing time in milliseconds")


class QuerySuggestion(BaseModel):
    """Query suggestion based on AI analysis."""
    text: str = Field(..., description="Suggested query text")
    type: str = Field(..., pattern="^(completion|correction|expansion|related)$", description="Suggestion type")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    reason: Optional[str] = Field(None, description="Reason for suggestion")
    intent_change: Optional[IntentType] = Field(None, description="Suggested intent change")

    @validator('score')
    def validate_score(cls, v):
        """Validate relevance score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class SearchQuery(BaseModel):
    """Complete search query with LLM enhancements."""
    original_query: str
    enhanced_query: Optional[str]
    intent: QueryIntent
    expansion: Optional[QueryExpansion]
    filters: List[QueryFilter]
    suggestions: List[QuerySuggestion]
    processing_metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)