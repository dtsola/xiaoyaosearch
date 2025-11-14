"""
Intent Analyzer - Query intent analysis component.

This module provides intelligent analysis of user query intents,
classifying search queries into document, image, audio, video,
or mixed search types with confidence scoring.
"""

import re
import logging
from typing import Dict, Any, Optional, List
import json

from ..models.query_intent import QueryIntent, IntentType
from ..llm_providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class IntentAnalyzer:
    """
    Query intent analyzer using both rule-based and LLM-based approaches.

    Combines fast pattern matching with LLM-powered analysis for
    accurate intent classification and understanding.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize intent analyzer.

        Args:
            llm_provider: LLM provider for advanced analysis
        """
        self.llm_provider = llm_provider

        # Intent detection patterns (Chinese and English)
        self.intent_patterns = {
            IntentType.DOCUMENT_SEARCH: [
                r'\b(文档|文件|资料|材料|文本|pdf|doc|txt|word|excel)\b',
                r'\b(document|file|text|pdf|doc|word|excel|paper|article)\b',
                r'\b(报告|论文|合同|方案|计划|总结)\b',
                r'\b(report|paper|contract|proposal|plan|summary)\b'
            ],
            IntentType.IMAGE_SEARCH: [
                r'\b(图片|图像|照片|截图|画|图|jpeg|jpg|png|gif)\b',
                r'\b(image|picture|photo|screenshot|drawing|graphic|jpeg|jpg|png|gif)\b',
                r'\b(截图|照片|相册|壁纸|图标)\b',
                r'\b(screenshot|photo|album|wallpaper|icon|avatar)\b'
            ],
            IntentType.AUDIO_SEARCH: [
                r'\b(音频|音乐|歌曲|录音|声音|mp3|wav|flac)\b',
                r'\b(audio|music|song|recording|sound|mp3|wav|flac|podcast)\b',
                r'\b(播客|有声书|铃声)\b',
                r'\b(podcast|audiobook|ringtone)\b'
            ],
            IntentType.VIDEO_SEARCH: [
                r'\b(视频|影片|电影|动画|录像|mp4|avi|mkv)\b',
                r'\b(video|movie|film|animation|recording|mp4|avi|mkv|clip)\b',
                r'\b(短片|教程|演示|会议录像)\b',
                r'\b(short|tutorial|demo|meeting_recording)\b'
            ]
        }

        # File type mappings
        self.file_type_patterns = {
            IntentType.DOCUMENT_SEARCH: [
                r'\.(pdf|doc|docx|txt|rtf|odt|xls|xlsx|ppt|pptx)$'
            ],
            IntentType.IMAGE_SEARCH: [
                r'\.(jpg|jpeg|png|gif|bmp|tiff|svg|webp)$'
            ],
            IntentType.AUDIO_SEARCH: [
                r'\.(mp3|wav|flac|aac|ogg|wma|m4a)$'
            ],
            IntentType.VIDEO_SEARCH: [
                r'\.(mp4|avi|mkv|mov|wmv|flv|webm|m4v)$'
            ]
        }

    async def analyze_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryIntent:
        """
        Analyze query intent using combined rule-based and LLM approach.

        Args:
            query: User query string
            context: Additional context information

        Returns:
            QueryIntent analysis result
        """
        logger.debug(f"Analyzing intent for query: {query}")

        # Step 1: Rule-based intent detection
        rule_based_result = self._rule_based_intent_analysis(query)

        # Step 2: LLM-based intent analysis for complex queries
        if not rule_based_result.confidence or rule_based_result.confidence < 0.8:
            try:
                llm_result = await self._llm_intent_analysis(query, context)
                # Combine results, preferring LLM for complex queries
                return self._combine_intent_results(rule_based_result, llm_result)
            except Exception as e:
                logger.warning(f"LLM intent analysis failed: {str(e)}, using rule-based result")
                return rule_based_result
        else:
            return rule_based_result

    def _rule_based_intent_analysis(self, query: str) -> QueryIntent:
        """
        Perform rule-based intent analysis using pattern matching.

        Args:
            query: User query string

        Returns:
            QueryIntent from pattern matching
        """
        query_lower = query.lower()
        intent_scores = {}
        detected_keywords = []
        detected_file_types = []

        # Score each intent type based on pattern matches
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            intent_keywords = []

            for pattern in patterns:
                matches = re.findall(pattern, query_lower, re.IGNORECASE)
                if matches:
                    score += len(matches)
                    intent_keywords.extend(matches)

            if score > 0:
                intent_scores[intent_type] = score
                detected_keywords.extend(intent_keywords)

        # Check for explicit file type mentions
        for intent_type, patterns in self.file_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    detected_file_types.extend(pattern.split('|')[1:])  # Extract extensions
                    if intent_type not in intent_scores:
                        intent_scores[intent_type] = 1
                    else:
                        intent_scores[intent_type] += 1

        # Determine primary intent
        if not intent_scores:
            # Default to document search if no patterns match
            primary_intent = IntentType.DOCUMENT_SEARCH
            confidence = 0.3
        else:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            max_score = max(intent_scores.values())
            total_score = sum(intent_scores.values())
            confidence = min(max_score / max(total_score, 1), 1.0)

        # Extract entities and additional information
        entities = self._extract_entities(query)
        language = self._detect_language(query)

        return QueryIntent(
            intent_type=primary_intent,
            confidence=confidence,
            keywords=list(set(detected_keywords)),
            entities=entities,
            file_types=list(set(detected_file_types)),
            language=language
        )

    async def _llm_intent_analysis(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryIntent:
        """
        Perform LLM-based intent analysis for complex queries.

        Args:
            query: User query string
            context: Additional context information

        Returns:
            QueryIntent from LLM analysis
        """
        system_prompt = """
你是一个查询意图分析专家。请分析用户的查询意图，并返回结构化的分析结果。

你需要：
1. 确定主要搜索意图类型
2. 提取关键词和实体
3. 识别文件类型偏好
4. 分析语言类型
5. 给出置信度评分

支持的意图类型：
- document_search: 文档搜索 (PDF, Word, Excel, PPT等)
- image_search: 图片搜索 (JPEG, PNG, GIF等)
- audio_search: 音频搜索 (MP3, WAV等)
- video_search: 视频搜索 (MP4, AVI等)
- mixed_search: 混合搜索
- semantic_search: 语义搜索
- factual_search: 事实搜索

请以JSON格式返回分析结果：
{
    "intent_type": "document_search",
    "confidence": 0.95,
    "keywords": ["产品设计", "PPT"],
    "entities": {
        "file_type": ["ppt"],
        "time_range": ["上周"]
    },
    "time_range": {
        "start": "2024-11-07",
        "end": "2024-11-14"
    },
    "file_types": ["ppt", "pptx"],
    "language": "zh",
    "semantic_description": "用户想要搜索最近的产品设计PPT文档"
}
"""

        try:
            response = await self.llm_provider.generate_response(
                prompt=f"请分析以下查询的意图：\n\n查询：{query}\n\n上下文：{json.dumps(context, ensure_ascii=False) if context else '无'}",
                system_prompt=system_prompt
            )

            if response.is_successful and response.content:
                # Parse JSON response
                try:
                    result_data = json.loads(response.content)
                    return QueryIntent(**result_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM intent response as JSON: {str(e)}")
                    # Fallback to keyword-based parsing
                    return self._parse_llm_text_response(response.content)

        except Exception as e:
            logger.error(f"LLM intent analysis failed: {str(e)}")

        # Fallback to rule-based analysis
        return self._rule_based_intent_analysis(query)

    def _parse_llm_text_response(self, content: str) -> QueryIntent:
        """
        Parse text-based LLM response when JSON parsing fails.

        Args:
            content: LLM response content

        Returns:
            Parsed QueryIntent
        """
        # Simple keyword-based fallback
        intent_type = IntentType.DOCUMENT_SEARCH
        confidence = 0.7

        content_lower = content.lower()
        if "image" in content_lower or "图片" in content_lower:
            intent_type = IntentType.IMAGE_SEARCH
        elif "audio" in content_lower or "音频" in content_lower:
            intent_type = IntentType.AUDIO_SEARCH
        elif "video" in content_lower or "视频" in content_lower:
            intent_type = IntentType.VIDEO_SEARCH

        return QueryIntent(
            intent_type=intent_type,
            confidence=confidence,
            keywords=["分析", "查询"],
            language="zh"
        )

    def _combine_intent_results(self, rule_based: QueryIntent, llm_based: QueryIntent) -> QueryIntent:
        """
        Combine results from rule-based and LLM analysis.

        Args:
            rule_based: Rule-based analysis result
            llm_based: LLM-based analysis result

        Returns:
            Combined QueryIntent
        """
        # Prefer LLM result for complex queries with higher confidence
        if llm_based.confidence > rule_based.confidence:
            return llm_based
        else:
            # Merge keywords and entities from both results
            combined_keywords = list(set(rule_based.keywords + llm_based.keywords))
            combined_entities = {**rule_based.entities, **llm_based.entities}

            return QueryIntent(
                intent_type=llm_based.intent_type if llm_based.confidence > 0.7 else rule_based.intent_type,
                confidence=max(rule_based.confidence, llm_based.confidence),
                keywords=combined_keywords,
                entities=combined_entities,
                time_range=llm_based.time_range or rule_based.time_range,
                file_types=list(set(rule_based.file_types + llm_based.file_types)),
                language=llm_based.language or rule_based.language,
                semantic_description=llm_based.semantic_description,
                sub_intents=list(set(rule_based.sub_intents + llm_based.sub_intents))
            )

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the query.

        Args:
            query: User query string

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        # Time expressions
        time_patterns = [
            r'(今天|昨天|本周|上周|本月|上月|今年|去年)',
            r'(today|yesterday|this week|last week|this month|last month|this year|last year)',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]

        time_matches = []
        for pattern in time_patterns:
            matches = re.findall(pattern, query)
            time_matches.extend(matches)

        if time_matches:
            entities['time_range'] = time_matches

        # File extensions
        file_pattern = r'\.(pdf|doc|docx|txt|jpg|jpeg|png|gif|mp3|mp4|avi|ppt|pptx|xls|xlsx)'
        file_matches = re.findall(file_pattern, query.lower())
        if file_matches:
            entities['file_extension'] = file_matches

        return entities

    def _detect_language(self, query: str) -> Optional[str]:
        """
        Detect the language of the query.

        Args:
            query: User query string

        Returns:
            Language code (zh, en, etc.)
        """
        # Simple character-based detection
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', query))
        total_chars = len(query.replace(' ', '').replace('\n', ''))

        if total_chars == 0:
            return None

        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.3:
            return "zh"
        elif chinese_ratio < 0.1:
            return "en"
        else:
            return "zh"  # 中英文混合时默认使用中文

    def get_intent_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about intent analysis performance.

        Returns:
            Intent analysis statistics
        """
        return {
            "supported_intents": [intent.value for intent in IntentType],
            "rule_based_patterns": sum(len(patterns) for patterns in self.intent_patterns.values()),
            "file_type_patterns": sum(len(patterns) for patterns in self.file_type_patterns.values()),
            "llm_provider": self.llm_provider.provider.value if self.llm_provider else None
        }