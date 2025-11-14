"""
Language Detector - Query language detection component.

This module provides intelligent detection of query languages,
supporting Chinese, English, and mixed-language queries.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from collections import Counter

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Language detector supporting Chinese, English, and mixed queries.

    Uses character analysis, pattern matching, and statistical methods
    to accurately detect query language and provide confidence scores.
    """

    def __init__(self):
        """Initialize language detector."""
        # Character set definitions
        self.chinese_chars = set(chr(i) for i in range(0x4E00, 0x9FFF + 1))  # CJK Unified Ideographs
        self.english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.numeric_chars = set('0123456789')
        self.common_punctuation = set('.,;:!?()[]{}""\'\'，。；：！？（）【】""''')

        # Language-specific word patterns
        self.chinese_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它',
            '我们', '你们', '他们', '她们', '它们', '这个', '那个', '这些', '那些', '什么', '怎么', '为什么'
        }

        self.english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
            'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
            'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just',
            'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see',
            'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back'
        }

        # Mixed language indicators
        self.mixed_patterns = [
            r'[a-zA-Z]+\s*[一-龯]+',  # English word followed by Chinese
            r'[一-龯]+\s*[a-zA-Z]+',  # Chinese followed by English word
            r'[a-zA-Z]+[一-龯]+',     # Mixed within word
            r'[一-龯]+[a-zA-Z]+',     # Mixed within word
        ]

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the given text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with language detection results
        """
        if not text or not text.strip():
            return {
                'primary_language': 'unknown',
                'confidence': 0.0,
                'language_distribution': {},
                'is_mixed': False,
                'method': 'empty_input'
            }

        logger.debug(f"Detecting language for text: {text[:50]}...")

        # Step 1: Character-based analysis
        char_analysis = self._character_analysis(text)

        # Step 2: Word-based analysis
        word_analysis = self._word_analysis(text)

        # Step 3: Pattern-based mixed language detection
        mixed_analysis = self._mixed_language_detection(text)

        # Step 4: Combine results and determine final classification
        result = self._combine_analysis_results(char_analysis, word_analysis, mixed_analysis)

        return result

    def _character_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze text based on character distribution.

        Args:
            text: Text to analyze

        Returns:
            Character analysis results
        """
        total_chars = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        if total_chars == 0:
            return {'chinese': 0, 'english': 0, 'other': 0, 'total': 0}

        chinese_count = 0
        english_count = 0
        other_count = 0

        for char in text:
            if char in self.chinese_chars:
                chinese_count += 1
            elif char in self.english_chars:
                english_count += 1
            elif char not in self.common_punctuation and char not in self.numeric_chars and not char.isspace():
                other_count += 1

        return {
            'chinese': chinese_count,
            'english': english_count,
            'other': other_count,
            'total': total_chars,
            'chinese_ratio': chinese_count / total_chars,
            'english_ratio': english_count / total_chars,
            'other_ratio': other_count / total_chars
        }

    def _word_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze text based on word patterns and common words.

        Args:
            text: Text to analyze

        Returns:
            Word analysis results
        """
        # Extract words
        chinese_words = re.findall(r'[一-龯]+', text)
        english_words = re.findall(r'[a-zA-Z]+', text)

        # Count common words
        chinese_common_count = sum(1 for word in chinese_words if word in self.chinese_words)
        english_common_count = sum(1 for word in english_words if word.lower() in self.english_words)

        total_chinese_words = len(chinese_words)
        total_english_words = len(english_words)
        total_words = total_chinese_words + total_english_words

        return {
            'chinese_words': total_chinese_words,
            'english_words': total_english_words,
            'total_words': total_words,
            'chinese_common_words': chinese_common_count,
            'english_common_words': english_common_count,
            'chinese_word_ratio': total_chinese_words / max(total_words, 1),
            'english_word_ratio': total_english_words / max(total_words, 1),
            'chinese_common_ratio': chinese_common_count / max(total_chinese_words, 1),
            'english_common_ratio': english_common_count / max(total_english_words, 1)
        }

    def _mixed_language_detection(self, text: str) -> Dict[str, Any]:
        """
        Detect patterns indicating mixed language usage.

        Args:
            text: Text to analyze

        Returns:
            Mixed language detection results
        """
        mixed_matches = 0
        total_patterns = len(self.mixed_patterns)

        for pattern in self.mixed_patterns:
            matches = re.findall(pattern, text)
            mixed_matches += len(matches)

        # Additional heuristics for mixed language
        has_chinese_and_english = (
            any(char in self.chinese_chars for char in text) and
            any(char in self.english_chars for char in text)
        )

        has_mixed_words = bool(re.findall(r'[a-zA-Z]+[一-龯]+|[一-龯]+[a-zA-Z]+', text))

        return {
            'mixed_pattern_matches': mixed_matches,
            'has_chinese_and_english': has_chinese_and_english,
            'has_mixed_words': has_mixed_words,
            'mixed_score': mixed_matches / max(len(text.split()), 1),
            'is_likely_mixed': mixed_matches > 0 or has_mixed_words
        }

    def _combine_analysis_results(
        self,
        char_analysis: Dict[str, Any],
        word_analysis: Dict[str, Any],
        mixed_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine analysis results to determine final language classification.

        Args:
            char_analysis: Character-based analysis
            word_analysis: Word-based analysis
            mixed_analysis: Mixed language analysis

        Returns:
            Final language detection result
        """
        # Determine if it's mixed language
        is_mixed = (
            mixed_analysis['is_likely_mixed'] or
            (char_analysis['chinese_ratio'] > 0.2 and char_analysis['english_ratio'] > 0.2) or
            (word_analysis['chinese_word_ratio'] > 0.2 and word_analysis['english_word_ratio'] > 0.2)
        )

        if is_mixed:
            # For mixed language, determine primary language
            chinese_score = (
                char_analysis['chinese_ratio'] * 0.6 +
                word_analysis['chinese_word_ratio'] * 0.3 +
                word_analysis['chinese_common_ratio'] * 0.1
            )
            english_score = (
                char_analysis['english_ratio'] * 0.6 +
                word_analysis['english_word_ratio'] * 0.3 +
                word_analysis['english_common_ratio'] * 0.1
            )

            primary_language = 'zh' if chinese_score > english_score else 'en'
            confidence = max(chinese_score, english_score) * 0.8  # Lower confidence for mixed

            language_distribution = {
                'zh': chinese_score,
                'en': english_score,
                'mixed': 0.2  # Base mixed component
            }

        else:
            # Single language detection
            chinese_score = char_analysis['chinese_ratio']
            english_score = char_analysis['english_ratio']

            if chinese_score > english_score:
                primary_language = 'zh'
                confidence = chinese_score
            else:
                primary_language = 'en'
                confidence = english_score

            language_distribution = {
                'zh': chinese_score,
                'en': english_score
            }

        # Normalize confidence
        confidence = min(max(confidence, 0.0), 1.0)

        # Determine detection method
        if word_analysis['total_words'] > 0:
            method = 'word_and_character_based'
        else:
            method = 'character_based_only'

        return {
            'primary_language': primary_language,
            'confidence': confidence,
            'language_distribution': language_distribution,
            'is_mixed': is_mixed,
            'method': method,
            'analysis_details': {
                'character_analysis': char_analysis,
                'word_analysis': word_analysis,
                'mixed_analysis': mixed_analysis
            }
        }

    def detect_multiple_languages(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Detect languages for multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            List of language detection results
        """
        results = []
        for text in texts:
            result = self.detect_language(text)
            results.append(result)

        # Calculate overall statistics
        if results:
            language_counts = Counter(result['primary_language'] for result in results)
            mixed_count = sum(1 for result in results if result['is_mixed'])

            # Add overall statistics to the first result
            results[0]['batch_statistics'] = {
                'total_texts': len(texts),
                'language_distribution': dict(language_counts),
                'mixed_language_count': mixed_count,
                'mixed_language_ratio': mixed_count / len(texts)
            }

        return results

    def get_dominant_language_batch(self, texts: List[str]) -> str:
        """
        Get the dominant language from a batch of texts.

        Args:
            texts: List of texts to analyze

        Returns:
            Dominant language code ('zh', 'en', 'mixed', 'unknown')
        """
        if not texts:
            return 'unknown'

        results = self.detect_multiple_languages(texts)
        language_counts = Counter(result['primary_language'] for result in results)

        # If more than 30% are mixed, classify as mixed
        total_texts = len(texts)
        mixed_count = language_counts.get('mixed', 0)

        if mixed_count / total_texts > 0.3:
            return 'mixed'

        # Return the most common language
        most_common = language_counts.most_common(1)
        return most_common[0][0] if most_common else 'unknown'

    def is_chinese_text(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is primarily Chinese.

        Args:
            text: Text to check
            threshold: Minimum Chinese character ratio

        Returns:
            True if text is primarily Chinese
        """
        result = self.detect_language(text)
        return result['primary_language'] == 'zh' and result['confidence'] >= threshold

    def is_english_text(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is primarily English.

        Args:
            text: Text to check
            threshold: Minimum English character ratio

        Returns:
            True if text is primarily English
        """
        result = self.detect_language(text)
        return result['primary_language'] == 'en' and result['confidence'] >= threshold

    def is_mixed_language(self, text: str) -> bool:
        """
        Check if text contains mixed languages.

        Args:
            text: Text to check

        Returns:
            True if text is mixed language
        """
        result = self.detect_language(text)
        return result['is_mixed']

    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about language detection capabilities.

        Returns:
            Detection statistics
        """
        return {
            'supported_languages': ['zh', 'en', 'mixed', 'unknown'],
            'chinese_chars_count': len(self.chinese_chars),
            'chinese_common_words': len(self.chinese_words),
            'english_common_words': len(self.english_words),
            'mixed_language_patterns': len(self.mixed_patterns),
            'detection_methods': ['character_based', 'word_based', 'pattern_based']
        }