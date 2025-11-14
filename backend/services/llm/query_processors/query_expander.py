"""
Query Expander - Query expansion and synonym component.

This module provides intelligent query expansion through synonyms,
related terms, and multilingual support to improve search recall.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Set
import json

from ..models.search_query import QueryExpansion
from ..llm_providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class QueryExpander:
    """
    Query expansion component using synonym dictionaries and LLM analysis.

    Expands user queries with synonyms, related terms, and translations
    to improve search coverage and recall.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize query expander.

        Args:
            llm_provider: LLM provider for intelligent expansion
        """
        self.llm_provider = llm_provider

        # Synonym dictionaries (Chinese and English)
        self.synonym_dict = {
            'zh': {
                '文档': ['文件', '资料', '材料', '文本', 'paper', 'document'],
                '文件': ['文档', '档案', '资料', 'file', 'document'],
                '图片': ['图像', '照片', '截图', '画', 'image', 'picture', 'photo'],
                '照片': ['图片', '相片', 'snapshot', 'photo', 'picture'],
                '视频': ['影片', '录像', 'video', 'movie', 'clip'],
                '音频': ['音乐', '声音', '录音', 'audio', 'sound', 'music'],
                '搜索': ['查找', '寻找', '检索', 'search', 'find', 'lookup'],
                '查找': ['搜索', '寻找', 'search', 'find', 'look for'],
                '报告': ['报表', '总结', '分析', 'report', 'summary'],
                '方案': ['计划', '建议', '提案', 'proposal', 'plan', 'solution'],
                '合同': ['协议', '契约', 'agreement', 'contract'],
                '产品': ['商品', '物品', 'product', 'item', 'goods'],
                '设计': ['规划', '布局', 'design', 'plan', 'layout'],
                '项目': ['计划', '工程', 'project', 'plan', 'program'],
                '数据': ['信息', '资料', 'data', 'information'],
                '系统': ['平台', '框架', 'system', 'platform', 'framework'],
                '软件': ['应用', '程序', 'software', 'application', 'app'],
                '会议': ['讨论', '研讨', 'meeting', 'conference', 'discussion'],
                '培训': ['学习', '教学', 'training', 'learning', 'education'],
                '教程': ['指南', '手册', 'tutorial', 'guide', 'manual'],
                '工具': ['用具', '软件', 'tool', 'utility', 'software'],
            },
            'en': {
                'document': ['file', 'paper', 'text', 'doc', 'report'],
                'file': ['document', 'paper', 'text', 'record'],
                'image': ['picture', 'photo', 'graphic', 'visual', 'pic'],
                'picture': ['image', 'photo', 'graphic', 'visual', 'pic'],
                'video': ['movie', 'film', 'clip', 'recording'],
                'audio': ['sound', 'music', 'recording', 'voice'],
                'search': ['find', 'lookup', 'seek', 'look for', 'query'],
                'find': ['search', 'locate', 'discover', 'look for'],
                'report': ['summary', 'analysis', 'document', 'paper'],
                'plan': ['proposal', 'scheme', 'strategy', 'design'],
                'project': ['program', 'initiative', 'venture', 'plan'],
                'data': ['information', 'stats', 'figures', 'records'],
                'system': ['platform', 'framework', 'software', 'application'],
                'software': ['application', 'app', 'program', 'tool'],
                'meeting': ['conference', 'discussion', 'session', 'gathering'],
                'tutorial': ['guide', 'manual', 'instructions', 'howto'],
                'tool': ['utility', 'application', 'software', 'instrument'],
            }
        }

        # Related term mappings
        self.related_terms = {
            'zh': {
                '设计': ['创意', '原型', '界面', '用户体验', 'UI', 'UX'],
                '开发': ['编程', '代码', '测试', '部署', '维护'],
                '分析': ['统计', '评估', '报告', '研究', '调研'],
                '管理': ['组织', '计划', '协调', '监督', '控制'],
                '学习': ['教育', '培训', '课程', '知识', '技能'],
            },
            'en': {
                'design': ['creative', 'prototype', 'interface', 'user experience', 'UI', 'UX'],
                'development': ['programming', 'coding', 'testing', 'deployment', 'maintenance'],
                'analysis': ['statistics', 'evaluation', 'research', 'study', 'assessment'],
                'management': ['organization', 'planning', 'coordination', 'supervision'],
                'learning': ['education', 'training', 'course', 'knowledge', 'skill'],
            }
        }

        # File type mappings
        self.file_type_expansions = {
            'ppt': ['powerpoint', 'presentation', 'slide', '演示文稿', '幻灯片'],
            'pdf': ['portable document', 'adobe pdf', 'acrobat', '文档'],
            'doc': ['word', 'microsoft word', 'document', '文档'],
            'xls': ['excel', 'spreadsheet', '电子表格', '工作表'],
            'jpg': ['jpeg', 'image', 'photo', 'picture', '图片', '照片'],
            'mp3': ['audio', 'music', 'sound', '音乐', '音频'],
            'mp4': ['video', 'movie', 'film', '视频', '影片'],
        }

    async def expand_query(
        self,
        query: str,
        language: Optional[str] = None,
        max_expansions: int = 5,
        include_translations: bool = True
    ) -> QueryExpansion:
        """
        Expand query with synonyms and related terms.

        Args:
            query: Original query string
            language: Query language hint
            max_expansions: Maximum number of expansions
            include_translations: Whether to include translations

        Returns:
            QueryExpansion result
        """
        logger.debug(f"Expanding query: {query}")

        # Detect language if not provided
        if not language:
            language = self._detect_language(query)

        # Step 1: Dictionary-based expansion
        dict_expansions = self._dictionary_expansion(query, language)

        # Step 2: LLM-based expansion for complex queries
        if len(query.split()) > 3 or self._needs_intelligent_expansion(query):
            try:
                llm_expansions = await self._llm_expansion(query, language)
                return self._combine_expansions(dict_expansions, llm_expansions, max_expansions)
            except Exception as e:
                logger.warning(f"LLM query expansion failed: {str(e)}, using dictionary expansion")
                return self._create_final_expansion(dict_expansions, max_expansions)
        else:
            return self._create_final_expansion(dict_expansions, max_expansions)

    def _dictionary_expansion(self, query: str, language: str) -> Dict[str, List[str]]:
        """
        Perform dictionary-based query expansion.

        Args:
            query: Original query string
            language: Query language

        Returns:
            Dictionary of expansion types and terms
        """
        expansions = {
            'synonyms': [],
            'related_terms': [],
            'file_types': [],
            'translations': []
        }

        # Lowercase query for matching
        query_lower = query.lower()

        # Extract words from query
        words = re.findall(r'\b\w+\b', query_lower)

        # Find synonyms
        for word in words:
            # Check in both languages for mixed queries
            for lang in [language, 'zh', 'en']:
                if word in self.synonym_dict.get(lang, {}):
                    synonyms = self.synonym_dict[lang][word]
                    # Filter out original word and duplicates
                    new_synonyms = [s for s in synonyms if s.lower() != word.lower() and s not in expansions['synonyms']]
                    expansions['synonyms'].extend(new_synonyms)

                # Check related terms
                if word in self.related_terms.get(lang, {}):
                    related = self.related_terms[lang][word]
                    new_related = [r for r in related if r.lower() != word.lower() and r not in expansions['related_terms']]
                    expansions['related_terms'].extend(new_related)

        # File type expansions
        for file_type, file_expansions in self.file_type_expansions.items():
            if file_type in query_lower:
                expansions['file_types'].extend(file_expansions)

        # Simple translations (basic cross-language terms)
        if include_translations and language in ['zh', 'mixed']:
            expansions['translations'] = self._get_basic_translations(words, language)

        return expansions

    async def _llm_expansion(self, query: str, language: str) -> Dict[str, List[str]]:
        """
        Perform LLM-based query expansion.

        Args:
            query: Original query string
            language: Query language

        Returns:
            Dictionary of LLM-generated expansions
        """
        system_prompt = f"""
