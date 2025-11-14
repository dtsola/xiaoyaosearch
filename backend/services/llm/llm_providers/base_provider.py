"""
Base LLM Provider - Abstract interface for LLM service implementations.

This module defines the abstract base class that all LLM providers must implement,
following the strategy pattern to enable easy switching between different AI models
and services (OpenAI, Ollama, etc.).
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

from ..models.llm_response import (
    LLMResponse,
    LLMProvider as Provider,
    LLMRequestMetadata,
    ResponseStatus,
    LLMErrorInfo
)

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    model: str
    temperature: float = 0.1
    max_tokens: int = 500
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True
    cache_ttl: int = 3600
    cost_per_token: float = 0.0


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement,
    ensuring consistent behavior across different AI services and models.
    """

    def __init__(
        self,
        config: LLMConfig,
        provider: Provider
    ):
        """
        Initialize the LLM provider.

        Args:
            config: Configuration for the provider
            provider: Provider type identifier
        """
        self.config = config
        self.provider = provider
        self._client = None
        self._cache = {}  # Simple in-memory cache
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    @abstractmethod
    async def _initialize_client(self) -> Any:
        """
        Initialize the provider-specific client.

        Returns:
            Provider-specific client instance
        """
        pass

    @abstractmethod
    async def _generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using the provider's API.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional provider-specific parameters

        Returns:
            Raw response from the provider
        """
        pass

    @abstractmethod
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from provider response.

        Args:
            response: Raw response from provider

        Returns:
            Extracted text content
        """
        pass

    @abstractmethod
    def _extract_usage_info(self, response: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract usage information from provider response.

        Args:
            response: Raw response from provider

        Returns:
            Dictionary with prompt_tokens, completion_tokens, total_tokens
        """
        pass

    @abstractmethod
    def _extract_error_info(self, error: Exception) -> LLMErrorInfo:
        """
        Extract error information from provider exception.

        Args:
            error: Provider-specific exception

        Returns:
            Standardized error information
        """
        pass

    async def _get_client(self) -> Any:
        """Get or initialize the client."""
        if self._client is None:
            self._client = await self._initialize_client()
        return self._client

    def _generate_cache_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate cache key for request."""
        import hashlib
        content = f"{prompt}:{system_prompt or ''}:{self.config.temperature}:{self.config.max_tokens}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response if available and not expired."""
        if not self.config.enable_caching:
            return None

        if cache_key in self._cache:
            cached_response, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.config.cache_ttl:
                logger.debug(f"Cache hit for key: {cache_key}")
                cached_response.metadata.cache_hit = True
                return cached_response
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache successful response."""
        if self.config.enable_caching and response.is_successful:
            self._cache[cache_key] = (response, datetime.now().timestamp())
            # Limit cache size
            if len(self._cache) > 1000:
                # Remove oldest entries (simple LRU)
                oldest_key = min(self._cache.keys(),
                               key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate LLM response with retry logic and caching.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM response with metadata
        """
        start_time = datetime.now()
        cache_key = self._generate_cache_key(prompt, system_prompt)

        # Check cache first
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Attempt generation with retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._attempt_generation(
                    prompt, system_prompt, start_time, **kwargs
                )

                # Cache successful response
                self._cache_response(cache_key, response)
                return response

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt == self.config.max_retries:
                    # All retries exhausted
                    return LLMResponse(
                        status=ResponseStatus.ERROR,
                        error=self._extract_error_info(e),
                        metadata=LLMRequestMetadata(
                            provider=self.provider,
                            model=self.config.model,
                            response_time_ms=int(
                                (datetime.now() - start_time).total_seconds() * 1000
                            ),
                            temperature=self.config.temperature,
                            max_tokens=self.config.max_tokens
                        )
                    )

                # Wait before retry
                if attempt < self.config.max_retries:
                    await asyncio.sleep(
                        self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    )

    async def _attempt_generation(
        self,
        prompt: str,
        system_prompt: Optional[str],
        start_time: datetime,
        **kwargs
    ) -> LLMResponse:
        """Attempt a single generation."""
        client = await self._get_client()

        # Generate completion
        raw_response = await asyncio.wait_for(
            self._generate_completion(prompt, system_prompt, **kwargs),
            timeout=self.config.timeout
        )

        # Extract content and usage info
        content = self._extract_content(raw_response)
        usage_info = self._extract_usage_info(raw_response)

        # Update statistics
        self._request_count += 1
        if usage_info.get('total_tokens'):
            self._total_tokens += usage_info['total_tokens']
            cost = usage_info['total_tokens'] * self.config.cost_per_token
            self._total_cost += cost

        # Create response metadata
        response_time_ms = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )

        metadata = LLMRequestMetadata(
            provider=self.provider,
            model=self.config.model,
            prompt_tokens=usage_info.get('prompt_tokens'),
            completion_tokens=usage_info.get('completion_tokens'),
            total_tokens=usage_info.get('total_tokens'),
            response_time_ms=response_time_ms,
            cost_usd=cost if usage_info.get('total_tokens') else None,
            cache_hit=False,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        from ..models.llm_response import LLMResponseData

        return LLMResponse(
            status=ResponseStatus.SUCCESS,
            data=LLMResponseData(
                content=content,
                raw_response=raw_response
            ),
            metadata=metadata
        )

    async def generate_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 3,
        **kwargs
    ) -> List[LLMResponse]:
        """
        Generate responses for multiple prompts concurrently.

        Args:
            prompts: List of user prompts
            system_prompt: System prompt for context
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional provider-specific parameters

        Returns:
            List of LLM responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_semaphore(prompt: str) -> LLMResponse:
            async with semaphore:
                return await self.generate_response(prompt, system_prompt, **kwargs)

        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=False)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get provider statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            'provider': self.provider.value,
            'model': self.config.model,
            'request_count': self._request_count,
            'total_tokens': self._total_tokens,
            'total_cost': self._total_cost,
            'cache_size': len(self._cache),
            'cache_enabled': self.config.enable_caching
        }

    def clear_cache(self):
        """Clear the provider's cache."""
        self._cache.clear()
        logger.info(f"Cleared cache for {self.provider} provider")

    async def close(self):
        """Close provider resources."""
        if hasattr(self._client, 'close'):
            await self._client.close()
        self._client = None
        logger.info(f"Closed {self.provider} provider")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client and hasattr(self._client, 'close'):
            asyncio.create_task(self.close())