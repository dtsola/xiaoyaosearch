"""
LLM cache model for caching LLM responses to avoid duplicate API calls.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Index
from sqlalchemy.orm import relationship

from db.base import Base


class LLMCache(Base):
    """LLM response cache model."""

    __tablename__ = "llm_cache"

    id = Column(Integer, primary_key=True, index=True)

    # Cache key and content
    cache_key = Column(String, index=True, nullable=False, unique=True)
    prompt_hash = Column(String, index=True)  # Hash of the prompt for faster lookups

    # Request information
    llm_provider = Column(String, index=True)  # openai, ollama, mock
    llm_model = Column(String, index=True)     # gpt-4, llama2, etc.
    prompt_template = Column(String)           # Template used for prompt
    system_prompt = Column(Text)               # System prompt if used

    # Response content
    response_content = Column(Text, nullable=False)
    structured_data = Column(JSON)             # Parsed structured response
    function_calls = Column(JSON)             # Function calls if any

    # Usage and cost information
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    response_time_ms = Column(Integer)
    cost_usd = Column(Float, default=0.0)

    # Response metadata
    finish_reason = Column(String)              # stop, length, etc.
    confidence_score = Column(Float)            # Response confidence if applicable
    quality_score = Column(Float)               # Quality score if rated

    # Cache management
    hit_count = Column(Integer, default=0)      # Number of times this cache was hit
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)               # Cache expiration time
    ttl_seconds = Column(Integer, default=3600) # Time to live in seconds

    # Additional metadata
    request_metadata = Column(JSON)             # Additional request parameters
    response_metadata = Column(JSON)            # Response metadata

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LLMCache(id={self.id}, provider='{self.llm_provider}', model='{self.llm_model}', hits={self.hit_count})>"

    @property
    def is_expired(self):
        """Check if cache entry is expired."""
        if self.expires_at is None:
            # Use TTL if expiration not explicitly set
            return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self):
        """Check if cache entry is still valid."""
        return not self.is_expired and self.response_content is not None

    def record_hit(self):
        """Record a cache hit."""
        self.hit_count += 1
        self.last_accessed = datetime.utcnow()

    def set_expiration(self, ttl_seconds=None):
        """Set expiration time for cache entry."""
        if ttl_seconds is not None:
            self.ttl_seconds = ttl_seconds
        self.expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)

    def extend_ttl(self, additional_seconds):
        """Extend TTL by additional seconds."""
        self.ttl_seconds += additional_seconds
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(seconds=additional_seconds)

    @property
    def efficiency_score(self):
        """Calculate cache efficiency score."""
        if self.hit_count == 0:
            return 0.0
        return min(self.hit_count / 10.0, 1.0)  # Normalize to 0-1 range

    @property
    def cost_savings(self):
        """Calculate cost savings from cache hits."""
        return self.cost_usd * self.hit_count

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'response_content': self.response_content,
            'structured_data': self.structured_data,
            'total_tokens': self.total_tokens,
            'response_time_ms': self.response_time_ms,
            'cost_usd': self.cost_usd,
            'hit_count': self.hit_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'efficiency_score': self.efficiency_score,
            'cost_savings': self.cost_savings
        }

# Create indexes for better performance
Index('idx_llm_cache_provider_model', LLMCache.llm_provider, LLMCache.llm_model)
Index('idx_llm_cache_created_expires', LLMCache.created_at, LLMCache.expires_at)
Index('idx_llm_cache_hits_last_accessed', LLMCache.hit_count, LLMCache.last_accessed)