"""
Mock Provider - Implementation of LLM provider for testing and development.

This module provides a mock LLM provider that generates predictable responses
for testing purposes without requiring actual API calls to external services.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from .base_provider import BaseLLMProvider, LLMConfig
from ..models.llm_response import (
    LLMProvider,
    LLMErrorInfo,
    ResponseStatus
)

logger = logging.getLogger(__name__)


class MockProvider(BaseLLMProvider):
    """
    Mock LLM provider implementation for testing.

    Generates predictable responses based on pattern matching and heuristics.
    Useful for unit tests, development, and when external LLM services are unavailable.
    """

    def __init__(
        self,
        model: str = "mock-gpt-3.5-turbo",
        temperature: float = 0.1,
        max_tokens: int = 500,
        response_delay: float = 0.1,  # Simulate API latency
        error_rate: float = 0.0,  # Simulate occasional errors
        **kwargs
    ):
        """
        Initialize Mock provider.

        Args:
            model: Mock model name
            temperature: Response randomness (simulated)
            max_tokens: Maximum tokens in response (simulated)
            response_delay: Delay to simulate API latency (seconds)
            error_rate: Probability of simulated errors (0.0-1.0)
            **kwargs: Additional configuration
        """
        config = LLMConfig(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            cost_per_token=0.0,
            **kwargs
        )

        super().__init__(config, LLMProvider.MOCK)

        self.response_delay = response_delay
        self.error_rate = error_rate
        self._response_counter = 0

    async def _initialize_client(self) -> None:
        """Mock client initialization (no actual client needed)."""
        logger.info(f"Initialized Mock provider with model: {self.config.model}")
        return None

    async def _generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate mock completion based on pattern matching.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional parameters (ignored in mock)

        Returns:
            Mock response data
        """
        # Simulate API delay
        if self.response_delay > 0:
            await asyncio.sleep(self.response_delay)

        # Simulate occasional errors
        import random
        if random.random() < self.error_rate:
            raise Exception("Simulated API error for testing")

        self._response_counter += 1

        # Generate mock response based on prompt patterns
        content = self._generate_mock_content(prompt, system_prompt)

        # Simulate token usage
        prompt_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)
        completion_tokens = len(content.split())
        total_tokens = prompt_tokens + completion_tokens

        return {
            "id": f"mock-response-{self._response_counter}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": self.config.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }

    def _generate_mock_content(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Generate mock content based on prompt analysis.

        Args:
            prompt: User prompt
            system_prompt: System prompt

        Returns:
            Generated mock content
        """
        prompt_lower = prompt.lower()

        # Query understanding patterns
        if "查询理解" in prompt_lower or "query understanding" in prompt_lower:
            return self._generate_query_understanding_response(prompt)
        elif "意图分析" in prompt_lower or "intent analysis" in prompt_lower:
            return self._generate_intent_analysis_response(prompt)
        elif "关键词提取" in prompt_lower or "keyword extraction" in prompt_lower:
            return self._generate_keyword_extraction_response(prompt)
        elif "时间解析" in prompt_lower or "time parsing" in prompt_lower:
            return self._generate_time_parsing_response(prompt)
        elif "查询扩展" in prompt_lower or "query expansion" in prompt_lower:
            return self._generate_query_expansion_response(prompt)

        # Default mock response
        return self._generate_default_response(prompt)

    def _generate_query_understanding_response(self, prompt: str) -> str:
        """Generate mock query understanding response."""
        return json.dumps({
            "intent": "document_search",
            "confidence": 0.95,
            "keywords": ["文档", "文件", "搜索"],
            "entities": {
                "file_type": ["pdf", "doc", "txt"],
                "time_range": ["最近一周"]
            },
            "time_range": {
                "start": "2024-11-07",
                "end": "2024-11-14"
            },
            "file_types": ["pdf", "docx"],
            "language": "zh",
            "semantic_description": "用户想要搜索文档文件"
        }, ensure_ascii=False)

    def _generate_intent_analysis_response(self, prompt: str) -> str:
        """Generate mock intent analysis response."""
        if "ppt" in prompt.lower() or "powerpoint" in prompt.lower():
            return json.dumps({
                "intent": "document_search",
                "confidence": 0.9,
                "file_types": ["ppt", "pptx"],
                "description": "搜索演示文稿文件"
            }, ensure_ascii=False)
        elif "图片" in prompt or "image" in prompt.lower():
            return json.dumps({
                "intent": "image_search",
                "confidence": 0.85,
                "file_types": ["jpg", "png", "gif"],
                "description": "搜索图片文件"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "intent": "document_search",
                "confidence": 0.8,
                "description": "一般文档搜索"
            }, ensure_ascii=False)

    def _generate_keyword_extraction_response(self, prompt: str) -> str:
        """Generate mock keyword extraction response."""
        # Extract potential keywords from the prompt
        words = re.findall(r'\b[\w\u4e00-\u9fff]+\b', prompt)
        keywords = [word for word in words if len(word) > 1][:5]  # Top 5 keywords

        return json.dumps({
            "keywords": keywords,
            "confidence": 0.88,
            "entities": {},
            "important_terms": keywords[:3]
        }, ensure_ascii=False)

    def _generate_time_parsing_response(self, prompt: str) -> str:
        """Generate mock time parsing response."""
        now = datetime.now()
        time_mapping = {
            "今天": now,
            "昨天": now - timedelta(days=1),
            "上周": now - timedelta(weeks=1),
            "最近一周": now - timedelta(days=7),
            "最近一月": now - timedelta(days=30),
            "today": now,
            "yesterday": now - timedelta(days=1),
            "last week": now - timedelta(weeks=1),
            "recent week": now - timedelta(days=7),
            "recent month": now - timedelta(days=30)
        }

        detected_time = None
        for expression, time_obj in time_mapping.items():
            if expression in prompt.lower():
                detected_time = time_obj
                break

        if detected_time:
            return json.dumps({
                "time_range": {
                    "start": detected_time.strftime("%Y-%m-%d"),
                    "end": now.strftime("%Y-%m-%d")
                },
                "confidence": 0.9,
                "expression": expression
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "time_range": None,
                "confidence": 0.0,
                "message": "未检测到时间表达式"
            }, ensure_ascii=False)

    def _generate_query_expansion_response(self, prompt: str) -> str:
        """Generate mock query expansion response."""
        # Simple synonym mapping
        synonym_mapping = {
            "文档": ["文件", "资料", "材料"],
            "图片": ["图像", "照片", "影像"],
            "搜索": ["查找", "检索", "寻找"],
            "document": ["file", "paper", "material"],
            "image": ["picture", "photo", "graphic"],
            "search": ["find", "lookup", "retrieve"]
        }

        synonyms = []
        related_terms = []

        for term, term_synonyms in synonym_mapping.items():
            if term in prompt.lower():
                synonyms.extend(term_synonyms)
                related_terms.append(term + "相关")

        return json.dumps({
            "expanded_query": prompt + " " + " ".join(synonyms[:3]),
            "synonyms": synonyms[:5],
            "related_terms": related_terms[:3],
            "confidence": 0.85
        }, ensure_ascii=False)

    def _generate_default_response(self, prompt: str) -> str:
        """Generate default mock response."""
        responses = [
            "这是一个模拟的LLM响应，用于测试和开发目的。",
            "我理解了您的查询，这是一个测试响应。",
            "作为模拟模型，我可以为您提供基本的查询分析功能。",
            "这是一个预设的响应，用于验证系统功能。"
        ]

        import random
        return random.choice(responses)

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from mock response.

        Args:
            response: Mock response

        Returns:
            Extracted content
        """
        try:
            choices = response.get("choices", [])
            if not choices:
                raise ValueError("No choices in mock response")

            message = choices[0].get("message", {})
            content = message.get("content", "")

            if not content:
                raise ValueError("No content in mock response")

            return content
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting content from mock response: {str(e)}")
            raise ValueError(f"Failed to extract content: {str(e)}")

    def _extract_usage_info(self, response: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract usage information from mock response.

        Args:
            response: Mock response

        Returns:
            Token usage information
        """
        try:
            usage = response.get("usage", {})
            return {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting usage info from mock response: {str(e)}")
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _extract_error_info(self, error: Exception) -> LLMErrorInfo:
        """
        Extract error information from mock exception.

        Args:
            error: Mock exception

        Returns:
            Standardized error information
        """
        error_message = str(error)
        error_type = type(error).__name__

        # Determine if error is recoverable
        is_recoverable = not "authentication" in error_message.lower()

        return LLMErrorInfo(
            error_type=error_type,
            error_message=error_message,
            is_recoverable=is_recoverable
        )

    async def test_connection(self) -> bool:
        """
        Test connection to mock provider (always successful).

        Returns:
            Always True for mock provider
        """
        logger.info("Mock provider connection test successful")
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the mock model.

        Returns:
            Mock model information
        """
        return {
            "provider": "mock",
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "supports_system_messages": True,
            "supports_streaming": False,
            "cost_per_token": 0.0,
            "response_delay": self.response_delay,
            "error_rate": self.error_rate,
            "description": "Mock provider for testing and development - predictable responses without API calls"
        }

    def set_response_delay(self, delay: float):
        """Set response delay for testing."""
        self.response_delay = delay
        logger.info(f"Set mock response delay to {delay} seconds")

    def set_error_rate(self, rate: float):
        """Set error rate for testing."""
        if not 0.0 <= rate <= 1.0:
            raise ValueError("Error rate must be between 0.0 and 1.0")
        self.error_rate = rate
        logger.info(f"Set mock error rate to {rate}")

    async def close(self):
        """Close mock provider resources (nothing to clean up)."""
        logger.info("Closed Mock provider")
        await super().close()