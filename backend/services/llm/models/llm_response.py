"""
LLM response models for query understanding and AI services.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class LLMProvider(str, Enum):
    """LLM provider types."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    MOCK = "mock"
    CLAUDE = "claude"
    GEMINI = "gemini"


class ResponseStatus(str, Enum):
    """Response status types."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    MODEL_UNAVAILABLE = "model_unavailable"
    INVALID_REQUEST = "invalid_request"


class LLMRequestMetadata(BaseModel):
    """Metadata about the LLM request."""
    provider: LLMProvider = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model name")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    prompt_tokens: Optional[int] = Field(None, description="Number of tokens in prompt")
    completion_tokens: Optional[int] = Field(None, description="Number of tokens in completion")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    cost_usd: Optional[float] = Field(None, description="Cost in USD")
    cache_hit: bool = Field(False, description="Whether response was from cache")
    temperature: Optional[float] = Field(None, description="Temperature used for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens allowed")

    @validator('response_time_ms')
    def validate_response_time(cls, v):
        """Validate response time is non-negative."""
        if v < 0:
            raise ValueError("Response time must be non-negative")
        return v


class LLMErrorInfo(BaseModel):
    """Error information for failed LLM requests."""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Detailed error message")
    error_code: Optional[str] = Field(None, description="Provider-specific error code")
    retry_count: int = Field(0, description="Number of retry attempts")
    is_recoverable: bool = Field(False, description="Whether error is recoverable")
    fallback_used: bool = Field(False, description="Whether fallback provider was used")

    @validator('retry_count')
    def validate_retry_count(cls, v):
        """Validate retry count is non-negative."""
        if v < 0:
            raise ValueError("Retry count must be non-negative")
        return v


class LLMResponseData(BaseModel):
    """Core data from LLM response."""
    content: str = Field(..., description="Generated content")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from provider")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Parsed structured data")
    function_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Function calls if any")
    tool_use: Optional[Dict[str, Any]] = Field(None, description="Tool use information")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")

    @validator('content')
    def validate_content_not_empty(cls, v):
        """Validate content is not empty."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class LLMResponse(BaseModel):
    """Complete LLM response with metadata and status."""
    status: ResponseStatus = Field(..., description="Response status")
    data: Optional[LLMResponseData] = Field(None, description="Response data if successful")
    error: Optional[LLMErrorInfo] = Field(None, description="Error information if failed")
    metadata: LLMRequestMetadata = Field(..., description="Request and response metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @validator('data')
    def validate_data_consistency(cls, v, values):
        """Validate data consistency with status."""
        if 'status' in values and values['status'] == ResponseStatus.SUCCESS and v is None:
            raise ValueError("Data cannot be None for successful responses")
        return v

    @validator('error')
    def validate_error_consistency(cls, v, values):
        """Validate error consistency with status."""
        if 'status' in values and values['status'] != ResponseStatus.SUCCESS and v is None:
            raise ValueError("Error cannot be None for failed responses")
        return v

    @property
    def is_successful(self) -> bool:
        """Check if response was successful."""
        return self.status == ResponseStatus.SUCCESS

    @property
    def content(self) -> Optional[str]:
        """Get content from response."""
        return self.data.content if self.data and self.data.content else None

    @property
    def structured_data(self) -> Optional[Dict[str, Any]]:
        """Get structured data from response."""
        return self.data.structured_data if self.data else None


class BatchLLMRequest(BaseModel):
    """Batch LLM request for multiple queries."""
    requests: List[Dict[str, Any]] = Field(..., min_items=1, max_items=10, description="Batch requests")
    provider: LLMProvider = Field(..., description="LLM provider to use")
    model: str = Field(..., description="Model name")
    max_concurrent: int = Field(3, ge=1, le=10, description="Maximum concurrent requests")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Timeout per request")

    @validator('requests')
    def validate_requests_not_empty(cls, v):
        """Validate requests list is not empty."""
        if len(v) == 0:
            raise ValueError("Requests list cannot be empty")
        return v


class BatchLLMResponse(BaseModel):
    """Batch LLM response."""
    responses: List[LLMResponse] = Field(..., description="Individual responses")
    batch_metadata: Dict[str, Any] = Field(..., description="Batch processing metadata")
    total_time_ms: int = Field(..., description="Total processing time")
    success_count: int = Field(..., description="Number of successful responses")
    error_count: int = Field(..., description="Number of failed responses")

    @validator('success_count', 'error_count')
    def validate_counts(cls, v, values):
        """Validate count consistency."""
        if 'responses' in values and v > len(values['responses']):
            raise ValueError("Count cannot exceed number of responses")
        return v

    @validator('total_time_ms')
    def validate_total_time(cls, v):
        """Validate total time is non-negative."""
        if v < 0:
            raise ValueError("Total time must be non-negative")
        return v

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.error_count
        return self.success_count / total if total > 0 else 0.0