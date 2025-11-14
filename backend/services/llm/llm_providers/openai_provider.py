"""
OpenAI Provider - Implementation of LLM provider for OpenAI GPT models.

This module provides integration with OpenAI's API, supporting GPT-4, GPT-3.5-turbo,
and other OpenAI models for query understanding and text generation.
"""

import os
import logging
from typing import Dict, Any, Optional

import openai
from openai import AsyncOpenAI

from .base_provider import BaseLLMProvider, LLMConfig
from ..models.llm_response import (
    LLMProvider,
    LLMErrorInfo,
    ResponseStatus
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.

    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models through
    their official API with proper error handling and retry logic.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        max_tokens: int = 500,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Custom API base URL
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        config = LLMConfig(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            cost_per_token=self._get_model_cost(model),
            **kwargs
        )

        super().__init__(config, LLMProvider.OPENAI)

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url

        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self._async_client = None

    def _get_model_cost(self, model: str) -> float:
        """Get cost per token for the model (approximate USD)."""
        costs = {
            "gpt-4": 0.00003,      # ~$0.03 per 1K tokens
            "gpt-4-32k": 0.00006,
            "gpt-3.5-turbo": 0.000002,  # ~$0.002 per 1K tokens
            "gpt-3.5-turbo-16k": 0.000003,
            "gpt-3.5-turbo-instruct": 0.000002,
        }
        return costs.get(model, 0.000002)  # Default to 3.5-turbo pricing

    async def _initialize_client(self) -> AsyncOpenAI:
        """Initialize OpenAI async client."""
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self._async_client = AsyncOpenAI(**client_kwargs)
        logger.info(f"Initialized OpenAI client with model: {self.config.model}")
        return self._async_client

    async def _generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using OpenAI's chat completion API.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            Raw response from OpenAI API
        """
        client = await self._get_client()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare request parameters
        request_params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs
        }

        # Remove None values from request params
        request_params = {k: v for k, v in request_params.items() if v is not None}

        logger.debug(f"Sending request to OpenAI with model: {self.config.model}")

        try:
            response = await client.chat.completions.create(**request_params)
            return response.model_dump()
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {str(e)}")
            raise
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI request: {str(e)}")
            raise

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from OpenAI response.

        Args:
            response: Raw response from OpenAI

        Returns:
            Extracted text content
        """
        try:
            choices = response.get("choices", [])
            if not choices:
                raise ValueError("No choices in OpenAI response")

            message = choices[0].get("message", {})
            content = message.get("content", "")

            if not content:
                raise ValueError("No content in OpenAI response")

            return content.strip()
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting content from OpenAI response: {str(e)}")
            raise ValueError(f"Failed to extract content: {str(e)}")

    def _extract_usage_info(self, response: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract usage information from OpenAI response.

        Args:
            response: Raw response from OpenAI

        Returns:
            Dictionary with token usage information
        """
        try:
            usage = response.get("usage", {})
            return {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting usage info from OpenAI response: {str(e)}")
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _extract_error_info(self, error: Exception) -> LLMErrorInfo:
        """
        Extract error information from OpenAI exception.

        Args:
            error: OpenAI-specific exception

        Returns:
            Standardized error information
        """
        error_message = str(error)
        error_type = type(error).__name__
        error_code = None
        is_recoverable = False

        if isinstance(error, openai.RateLimitError):
            error_type = "rate_limit"
            error_code = "rate_limit_exceeded"
            is_recoverable = True
        elif isinstance(error, openai.AuthenticationError):
            error_type = "authentication"
            error_code = "invalid_api_key"
            is_recoverable = False
        elif isinstance(error, openai.APIError):
            error_type = "api_error"
            if "insufficient_quota" in error_message.lower():
                error_code = "insufficient_quota"
                is_recoverable = False
            else:
                is_recoverable = True
        elif isinstance(error, openai.APIConnectionError):
            error_type = "connection_error"
            is_recoverable = True
        elif isinstance(error, TimeoutError):
            error_type = "timeout"
            is_recoverable = True

        return LLMErrorInfo(
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            is_recoverable=is_recoverable
        )

    async def test_connection(self) -> bool:
        """
        Test connection to OpenAI API.

        Returns:
            True if connection is successful
        """
        try:
            client = await self._get_client()
            # Simple test request
            response = await client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("OpenAI connection test successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Model information dictionary
        """
        model_info = {
            "provider": "openai",
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "supports_system_messages": True,
            "supports_streaming": True,
            "cost_per_token": self.config.cost_per_token
        }

        # Add model-specific information
        if "gpt-4" in self.config.model:
            model_info.update({
                "context_window": 8192 if "32k" not in self.config.model else 32768,
                "training_cutoff": "2021-09",
                "description": "GPT-4: Most capable model, good for complex reasoning"
            })
        elif "gpt-3.5-turbo" in self.config.model:
            model_info.update({
                "context_window": 4096 if "16k" not in self.config.model else 16384,
                "training_cutoff": "2021-09",
                "description": "GPT-3.5-turbo: Fast and cost-effective model"
            })

        return model_info

    async def close(self):
        """Close OpenAI client resources."""
        if self._async_client:
            await self._async_client.close()
            self._async_client = None
        await super().close()