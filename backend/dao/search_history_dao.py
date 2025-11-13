"""
Search History Data Access Object (DAO) implementation.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, delete

from model.search_history import SearchHistory
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class SearchHistoryDAO(BaseDAO[SearchHistory, Dict[str, Any], Dict[str, Any]]):
    """Search History DAO with specific search history operations."""

    def __init__(self):
        super().__init__(SearchHistory)

    async def get_recent_searches(
        self,
        db: AsyncSession,
        *,
        limit: int = 50,
        query_type: Optional[str] = None
    ) -> List[SearchHistory]:
        """
        Get recent search history.

        Args:
            db: Database session
            limit: Maximum number of searches to return
            query_type: Optional query type filter

        Returns:
            List of recent searches
        """
        try:
            query = select(SearchHistory)

            if query_type:
                query = query.where(SearchHistory.query_type == query_type)

            query = query.order_by(desc(SearchHistory.created_at)).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting recent searches: {e}")
            raise

    async def get_popular_searches(
        self,
        db: AsyncSession,
        *,
        days: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get popular searches by frequency.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of searches to return

        Returns:
            List of popular search queries with counts
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = (
                select(
                    SearchHistory.query_text,
                    SearchHistory.query_type,
                    func.count(SearchHistory.id).label('frequency'),
                    func.avg(SearchHistory.search_time_ms).label('avg_time_ms'),
                    func.avg(SearchHistory.result_count).label('avg_results')
                )
                .where(SearchHistory.created_at >= cutoff_date)
                .group_by(SearchHistory.query_text, SearchHistory.query_type)
                .order_by(desc(func.count(SearchHistory.id)))
                .limit(limit)
            )

            result = await db.execute(query)
            return [
                {
                    "query_text": row.query_text,
                    "query_type": row.query_type,
                    "frequency": row.frequency,
                    "avg_time_ms": round(row.avg_time_ms, 2) if row.avg_time_ms else 0,
                    "avg_results": round(row.avg_results, 2) if row.avg_results else 0
                }
                for row in result.all()
            ]
        except Exception as e:
            logger.error(f"Error getting popular searches: {e}")
            raise

    async def get_search_statistics(
        self,
        db: AsyncSession,
        *,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get search statistics.

        Args:
            db: Database session
            days: Number of days to look back

        Returns:
            Dictionary with search statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Total searches
            total_query = select(func.count(SearchHistory.id)).where(
                SearchHistory.created_at >= cutoff_date
            )
            total_result = await db.execute(total_query)
            total_searches = total_result.scalar() or 0

            # Searches by type
            type_query = (
                select(
                    SearchHistory.query_type,
                    func.count(SearchHistory.id).label('count')
                )
                .where(SearchHistory.created_at >= cutoff_date)
                .group_by(SearchHistory.query_type)
            )
            type_result = await db.execute(type_query)
            type_stats = type_result.all()

            # Average performance metrics
            performance_query = (
                select(
                    func.avg(SearchHistory.search_time_ms).label('avg_time_ms'),
                    func.avg(SearchHistory.result_count).label('avg_results'),
                    func.max(SearchHistory.search_time_ms).label('max_time_ms'),
                    func.min(SearchHistory.search_time_ms).label('min_time_ms')
                )
                .where(SearchHistory.created_at >= cutoff_date)
            )
            performance_result = await db.execute(performance_query)
            performance_stats = performance_result.first()

            # Searches by mode
            mode_query = (
                select(
                    SearchHistory.search_mode,
                    func.count(SearchHistory.id).label('count')
                )
                .where(SearchHistory.created_at >= cutoff_date)
                .group_by(SearchHistory.search_mode)
            )
            mode_result = await db.execute(mode_query)
            mode_stats = mode_result.all()

            return {
                "total_searches": total_searches,
                "period_days": days,
                "by_query_type": [
                    {
                        "type": stat.query_type or "unknown",
                        "count": stat.count
                    }
                    for stat in type_stats
                ],
                "by_search_mode": [
                    {
                        "mode": stat.search_mode or "unknown",
                        "count": stat.count
                    }
                    for stat in mode_stats
                ],
                "performance": {
                    "avg_time_ms": round(performance_stats.avg_time_ms, 2) if performance_stats.avg_time_ms else 0,
                    "avg_results": round(performance_stats.avg_results, 2) if performance_stats.avg_results else 0,
                    "max_time_ms": performance_stats.max_time_ms or 0,
                    "min_time_ms": performance_stats.min_time_ms or 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            raise

    async def find_similar_queries(
        self,
        db: AsyncSession,
        *,
        query_text: str,
        limit: int = 10
    ) -> List[SearchHistory]:
        """
        Find similar search queries.

        Args:
            db: Database session
            query_text: Query to find similarities for
            limit: Maximum number of similar queries to return

        Returns:
            List of similar search histories
        """
        try:
            # Simple string matching for similarity
            query = (
                select(SearchHistory)
                .where(
                    and_(
                        SearchHistory.query_text.ilike(f"%{query_text}%"),
                        SearchHistory.query_text != query_text
                    )
                )
                .order_by(desc(SearchHistory.created_at))
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error finding similar queries for '{query_text}': {e}")
            raise

    async def get_user_search_history(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        query_type: Optional[str] = None,
        days: Optional[int] = None
    ) -> List[SearchHistory]:
        """
        Get user search history with filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            query_type: Optional query type filter
            days: Optional number of days to limit to

        Returns:
            List of search histories
        """
        try:
            query = select(SearchHistory)

            if query_type:
                query = query.where(SearchHistory.query_type == query_type)

            if days:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                query = query.where(SearchHistory.created_at >= cutoff_date)

            query = query.order_by(desc(SearchHistory.created_at)).offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user search history: {e}")
            raise

    async def clear_search_history(
        self,
        db: AsyncSession,
        *,
        days: Optional[int] = None,
        query_type: Optional[str] = None
    ) -> int:
        """
        Clear search history.

        Args:
            db: Database session
            days: Optional number of days to clear (older than)
            query_type: Optional query type filter

        Returns:
            Number of records deleted
        """
        try:
            query = delete(SearchHistory)

            conditions = []
            if days:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                conditions.append(SearchHistory.created_at < cutoff_date)

            if query_type:
                conditions.append(SearchHistory.query_type == query_type)

            if conditions:
                query = query.where(and_(*conditions))

            result = await db.execute(query)
            await db.flush()
            return result.rowcount
        except Exception as e:
            logger.error(f"Error clearing search history: {e}")
            raise

    async def get_slow_searches(
        self,
        db: AsyncSession,
        *,
        threshold_ms: int = 1000,
        days: int = 30,
        limit: int = 50
    ) -> List[SearchHistory]:
        """
        Get searches that took longer than threshold.

        Args:
            db: Database session
            threshold_ms: Time threshold in milliseconds
            days: Number of days to look back
            limit: Maximum number of searches to return

        Returns:
            List of slow searches
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = (
                select(SearchHistory)
                .where(
                    and_(
                        SearchHistory.created_at >= cutoff_date,
                        SearchHistory.search_time_ms > threshold_ms
                    )
                )
                .order_by(desc(SearchHistory.search_time_ms))
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting slow searches: {e}")
            raise

    async def get_zero_result_searches(
        self,
        db: AsyncSession,
        *,
        days: int = 30,
        limit: int = 50
    ) -> List[SearchHistory]:
        """
        Get searches that returned no results.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of searches to return

        Returns:
            List of zero-result searches
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = (
                select(SearchHistory)
                .where(
                    and_(
                        SearchHistory.created_at >= cutoff_date,
                        SearchHistory.result_count == 0
                    )
                )
                .order_by(desc(SearchHistory.created_at))
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting zero-result searches: {e}")
            raise


# Create a singleton instance
search_history_dao = SearchHistoryDAO()