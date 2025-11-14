"""
Query Understanding Service - Main orchestration service.

This module provides the main service that orchestrates all query understanding
components including intent analysis, keyword extraction, time parsing, and query expansion.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from .llm_providers.base_provider import BaseLLMProvider
from .llm_providers.openai_provider import OpenAIProvider
from .llm_providers.ollama_provider import OllamaProvider
from .llm_providers.mock_provider import MockProvider
from .query_processors.intent_analyzer import IntentAnalyzer
from .query_processors.keyword_extractor import KeywordExtractor
from .query_processors.time_parser import TimeParser
from .query_processors.query_expander import QueryExpander
from .query_processors.language_detector import LanguageDetector
from .models.query_intent import QueryIntent, QueryAnalysisRequest, QueryContext
from .models.search_query import ParsedQuery, QueryFilter
from .models.llm_response import LLMProvider, ResponseStatus

logger = logging.getLogger(__name__)


class QueryUnderstandingService:
    """
    Main service for query understanding and AI-powered search enhancement.

    Orchestrates multiple components to provide comprehensive query analysis
    including intent recognition, keyword extraction, time parsing, and query expansion.
    """

    def __init__(
        self,
        provider_type: LLMProvider = LLMProvider.MOCK,
        provider_config: Optional[Dict[str, Any]] = None,
        enable_caching: bool = True
    ):
        """
        Initialize query understanding service.

        Args:
            provider_type: LLM provider type (openai, ollama, mock)
            provider_config: Provider-specific configuration
            enable_caching: Whether to enable result caching
        """
        self.provider_type = provider_type
        self.enable_caching = enable_caching
        self._cache = {} if enable_caching else None
        self._provider = None
        self._processors = {}

        # Initialize components
        self._initialize_provider(provider_type, provider_config or {})
        self._initialize_processors()

        logger.info(f"Initialized QueryUnderstandingService with {provider_type} provider")

    def _initialize_provider(self, provider_type: LLMProvider, config: Dict[str, Any]):
        """Initialize the LLM provider."""
        try:
            if provider_type == LLMProvider.OPENAI:
                self._provider = OpenAIProvider(**config)
            elif provider_type == LLMProvider.OLLAMA:
                self._provider = OllamaProvider(**config)
            else:
                # Default to mock provider
                mock_config = {k: v for k, v in config.items() if k in ['model', 'temperature', 'max_tokens']}
                self._provider = MockProvider(**mock_config)

            logger.info(f"Initialized {provider_type} LLM provider")

        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {str(e)}")
            # Fallback to mock provider
            self._provider = MockProvider()
            self.provider_type = LLMProvider.MOCK
            logger.warning("Falling back to mock provider")

    def _initialize_processors(self):
        """Initialize query processing components."""
        if not self._provider:
            raise ValueError("LLM provider must be initialized first")

        self._processors = {
            'intent_analyzer': IntentAnalyzer(self._provider),
            'keyword_extractor': KeywordExtractor(self._provider),
            'time_parser': TimeParser(self._provider),
            'query_expander': QueryExpander(self._provider),
            'language_detector': LanguageDetector()
        }

        logger.info("Initialized all query processing components")

    async def understand_query(
        self,
        request: QueryAnalysisRequest
    ) -> Dict[str, Any]:
        """
        Perform comprehensive query understanding.

        Args:
            request: Query analysis request

        Returns:
            Complete query understanding result
        """
        start_time = datetime.now()
        query = request.query

        logger.info(f"Starting query understanding for: {query}")

        # Check cache first
        cache_key = self._generate_cache_key(query, request.options) if self.enable_caching else None
        if cache_key and cache_key in self._cache:
            logger.debug("Cache hit for query understanding")
            cached_result = self._cache[cache_key]
            cached_result['cached'] = True
            return cached_result

        try:
            # Initialize result structure
            result = {
                'original_query': query,
                'processing_time_ms': 0,
                'cached': False,
                'success': False,
                'error': None,
                'components': {}
            }

            # Step 1: Language detection (always performed)
            language_result = self._processors['language_detector'].detect_language(query)
            result['language'] = language_result['primary_language']
            result['language_confidence'] = language_result['confidence']
            result['is_mixed_language'] = language_result['is_mixed']

            # Step 2: Parallel processing of components
            tasks = []

            if request.analyze_intent:
                tasks.append(self._analyze_intent_with_retry(query, request.context, language_result['primary_language']))

            if request.extract_keywords:
                tasks.append(self._extract_keywords_with_retry(query, language_result['primary_language']))

            if request.parse_time:
                tasks.append(self._parse_time_with_retry(query, language_result['primary_language']))

            if request.expand_query:
                tasks.append(self._expand_query_with_retry(query, language_result['primary_language']))

            # Execute all tasks concurrently
            if tasks:
                component_results = await asyncio.gather(*tasks, return_exceptions=True)
                self._process_component_results(result, component_results, request)
            else:
                logger.warning("No analysis components enabled in request")

            # Step 3: Generate final parsed query
            result['parsed_query'] = self._create_parsed_query(query, result)

            # Step 4: Calculate processing time
            end_time = datetime.now()
            result['processing_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
            result['success'] = True

            # Cache result if enabled
            if cache_key and self.enable_caching:
                self._cache_result(cache_key, result)

            logger.info(f"Query understanding completed in {result['processing_time_ms']}ms")
            return result

        except Exception as e:
            logger.error(f"Query understanding failed: {str(e)}")
            end_time = datetime.now()
            return {
                'original_query': query,
                'processing_time_ms': int((end_time - start_time).total_seconds() * 1000),
                'cached': False,
                'success': False,
                'error': str(e),
                'components': {}
            }

    async def _analyze_intent_with_retry(self, query: str, context: Optional[QueryContext], language: str) -> QueryIntent:
        """Analyze query intent with retry logic."""
        try:
            return await self._processors['intent_analyzer'].analyze_intent(query, context.__dict__ if context else None)
        except Exception as e:
            logger.warning(f"Intent analysis failed: {str(e)}")
            # Return fallback intent
            from .models.query_intent import IntentType
            return QueryIntent(
                intent_type=IntentType.DOCUMENT_SEARCH,
                confidence=0.3,
                keywords=[],
                language=language
            )

    async def _extract_keywords_with_retry(self, query: str, language: str) -> Dict[str, Any]:
        """Extract keywords with retry logic."""
        try:
            return await self._processors['keyword_extractor'].extract_keywords(query, language)
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {str(e)}")
            return {'keywords': [], 'entities': {}, 'method': 'fallback'}

    async def _parse_time_with_retry(self, query: str, language: str) -> Optional[Dict[str, Any]]:
        """Parse time expressions with retry logic."""
        try:
            time_result = await self._processors['time_parser'].parse_time_expression(query, language)
            return time_result.__dict__ if time_result else None
        except Exception as e:
            logger.warning(f"Time parsing failed: {str(e)}")
            return None

    async def _expand_query_with_retry(self, query: str, language: str) -> Optional[Dict[str, Any]]:
        """Expand query with retry logic."""
        try:
            expansion_result = await self._processors['query_expander'].expand_query(query, language)
            return expansion_result.__dict__
        except Exception as e:
            logger.warning(f"Query expansion failed: {str(e)}")
            return None

    def _process_component_results(self, result: Dict[str, Any], component_results: List[Any], request: QueryAnalysisRequest):
        """Process results from component analysis."""
        component_names = []
        if request.analyze_intent:
            component_names.append('intent')
        if request.extract_keywords:
            component_names.append('keywords')
        if request.parse_time:
            component_names.append('time')
        if request.expand_query:
            component_names.append('expansion')

        for i, (component_name, component_result) in enumerate(zip(component_names, component_results)):
            if isinstance(component_result, Exception):
                logger.error(f"Component {component_name} failed: {str(component_result)}")
                result['components'][component_name] = {'error': str(component_result)}
            else:
                # Convert Pydantic models to dicts for JSON serialization
                if hasattr(component_result, 'dict'):
                    result['components'][component_name] = component_result.dict()
                elif hasattr(component_result, '__dict__'):
                    result['components'][component_name] = component_result.__dict__
                else:
                    result['components'][component_name] = component_result

    def _create_parsed_query(self, original_query: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create final parsed query from component results."""
        intent = result['components'].get('intent', {})
        keywords = result['components'].get('keywords', {})
        time_info = result['components'].get('time')
        expansion = result['components'].get('expansion', {})

        # Build search terms
        search_terms = []
        if keywords.get('keywords'):
            search_terms.extend(keywords['keywords'])
        if intent.get('keywords'):
            search_terms.extend(intent['keywords'])

        # Build filters
        filters = []
        if intent.get('file_types'):
            filters.append(QueryFilter(
                filter_type='file_type',
                value=intent['file_types'],
                operator='in',
                confidence=intent.get('confidence', 0.5)
            ))

        if time_info and time_info.get('start_date'):
            filters.append(QueryFilter(
                filter_type='date_range',
                value={
                    'start': time_info['start_date'],
                    'end': time_info.get('end_date', time_info['start_date'])
                },
                operator='range',
                confidence=time_info.get('confidence', 0.5)
            ))

        return {
            'original_query': original_query,
            'normalized_query': original_query.strip(),
            'expanded_query': expansion.get('synonyms', []) if expansion else [],
            'intent': intent,
            'search_terms': list(set(search_terms)),
            'filters': [f.__dict__ for f in filters],
            'language': result.get('language'),
            'confidence': min(
                intent.get('confidence', 0.5),
                keywords.get('method', '') == 'llm_based' and 0.8 or 0.5,
                time_info.get('confidence', 0.5) if time_info else 1.0,
                expansion.get('expansion_confidence', 0.5) if expansion else 1.0
            )
        }

    def _generate_cache_key(self, query: str, options: Dict[str, Any]) -> str:
        """Generate cache key for query."""
        import hashlib
        content = f"{query}:{str(sorted(options.items()))}"
        return hashlib.md5(content.encode()).hexdigest()

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache query understanding result."""
        if self._cache is not None and len(self._cache) < 1000:  # Limit cache size
            self._cache[cache_key] = result.copy()

    async def get_query_suggestions(self, query: str, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Get query suggestions based on AI analysis.

        Args:
            query: Original query
            max_suggestions: Maximum number of suggestions

        Returns:
            List of query suggestions
        """
        if not self._provider:
            return []

        try:
            system_prompt = f"""
你是一个查询建议专家。请为用户的查询提供5个以内的相关建议，帮助用户更好地表达搜索意图。

建议类型：
1. completion: 查询补全
2. correction: 查询纠正
3. expansion: 查询扩展
4. related: 相关查询

请以JSON格式返回：
{{
    "suggestions": [
        {{"text": "建议查询1", "type": "completion", "score": 0.9, "reason": "基于常见查询模式"}},
        {{"text": "建议查询2", "type": "correction", "score": 0.8, "reason": "可能的拼写纠正"}},
        {{"text": "建议查询3", "type": "expansion", "score": 0.7, "reason": "添加相关术语"}},
        {{"text": "建议查询4", "type": "related", "score": 0.6, "reason": "相关主题"}}
    ]
}}
"""

            response = await self._provider.generate_response(
                prompt=f"请为以下查询提供建议：{query}",
                system_prompt=system_prompt
            )

            if response.is_successful and response.content:
                import json
                result_data = json.loads(response.content)
                suggestions = result_data.get('suggestions', [])
                return suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"Failed to get query suggestions: {str(e)}")

        return []

    async def test_provider_connection(self) -> bool:
        """
        Test connection to the LLM provider.

        Returns:
            True if connection is successful
        """
        if not self._provider:
            return False

        try:
            return await self._provider.test_connection()
        except Exception as e:
            logger.error(f"Provider connection test failed: {str(e)}")
            return False

    def get_service_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive service statistics.

        Returns:
            Service statistics dictionary
        """
        stats = {
            'provider_type': self.provider_type.value,
            'provider_available': self._provider is not None,
            'caching_enabled': self.enable_caching,
            'cache_size': len(self._cache) if self._cache else 0,
            'components': {}
        }

        # Get component statistics
        for name, processor in self._processors.items():
            if hasattr(processor, 'get_statistics'):
                stats['components'][name] = processor.get_statistics()
            elif hasattr(processor, f'get_{name.replace("_analyzer", "").replace("_extractor", "").replace("_parser", "").replace("_expander", "")}_statistics'):
                method_name = f'get_{name.replace("_analyzer", "").replace("_extractor", "").replace("_parser", "").replace("_expander", "")}_statistics'
                if hasattr(processor, method_name):
                    stats['components'][name] = getattr(processor, method_name)()

        # Provider statistics
        if self._provider:
            stats['provider_statistics'] = self._provider.get_statistics()

        return stats

    def clear_cache(self):
        """Clear the service cache."""
        if self._cache is not None:
            self._cache.clear()
            logger.info("Cleared query understanding cache")

    async def close(self):
        """Close the service and release resources."""
        if self._provider:
            await self._provider.close()
            self._provider = None

        self._processors.clear()
        if self._cache is not None:
            self._cache.clear()

        logger.info("Closed QueryUnderstandingService")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()