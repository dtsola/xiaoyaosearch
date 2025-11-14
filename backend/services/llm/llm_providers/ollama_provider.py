"""
Ollama Provider - Implementation of LLM provider for local Ollama models.

This module provides integration with Ollama, enabling local execution of
LLM models like Llama2, Qwen, and other open-source models for
privacy-first query understanding and text generation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
import asyncio

from .base_provider import BaseLLMProvider, LLMConfig
from ..models.llm_response import (
    LLMProvider,
    LLMErrorInfo,
    ResponseStatus
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM provider implementation.

    Supports local execution of various open-source models through
    Ollama's HTTP API with model management and proper error handling.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "llama2",
        temperature: float = 0.1,
        max_tokens: int = 500,
        timeout: int = 60,  # Longer timeout for local models
        **kwargs
    ):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama server URL (defaults to http://localhost:11434)
            model: Model name (llama2, qwen, mistral, etc.)
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
            cost_per_token=0.0,  # Local models are free
            **kwargs
        )

        super().__init__(config, LLMProvider.OLLAMA)

        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self._http_client = None

    async def _initialize_client(self) -> httpx.AsyncClient:
        """Initialize HTTP client for Ollama API."""
        self._http_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.config.timeout
        )
        logger.info(f"Initialized Ollama client at {self.base_url} with model: {self.config.model}")
        return self._http_client

    async def _ensure_model_available(self) -> bool:
        """
        Ensure the model is available locally or download it.

        Returns:
            True if model is available
        """
        try:
            client = await self._get_client()

            # Check if model is available
            response = await client.get("/api/tags")
            models_data = response.json()

            available_models = [model["name"] for model in models_data.get("models", [])]

            if self.config.model in available_models:
                logger.info(f"Model {self.config.model} is available locally")
                return True

            # Model not available, try to pull it
            logger.info(f"Model {self.config.model} not found locally. Attempting to pull...")
            pull_response = await client.post(
                "/api/pull",
                json={"name": self.config.model}
            )

            if pull_response.status_code == 200:
                logger.info(f"Successfully pulled model {self.config.model}")
                return True
            else:
                logger.error(f"Failed to pull model {self.config.model}")
                return False

        except Exception as e:
            logger.error(f"Error ensuring model availability: {str(e)}")
            return False

    async def _generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using Ollama's generate API.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional Ollama-specific parameters

        Returns:
            Raw response from Ollama API
        """
        client = await self._get_client()

        # Ensure model is available
        if not await self._ensure_model_available():
            raise ValueError(f"Model {self.config.model} is not available and could not be pulled")

        # Build the request
        request_data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }

        # Add system prompt if provided
        if system_prompt:
            request_data["system"] = system_prompt

        # Merge additional options
        additional_options = kwargs.get("options", {})
        request_data["options"].update(additional_options)

        # Remove None values
        request_data["options"] = {k: v for k, v in request_data["options"].items() if v is not None}

        logger.debug(f"Sending request to Ollama with model: {self.config.model}")

        try:
            response = await client.post("/api/generate", json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ollama request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama request: {str(e)}")
            raise

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from Ollama response.

        Args:
            response: Raw response from Ollama

        Returns:
            Extracted text content
        """
        try:
            content = response.get("response", "")
            if not content:
                raise ValueError("No response content in Ollama response")

            return content.strip()
        except (KeyError, TypeError) as e:
            logger.error(f"Error extracting content from Ollama response: {str(e)}")
            raise ValueError(f"Failed to extract content: {str(e)}")

    def _extract_usage_info(self, response: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract usage information from Ollama response.

        Args:
            response: Raw response from Ollama

        Returns:
            Dictionary with token usage information
        """
        try:
            # Ollama provides prompt_eval_count and eval_count
            return {
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0),
                "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
            }
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting usage info from Ollama response: {str(e)}")
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _extract_error_info(self, error: Exception) -> LLMErrorInfo:
        """
        Extract error information from Ollama exception.

        Args:
            error: Ollama-specific exception

        Returns:
            Standardized error information
        """
        error_message = str(error)
        error_type = type(error).__name__
        error_code = None
        is_recoverable = False

        if isinstance(error, httpx.HTTPStatusError):
            error_type = "http_error"
            error_code = str(error.response.status_code)
            if error.response.status_code == 404:
                error_type = "model_not_found"
                is_recoverable = False
            elif error.response.status_code >= 500:
                is_recoverable = True
        elif isinstance(error, httpx.RequestError):
            error_type = "connection_error"
            is_recoverable = True
        elif isinstance(error, TimeoutError):
            error_type = "timeout"
            is_recoverable = True
        elif "model not found" in error_message.lower():
            error_type = "model_not_found"
            is_recoverable = False

        return LLMErrorInfo(
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            is_recoverable=is_recoverable
        )

    async def test_connection(self) -> bool:
        """
        Test connection to Ollama server.

        Returns:
            True if connection is successful
        """
        try:
            client = await self._get_client()

            # Test with version endpoint
            response = await client.get("/api/version")
            if response.status_code == 200:
                version = response.json().get("version", "unknown")
                logger.info(f"Ollama connection test successful, version: {version}")

                # Also test model availability
                model_available = await self._ensure_model_available()
                return model_available
            else:
                logger.error(f"Ollama version check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ollama connection test failed: {str(e)}")
            return False

    async def list_available_models(self) -> List[str]:
        """
        List available models on the Ollama server.

        Returns:
            List of available model names
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")

            if response.status_code == 200:
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]
                logger.info(f"Found {len(models)} available models")
                return models
            else:
                logger.error(f"Failed to list models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {str(e)}")
            return []

    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from the Ollama registry.

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful
        """
        try:
            client = await self._get_client()
            logger.info(f"Pulling model: {model_name}")

            response = await client.post("/api/pull", json={"name": model_name})

            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Model information dictionary
        """
        return {
            "provider": "ollama",
            "model": self.config.model,
            "base_url": self.base_url,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "supports_system_messages": True,
            "supports_streaming": True,
            "cost_per_token": 0.0,
            "local_execution": True,
            "privacy_friendly": True,
            "description": "Local model via Ollama - privacy-first with no external API calls"
        }

    async def close(self):
        """Close Ollama client resources."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        await super().close()