你是一个查询扩展专家。请为用户的查询提供同义词、相关术语和翻译建议。

要求：
1. 提供5-10个同义词
2. 提供3-5个相关术语
3. 如适用，提供中英文翻译
4. 确保扩展术语与原查询语义相关
5. 按相关性排序

查询语言：{language}

请以JSON格式返回结果：
{{
    "synonyms": ["同义词1", "同义词2", "同义词3"],
    "related_terms": ["相关词1", "相关词2", "相关词3"],
    "semantic_variations": ["语义变化1", "语义变化2"],
    "translations": {{
        "zh": ["中文翻译1", "中文翻译2"],
        "en": ["English translation 1", "English translation 2"]
    }},
    "expansion_confidence": 0.85
}}
"""

        try:
            response = await self.llm_provider.generate_response(
                prompt=f"请为以下查询提供扩展建议：\n\n查询：{query}",
                system_prompt=system_prompt
            )

            if response.is_successful and response.content:
                result_data = json.loads(response.content)
                return result_data

        except Exception as e:
            logger.error(f"LLM expansion failed: {str(e)}")

        return {}

    def _combine_expansions(
        self,
        dict_expansions: Dict[str, List[str]],
        llm_expansions: Dict[str, List[str]],
        max_expansions: int
    ) -> QueryExpansion:
        """
        Combine dictionary and LLM expansions.

        Args:
            dict_expansions: Dictionary-based expansions
            llm_expansions: LLM-based expansions
            max_expansions: Maximum total expansions

        Returns:
            Combined QueryExpansion
        """
        # Combine all expansion types
        all_synonyms = list(set(
            dict_expansions.get('synonyms', []) +
            llm_expansions.get('synonyms', [])
        ))

        all_related = list(set(
            dict_expansions.get('related_terms', []) +
            llm_expansions.get('related_terms', []) +
            llm_expansions.get('semantic_variations', [])
        ))

        # Combine translations
        translations = {}
        if dict_expansions.get('translations'):
            translations['auto'] = dict_expansions['translations']
        if llm_expansions.get('translations'):
            translations.update(llm_expansions['translations'])

        # Calculate confidence
        dict_confidence = 0.7 if any(dict_expansions.values()) else 0.0
        llm_confidence = llm_expansions.get('expansion_confidence', 0.0)
        combined_confidence = max(dict_confidence, llm_confidence)

        # Limit to max_expansions
        all_synonyms = all_synonyms[:max_expansions]
        all_related = all_related[:max_expansions]

        return QueryExpansion(
            synonyms=all_synonyms,
            related_terms=all_related,
            translations=translations,
            semantic_variations=llm_expansions.get('semantic_variations', []),
            expansion_confidence=combined_confidence
        )

    def _create_final_expansion(
        self,
        expansions: Dict[str, List[str]],
        max_expansions: int
    ) -> QueryExpansion:
        """
        Create final QueryExpansion from dictionary expansions.

        Args:
            expansions: Dictionary expansions
            max_expansions: Maximum expansions

        Returns:
            QueryExpansion result
        """
        synonyms = expansions.get('synonyms', [])[:max_expansions]
        related_terms = expansions.get('related_terms', [])[:max_expansions]
        translations = {'auto': expansions.get('translations', [])} if expansions.get('translations') else {}

        # Calculate confidence based on expansion quality
        total_expansions = len(synonyms) + len(related_terms) + len(translations.get('auto', []))
        confidence = min(total_expansions / 10.0, 0.8)  # Max 0.8 for dictionary-only

        return QueryExpansion(
            synonyms=synonyms,
            related_terms=related_terms,
            translations=translations,
            semantic_variations=[],
            expansion_confidence=confidence
        )

    def _get_basic_translations(self, words: List[str], language: str) -> List[str]:
        """
        Get basic translations for common terms.

        Args:
            words: List of words to translate
            language: Source language

        Returns:
            List of translations
        """
        translations = []

        # Basic cross-language mappings
        basic_translations = {
            'zh_to_en': {
                '文档': 'document', '文件': 'file', '图片': 'image', '照片': 'photo',
                '视频': 'video', '音频': 'audio', '搜索': 'search', '查找': 'find',
                '报告': 'report', '项目': 'project', '设计': 'design', '数据': 'data'
            },
            'en_to_zh': {
                'document': '文档', 'file': '文件', 'image': '图片', 'photo': '照片',
                'video': '视频', 'audio': '音频', 'search': '搜索', 'find': '查找',
                'report': '报告', 'project': '项目', 'design': '设计', 'data': '数据'
            }
        }

        mapping_key = f'{language}_to_en' if language == 'zh' else 'en_to_zh'
        translation_map = basic_translations.get(mapping_key, {})

        for word in words:
            if word in translation_map:
                translations.append(translation_map[word])

        return translations

    def _detect_language(self, query: str) -> str:
        """Detect query language."""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', query))
        total_chars = len(query.replace(' ', '').replace('\n', ''))

        if total_chars == 0:
            return 'en'

        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.3:
            return 'zh'
        elif chinese_ratio < 0.1:
            return 'en'
        else:
            return 'mixed'

    def _needs_intelligent_expansion(self, query: str) -> bool:
        """
        Determine if query needs LLM-based intelligent expansion.

        Args:
            query: Query string

        Returns:
            True if intelligent expansion is needed
        """
        # Needs intelligent expansion if:
        # - Contains technical or domain-specific terms
        # - Has abstract concepts
        # - Contains question words
        technical_indicators = [
            r'(算法|架构|框架|平台|系统)',
            r'(algorithm|architecture|framework|platform|system)',
            r'(优化|性能|效率|解决方案)',
            r'(optimization|performance|efficiency|solution)'
        ]

        question_indicators = [
            r'(如何|怎么|怎样|what|how|why)',
            r'(哪个|哪些|which|what)',
            r'(为什么|why|reason)'
        ]

        for indicator in technical_indicators + question_indicators:
            if re.search(indicator, query, re.IGNORECASE):
                return True

        return False

    def get_expansion_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about query expansion capabilities.

        Returns:
            Expansion statistics
        """
        total_synonyms = sum(len(synonyms) for synonyms in self.synonym_dict.values())
        total_related = sum(len(terms) for terms in self.related_terms.values())

        return {
            'supported_languages': list(self.synonym_dict.keys()),
            'total_synonyms': total_synonyms,
            'total_related_terms': total_related,
            'file_type_expansions': len(self.file_type_expansions),
            'llm_provider': self.llm_provider.provider.value if self.llm_provider else None
        }