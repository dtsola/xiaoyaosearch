"""
Time Parser - Time expression parsing component.

This module provides intelligent parsing of time expressions in user queries,
converting relative and absolute time references to structured date ranges.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import json

from ..models.query_intent import TimeRange
from ..llm_providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class TimeParser:
    """
    Time expression parser supporting multiple languages and formats.

    Parses relative expressions like "上周", "最近一周", "last month" and
    absolute date formats into structured date ranges.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize time parser.

        Args:
            llm_provider: LLM provider for complex time expression parsing
        """
        self.llm_provider = llm_provider
        self.now = datetime.now()

        # Time expression patterns (Chinese and English)
        self.time_patterns = {
            # Relative time patterns
            'relative': {
                'zh': [
                    (r'今天', lambda: (self.now.date(), self.now.date())),
                    (r'昨天', lambda: (self.now.date() - timedelta(days=1), self.now.date() - timedelta(days=1))),
                    (r'前天', lambda: (self.now.date() - timedelta(days=2), self.now.date() - timedelta(days=2))),
                    (r'明天', lambda: (self.now.date() + timedelta(days=1), self.now.date() + timedelta(days=1))),
                    (r'后天', lambda: (self.now.date() + timedelta(days=2), self.now.date() + timedelta(days=2))),
                    (r'本周|这周', self._get_this_week),
                    (r'上周', self._get_last_week),
                    (r'下周', self._get_next_week),
                    (r'本月|这个月', self._get_this_month),
                    (r'上月|上个月', self._get_last_month),
                    (r'下月|下个月', self._get_next_month),
                    (r'今年|这一年', self._get_this_year),
                    (r'去年|上一年', self._get_last_year),
                    (r'明年|下一年', self._get_next_year),
                    (r'最近(\d+)(天|日)', self._get_recent_days),
                    (r'最近(\d+)周', self._get_recent_weeks),
                    (r'最近(\d+)月', self._get_recent_months),
                    (r'最近(\d+)年', self._get_recent_years),
                    (r'过去(\d+)(天|日)', self._get_recent_days),
                    (r'过去(\d+)周', self._get_recent_weeks),
                    (r'过去(\d+)月', self._get_recent_months),
                ],
                'en': [
                    (r'today', lambda: (self.now.date(), self.now.date())),
                    (r'yesterday', lambda: (self.now.date() - timedelta(days=1), self.now.date() - timedelta(days=1))),
                    (r'tomorrow', lambda: (self.now.date() + timedelta(days=1), self.now.date() + timedelta(days=1))),
                    (r'this week', self._get_this_week),
                    (r'last week', self._get_last_week),
                    (r'next week', self._get_next_week),
                    (r'this month', self._get_this_month),
                    (r'last month', self._get_last_month),
                    (r'next month', self._get_next_month),
                    (r'this year', self._get_this_year),
                    (r'last year', self._get_last_year),
                    (r'next year', self._get_next_year),
                    (r'recent (\d+) days?', self._get_recent_days),
                    (r'recent (\d+) weeks?', self._get_recent_weeks),
                    (r'recent (\d+) months?', self._get_recent_months),
                    (r'recent (\d+) years?', self._get_recent_years),
                    (r'past (\d+) days?', self._get_recent_days),
                    (r'past (\d+) weeks?', self._get_recent_weeks),
                    (r'past (\d+) months?', self._get_recent_months),
                    (r'last (\d+) days?', self._get_last_days),
                    (r'last (\d+) weeks?', self._get_last_weeks),
                    (r'last (\d+) months?', self._get_last_months),
                ]
            },
            # Absolute date patterns
            'absolute': [
                # Chinese date formats
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{4})/(\d{1,2})/(\d{1,2})',
                # International date formats
                r'(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{1,2})-(\d{1,2})-(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                # Month name patterns
                r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}),? (\d{4})',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}),? (\d{4})',
            ]
        }

        # Month name mapping
        self.month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

    async def parse_time_expression(
        self,
        query: str,
        language: Optional[str] = None
    ) -> Optional[TimeRange]:
        """
        Parse time expressions in the query.

        Args:
            query: User query string
            language: Language hint (zh, en, mixed)

        Returns:
            TimeRange if time expression found, None otherwise
        """
        logger.debug(f"Parsing time expressions in query: {query}")

        # Detect language if not provided
        if not language:
            language = self._detect_language(query)

        # Step 1: Try rule-based parsing
        rule_based_result = self._rule_based_parsing(query, language)
        if rule_based_result:
            return rule_based_result

        # Step 2: Try LLM-based parsing for complex expressions
        try:
            llm_result = await self._llm_parsing(query, language)
            return llm_result
        except Exception as e:
            logger.warning(f"LLM time parsing failed: {str(e)}")
            return None

    def _rule_based_parsing(self, query: str, language: str) -> Optional[TimeRange]:
        """
        Perform rule-based time expression parsing.

        Args:
            query: User query string
            language: Query language

        Returns:
            TimeRange if expression found
        """
        # Try relative time expressions first
        for lang in [language, 'zh', 'en']:
            if lang in self.time_patterns['relative']:
                for pattern, handler in self.time_patterns['relative'][lang]:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        try:
                            if callable(handler):
                                start_date, end_date = handler()
                                confidence = 0.9
                            else:
                                start_date, end_date = handler
                                confidence = 0.9

                            return TimeRange(
                                start_date=start_date,
                                end_date=end_date,
                                relative_expression=match.group(0),
                                confidence=confidence
                            )
                        except Exception as e:
                            logger.warning(f"Error handling time pattern {pattern}: {str(e)}")
                            continue

        # Try absolute date patterns
        for pattern in self.time_patterns['absolute']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    start_date, end_date = self._parse_absolute_date(match)
                    if start_date:
                        return TimeRange(
                            start_date=start_date,
                            end_date=end_date,
                            relative_expression=match.group(0),
                            confidence=0.95
                        )
                except Exception as e:
                    logger.warning(f"Error parsing absolute date {match.group(0)}: {str(e)}")
                    continue

        return None

    async def _llm_parsing(self, query: str, language: str) -> Optional[TimeRange]:
        """
        Perform LLM-based time expression parsing.

        Args:
            query: User query string
            language: Query language

        Returns:
            TimeRange if expression found
        """
        system_prompt = f"""
