"""
Keyword Extractor - Query keyword extraction component.

This module provides intelligent keyword and entity extraction from user queries,
supporting both rule-based and LLM-powered approaches for accurate term identification.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Set
import json

from ..llm_providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    Keyword and entity extractor using combined NLP approaches.

    Extracts meaningful keywords, entities, and concepts from user queries
    to improve search relevance and understanding.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize keyword extractor.

        Args:
            llm_provider: LLM provider for advanced analysis
        """
        self.llm_provider = llm_provider

        # Common stop words (Chinese and English)
        self.stop_words = {
            'zh': {
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很',
                '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它',
                '想要', '帮我', '寻找', '查找', '搜索', '找', '给', '把', '被', '从', '为', '对', '向', '跟', '与'
            },
            'en': {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'must', 'i', 'you', 'he',
                'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its',
                'our', 'their', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'when', 'where',
                'why', 'how', 'find', 'search', 'look', 'get', 'show', 'give', 'want', 'need', 'help'
            }
        }

        # Domain-specific keyword patterns
        self.domain_patterns = {
            'file_types': [
                r'\b(pdf|doc|docx|txt|rtf|odt|xls|xlsx|ppt|pptx|csv|html|xml|json)\b',
                r'\b(jpg|jpeg|png|gif|bmp|tiff|svg|webp|ico)\b',
                r'\b(mp3|wav|flac|aac|ogg|wma|m4a|mp4|avi|mkv|mov|wmv|flv|webm)\b'
            ],
            'technical_terms': [
                r'\b(api|sdk|framework|library|database|algorithm|function|method|class|object)\b',
                r'\b(server|client|frontend|backend|database|cache|queue|middleware)\b',
                r'\b(机器学习|深度学习|神经网络|算法|数据结构|编程|开发)\b'
            ],
            'business_terms': [
                r'\b(report|proposal|contract|invoice|budget|schedule|meeting|presentation)\b',
                r'\b(报告|提案|合同|发票|预算|计划|会议|演示|项目)\b'
            ]
        }

        # Entity patterns
        self.entity_patterns = {
            'dates': [
                r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?',
                r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
                r'(今天|昨天|前天|明天|后天|本周|上周|下周|本月|上月|下月|今年|去年|明年)'
            ],
            'numbers': [
                r'\b\d+(\.\d+)?\b',
                r'\b第[一二三四五六七八九十\d]+[个批次期章节部分]\b'
            ],
            'organizations': [
                r'\b([A-Z][a-z]+\s?)+(Inc|Corp|LLC|Ltd|Co|Company|集团|公司|有限)\b'
            ]
        }

    async def extract_keywords(
        self,
        query: str,
        language: Optional[str] = None,
        max_keywords: int = 10
    ) -> Dict[str, Any]:
        """
        Extract keywords and entities from the query.

        Args:
            query: User query string
            language: Language hint (zh, en, mixed)
            max_keywords: Maximum number of keywords to return

        Returns:
            Dictionary with extracted keywords and metadata
        """
        logger.debug(f"Extracting keywords from query: {query}")

        # Detect language if not provided
        if not language:
            language = self._detect_language(query)

        # Step 1: Rule-based extraction
        rule_based_result = self._rule_based_extraction(query, language)

        # Step 2: LLM-based extraction for complex queries
        if len(query.split()) > 5 or self._is_complex_query(query):
            try:
                llm_result = await self._llm_extraction(query, language)
                # Combine results
                return self._combine_extraction_results(rule_based_result, llm_result, max_keywords)
            except Exception as e:
                logger.warning(f"LLM keyword extraction failed: {str(e)}, using rule-based result")
                return rule_based_result
        else:
            return rule_based_result

    def _rule_based_extraction(self, query: str, language: str) -> Dict[str, Any]:
        """
        Perform rule-based keyword extraction.

        Args:
            query: User query string
            language: Query language

        Returns:
            Dictionary with extracted keywords
        """
        # Normalize query
        normalized_query = query.lower()

        # Extract tokens
        tokens = self._tokenize_query(normalized_query, language)

        # Remove stop words
        filtered_tokens = self._remove_stop_words(tokens, language)

        # Extract domain-specific terms
        domain_keywords = self._extract_domain_keywords(normalized_query)

        # Extract entities
        entities = self._extract_entities(query)

        # Calculate keyword scores
        keyword_scores = self._calculate_keyword_scores(filtered_tokens, domain_keywords)

        # Select top keywords
        top_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            'keywords': [kw for kw, score in top_keywords],
            'keyword_scores': dict(top_keywords),
            'entities': entities,
            'domain_keywords': domain_keywords,
            'language': language,
            'method': 'rule_based'
        }

    async def _llm_extraction(self, query: str, language: str) -> Dict[str, Any]:
        """
        Perform LLM-based keyword extraction.

        Args:
            query: User query string
            language: Query language

        Returns:
            Dictionary with LLM-extracted keywords
        """
        system_prompt = f"""
你是一个关键词提取专家。请从用户的查询中提取最重要的关键词和实体。

要求：
1. 提取核心关键词（5-10个）
2. 识别命名实体（人名、地名、机构名、时间等）
3. 识别专业术语和领域词汇
4. 计算关键词重要性评分（0.0-1.0）
5. 识别查询类型和意图

查询语言：{language}

请以JSON格式返回结果：
{{
    "keywords": [
        {{"keyword": "产品设计", "score": 0.95, "type": "domain"}},
        {{"keyword": "PPT", "score": 0.90, "type": "file_type"}},
        {{"keyword": "上周", "score": 0.85, "type": "time"}}
    ],
    "entities": {{
        "time": ["上周"],
        "file_type": ["PPT"],
        "domain": ["产品设计"]
    }},
    "query_type": "document_search",
    "importance_scores": {{
        "产品设计": 0.95,
        "PPT": 0.90,
        "上周": 0.85
    }}
}}
"""

        try:
            response = await self.llm_provider.generate_response(
                prompt=f"请从以下查询中提取关键词和实体：\n\n查询：{query}",
                system_prompt=system_prompt
            )

            if response.is_successful and response.content:
                # Parse JSON response
                try:
                    result_data = json.loads(response.content)
                    result_data['method'] = 'llm_based'
                    return result_data
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM keyword response as JSON: {str(e)}")
                    return self._parse_llm_text_keywords(response.content)

        except Exception as e:
            logger.error(f"LLM keyword extraction failed: {str(e)}")

        # Fallback to rule-based extraction
        return self._rule_based_extraction(query, language)

    def _parse_llm_text_keywords(self, content: str) -> Dict[str, Any]:
        """
        Parse text-based LLM response when JSON parsing fails.

        Args:
            content: LLM response content

        Returns:
            Parsed keyword extraction result
        """
        # Simple word extraction from text
        words = re.findall(r'\b\w+\b', content.lower())
        return {
            'keywords': words[:10],
            'keyword_scores': {word: 0.7 for word in words[:10]},
            'entities': {},
            'method': 'llm_text_fallback'
        }

    def _combine_extraction_results(
        self,
        rule_based: Dict[str, Any],
        llm_based: Dict[str, Any],
        max_keywords: int
    ) -> Dict[str, Any]:
        """
        Combine results from rule-based and LLM extraction.

        Args:
            rule_based: Rule-based extraction result
            llm_based: LLM-based extraction result
            max_keywords: Maximum keywords to return

        Returns:
            Combined extraction result
        """
        # Combine keyword scores
        combined_scores = {}

        # Add rule-based scores
        for keyword, score in rule_based.get('keyword_scores', {}).items():
            combined_scores[keyword] = score * 0.7  # Weight rule-based results

        # Add LLM-based scores
        for keyword_data in llm_based.get('keywords', []):
            if isinstance(keyword_data, dict):
                keyword = keyword_data.get('keyword')
                score = keyword_data.get('score', 0.5)
            else:
                keyword = keyword_data
                score = 0.5

            if keyword in combined_scores:
                combined_scores[keyword] = max(combined_scores[keyword], score)
            else:
                combined_scores[keyword] = score

        # Sort by score and limit
        sorted_keywords = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_keywords = sorted_keywords[:max_keywords]

        # Combine entities
        combined_entities = {**rule_based.get('entities', {}), **llm_based.get('entities', {})}

        return {
            'keywords': [kw for kw, score in top_keywords],
            'keyword_scores': dict(top_keywords),
            'entities': combined_entities,
            'domain_keywords': list(set(
                rule_based.get('domain_keywords', []) +
                [kw.get('keyword') for kw in llm_based.get('keywords', []) if isinstance(kw, dict) and kw.get('type') == 'domain']
            )),
            'language': rule_based.get('language') or llm_based.get('language'),
            'method': 'combined'
        }

    def _tokenize_query(self, query: str, language: str) -> List[str]:
        """
        Tokenize the query based on language.

        Args:
            query: Query string
            language: Language code

        Returns:
            List of tokens
        """
        if language == 'zh':
            # Simple Chinese tokenization (could use jieba in production)
            tokens = []
            for char in query:
                if char.strip():
                    # Handle multi-character words
                    if len(tokens) > 0 and len(tokens[-1]) == 1 and self._is_chinese_char(char):
                        tokens[-1] += char
                    else:
                        tokens.append(char)
            return tokens
        else:
            # English tokenization
            return re.findall(r'\b\w+\b', query)

    def _is_chinese_char(self, char: str) -> bool:
        """Check if character is Chinese."""
        return '\u4e00' <= char <= '\u9fff'

    def _remove_stop_words(self, tokens: List[str], language: str) -> List[str]:
        """
        Remove stop words from tokens.

        Args:
            tokens: List of tokens
            language: Language code

        Returns:
            Filtered tokens
        """
        stop_words = set()
        if language in ['zh', 'mixed']:
            stop_words.update(self.stop_words['zh'])
        if language in ['en', 'mixed']:
            stop_words.update(self.stop_words['en'])

        return [token for token in tokens if token.lower() not in stop_words and len(token) > 1]

    def _extract_domain_keywords(self, query: str) -> List[str]:
        """
        Extract domain-specific keywords.

        Args:
            query: Query string

        Returns:
            List of domain keywords
        """
        domain_keywords = []

        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                domain_keywords.extend(matches)

        return list(set(domain_keywords))

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the query.

        Args:
            query: Query string

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, query)
                matches.extend(found)

            if matches:
                entities[entity_type] = matches

        return entities

    def _calculate_keyword_scores(
        self,
        tokens: List[str],
        domain_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Calculate importance scores for keywords.

        Args:
            tokens: Filtered tokens
            domain_keywords: Domain-specific keywords

        Returns:
            Dictionary of keyword scores
        """
        scores = {}

        # Count token frequencies
        token_counts = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        # Calculate base scores
        total_tokens = len(tokens)
        for token, count in token_counts.items():
            base_score = count / total_tokens

            # Boost domain keywords
            if token in domain_keywords:
                base_score *= 1.5

            # Boost longer tokens
            if len(token) > 2:
                base_score *= 1.2

            scores[token] = min(base_score, 1.0)

        return scores

    def _detect_language(self, query: str) -> str:
        """
        Detect query language.

        Args:
            query: Query string

        Returns:
            Language code
        """
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', query))
        total_chars = len(query.replace(' ', '').replace('\n', ''))

        if total_chars == 0:
            return 'en'

        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.4:
            return 'zh'
        elif chinese_ratio < 0.1:
            return 'en'
        else:
            return 'mixed'

    def _is_complex_query(self, query: str) -> bool:
        """
        Determine if query is complex enough for LLM analysis.

        Args:
            query: Query string

        Returns:
            True if query is complex
        """
        # Consider complex if:
        # - Has question words
        # - Has multiple clauses
        # - Has logical connectors
        complex_indicators = [
            r'(什么|如何|为什么|哪里|哪个|怎么)',
            r'(what|how|why|where|which|when)',
            r'(并且|或者|但是|不过|而且|同时)',
            r'(and|or|but|however|also|meanwhile)'
        ]

        for indicator in complex_indicators:
            if re.search(indicator, query, re.IGNORECASE):
                return True

        return len(query.split()) > 8

    def get_extraction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about keyword extraction performance.

        Returns:
            Extraction statistics
        """
        return {
            'supported_languages': list(self.stop_words.keys()),
            'domain_patterns_count': sum(len(patterns) for patterns in self.domain_patterns.values()),
            'entity_patterns_count': sum(len(patterns) for patterns in self.entity_patterns.values()),
            'llm_provider': self.llm_provider.provider.value if self.llm_provider else None
        }