你是一个时间表达式解析专家。请从用户的查询中识别并解析时间表达式。

要求：
1. 识别绝对日期（如2024年1月15日、15/01/2024）
2. 识别相对时间（如上周、最近一月、去年）
3. 识别时间范围（如1月到3月、去年全年）
4. 计算具体的开始和结束日期
5. 给出解析置信度（0.0-1.0）

查询语言：{language}

请以JSON格式返回结果：
{{
    "start_date": "2024-11-07",
    "end_date": "2024-11-14",
    "relative_expression": "上周",
    "confidence": 0.95,
    "date_format": "YYYY-MM-DD"
}}

如果没有找到时间表达式，返回：
{{
    "found": false,
    "confidence": 0.0
}}
"""

        try:
            response = await self.llm_provider.generate_response(
                prompt=f"请解析以下查询中的时间表达式：\n\n查询：{query}",
                system_prompt=system_prompt
            )

            if response.is_successful and response.content:
                result_data = json.loads(response.content)

                if result_data.get('found', True) and 'start_date' in result_data:
                    start_date = datetime.strptime(result_data['start_date'], '%Y-%m-%d').date()
                    end_date = datetime.strptime(result_data['end_date'], '%Y-%m-%d').date()

                    return TimeRange(
                        start_date=start_date,
                        end_date=end_date,
                        relative_expression=result_data.get('relative_expression'),
                        confidence=result_data.get('confidence', 0.8)
                )

        except Exception as e:
            logger.error(f"LLM time parsing failed: {str(e)}")

        return None

    def _parse_absolute_date(self, match) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Parse absolute date from regex match.

        Args:
            match: Regex match object

        Returns:
            Tuple of (start_date, end_date)
        """
        groups = match.groups()

        # Handle different date formats
        if len(groups) >= 3:
            try:
                # Format: YYYY-MM-DD or YYYY年MM月DD日
                if len(groups[0]) == 4:  # Year first
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                # Format: DD/MM/YYYY or month name DD, YYYY
                elif len(groups[2]) == 4:  # Year last
                    day, month_input, year = int(groups[0]), groups[1], int(groups[2])
                    if isinstance(month_input, str):
                        month = self.month_names.get(month_input.lower())
                        if month is None:
                            month = int(month_input)
                    else:
                        month = int(month_input)
                else:
                    return None, None

                # Validate date
                parsed_date = datetime(year, month, day).date()
                return parsed_date, parsed_date

            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid date format: {groups}, error: {str(e)}")
                return None, None

        return None, None

    # Time range calculation methods
    def _get_this_week(self) -> Tuple[datetime.date, datetime.date]:
        """Get this week's date range."""
        today = self.now.date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week

    def _get_last_week(self) -> Tuple[datetime.date, datetime.date]:
        """Get last week's date range."""
        start_of_this_week = self.now.date() - timedelta(days=self.now.weekday())
        start_of_last_week = start_of_this_week - timedelta(days=7)
        end_of_last_week = start_of_this_week - timedelta(days=1)
        return start_of_last_week, end_of_last_week

    def _get_next_week(self) -> Tuple[datetime.date, datetime.date]:
        """Get next week's date range."""
        start_of_this_week = self.now.date() - timedelta(days=self.now.weekday())
        start_of_next_week = start_of_this_week + timedelta(days=7)
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return start_of_next_week, end_of_next_week

    def _get_this_month(self) -> Tuple[datetime.date, datetime.date]:
        """Get this month's date range."""
        today = self.now.date()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start_of_month, end_of_month

    def _get_last_month(self) -> Tuple[datetime.date, datetime.date]:
        """Get last month's date range."""
        today = self.now.date()
        if today.month == 1:
            last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month - 1, day=1)

        start_of_last_month = last_month
        end_of_last_month = (today.replace(day=1) - timedelta(days=1))
        return start_of_last_month, end_of_last_month

    def _get_next_month(self) -> Tuple[datetime.date, datetime.date]:
        """Get next month's date range."""
        today = self.now.date()
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        start_of_next_month = next_month
        if next_month.month == 12:
            end_of_next_month = next_month.replace(year=next_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_next_month = next_month.replace(month=next_month.month + 1, day=1) - timedelta(days=1)
        return start_of_next_month, end_of_next_month

    def _get_this_year(self) -> Tuple[datetime.date, datetime.date]:
        """Get this year's date range."""
        start_of_year = self.now.date().replace(month=1, day=1)
        end_of_year = self.now.date().replace(month=12, day=31)
        return start_of_year, end_of_year

    def _get_last_year(self) -> Tuple[datetime.date, datetime.date]:
        """Get last year's date range."""
        last_year = self.now.year - 1
        start_of_last_year = datetime(last_year, 1, 1).date()
        end_of_last_year = datetime(last_year, 12, 31).date()
        return start_of_last_year, end_of_last_year

    def _get_next_year(self) -> Tuple[datetime.date, datetime.date]:
        """Get next year's date range."""
        next_year = self.now.year + 1
        start_of_next_year = datetime(next_year, 1, 1).date()
        end_of_next_year = datetime(next_year, 12, 31).date()
        return start_of_next_year, end_of_next_year

    def _get_recent_days(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get recent N days."""
        days = int(match.group(1))
        end_date = self.now.date()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date

    def _get_last_days(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get last N days (excluding today)."""
        days = int(match.group(1))
        end_date = self.now.date() - timedelta(days=1)
        start_date = end_date - timedelta(days=days - 1)
        return start_date, end_date

    def _get_recent_weeks(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get recent N weeks."""
        weeks = int(match.group(1))
        end_date = self.now.date()
        start_date = end_date - timedelta(weeks=weeks * 7)
        return start_date, end_date

    def _get_last_weeks(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get last N weeks."""
        weeks = int(match.group(1))
        end_date = self.now.date() - timedelta(days=7)
        start_date = end_date - timedelta(weeks=weeks * 7)
        return start_date, end_date

    def _get_recent_months(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get recent N months."""
        months = int(match.group(1))
        end_date = self.now.date()

        start_date = end_date
        for _ in range(months):
            if start_date.month == 1:
                start_date = start_date.replace(year=start_date.year - 1, month=12)
            else:
                start_date = start_date.replace(month=start_date.month - 1)

        return start_date, end_date

    def _get_last_months(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get last N months (excluding current month)."""
        months = int(match.group(1))
        end_date = self.now.date().replace(day=1) - timedelta(days=1)

        start_date = end_date
        for _ in range(months - 1):
            if start_date.month == 1:
                start_date = start_date.replace(year=start_date.year - 1, month=12, day=1)
            else:
                start_date = start_date.replace(month=start_date.month - 1, day=1)

        return start_date.replace(day=1), end_date

    def _get_recent_years(self, match) -> Tuple[datetime.date, datetime.date]:
        """Get recent N years."""
        years = int(match.group(1))
        end_date = self.now.date()
        start_date = end_date.replace(year=end_date.year - years)
        return start_date, end_date

    def _detect_language(self, query: str) -> str:
        """Detect query language."""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', query))
        total_chars = len(query.replace(' ', '').replace('\n', ''))

        if total_chars == 0:
            return 'en'

        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.3:
            return 'zh'
        else:
            return 'en'

    def get_parser_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about time parser performance.

        Returns:
            Parser statistics
        """
        return {
            'supported_languages': ['zh', 'en'],
            'relative_patterns_count': sum(
                len(patterns) for patterns in self.time_patterns['relative'].values()
            ),
            'absolute_patterns_count': len(self.time_patterns['absolute']),
            'llm_provider': self.llm_provider.provider.value if self.llm_provider else None
        }