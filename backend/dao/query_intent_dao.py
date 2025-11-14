"""
Query Intent Data Access Object for LLM query understanding results.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from model.query_intent import QueryIntent
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class QueryIntentDAO(BaseDAO[QueryIntent, Dict[str, Any], Dict[str, Any]]):
    """Data Access Object for QueryIntent model."""

    def __init__(self):
        """Initialize QueryIntent DAO."""
        super().__init__(QueryIntent)

    async def create_intent(
        self,
        db: AsyncSession,
        original_query: str,
        intent_type: str,
        confidence: float,
        **kwargs
    ) -> QueryIntent:
        """
        Create a new query intent record.

        Args:
            db: Database session
            original_query: Original user query
            intent_type: Type of intent
            confidence: Confidence score
            **kwargs: Additional fields

        Returns:
            Created QueryIntent instance
        """
        intent = QueryIntent(
            original_query=original_query,
            intent_type=intent_type,
            confidence=confidence,
            **kwargs
        )

        db.add(intent)
        await db.flush()
        await db.refresh(intent)

        logger.debug(f"Created query intent: {intent.id} for query: {original_query[:50]}...")
        return intent

    async def get_by_query(
        self,
        db: AsyncSession,
        query: str,
        exact_match: bool = True
    ) -> Optional[QueryIntent]:
        """
        Get query intent by query text.

        Args:
            db: Database session
            query: Query text to search for
            exact_match: Whether to require exact match

        Returns:
            QueryIntent if found, None otherwise
        """
        if exact_match:
            stmt = select(QueryIntent).where(QueryIntent.original_query == query)
        else:
            stmt = select(QueryIntent).where(
                func.lower(QueryIntent.original_query).contains(func.lower(query))
            )

        stmt = stmt.order_by(desc(QueryIntent.confidence)).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_intents(
        self,
        db: AsyncSession,
        limit: int = 50,
        intent_type: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> List[QueryIntent]:
        """
        Get recent query intents.

        Args:
            db: Database session
            limit: Maximum number of results
            intent_type: Filter by intent type
            min_confidence: Minimum confidence threshold

        Returns:
            List of QueryIntent instances
        """
        stmt = select(QueryIntent).order_by(desc(QueryIntent.created_at))

        if intent_type:
            stmt = stmt.where(QueryIntent.intent_type == intent_type)

        if min_confidence is not None:
            stmt = stmt.where(QueryIntent.confidence >= min_confidence)

        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_intent_statistics(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get statistics about query intents.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total intents in period
        total_stmt = select(func.count(QueryIntent.id)).where(
            QueryIntent.created_at >= cutoff_date
        )
        total_result = await db.execute(total_stmt)
        total_intents = total_result.scalar() or 0

        # Intents by type
        type_stmt = select(
            QueryIntent.intent_type,
            func.count(QueryIntent.id).label('count'),
            func.avg(QueryIntent.confidence).label('avg_confidence')
        ).where(
            QueryIntent.created_at >= cutoff_date
        ).group_by(QueryIntent.intent_type)

        type_result = await db.execute(type_stmt)
        intent_types = {}
        for row in type_result:
            intent_types[row.intent_type] = {
                'count': row.count,
                'avg_confidence': float(row.avg_confidence or 0.0)
            }

        # Language distribution
        lang_stmt = select(
            QueryIntent.language,
            func.count(QueryIntent.id).label('count')
        ).where(
            and_(
                QueryIntent.created_at >= cutoff_date,
                QueryIntent.language.isnot(None)
            )
        ).group_by(QueryIntent.language)

        lang_result = await db.execute(lang_stmt)
        languages = {row.language: row.count for row in lang_result}

        # Average processing time
        time_stmt = select(
            func.avg(QueryIntent.processing_time_ms)
        ).where(
            and_(
                QueryIntent.created_at >= cutoff_date,
                QueryIntent.processing_time_ms.isnot(None)
            )
        )
        time_result = await db.execute(time_stmt)
        avg_processing_time = float(time_result.scalar() or 0.0)

        return {
            'period_days': days,
            'total_intents': total_intents,
            'intent_types': intent_types,
            'languages': languages,
            'avg_processing_time_ms': avg_processing_time,
            'generated_at': datetime.utcnow().isoformat()
        }

    async def get_popular_keywords(
        self,
        db: AsyncSession,
        limit: int = 20,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get most popular keywords from recent intents.

        Args:
            db: Database session
            limit: Maximum number of keywords to return
            days: Number of days to analyze

        Returns:
            List of keyword statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # This is a simplified approach - in production you might want to use
        # JSON functions or proper keyword normalization
        stmt = select(QueryIntent).where(
            and_(
                QueryIntent.created_at >= cutoff_date,
                QueryIntent.keywords.isnot(None)
            )
        )

        result = await db.execute(stmt)
        intents = result.scalars().all()

        keyword_counts = {}
        for intent in intents:
            if intent.keywords and isinstance(intent.keywords, list):
                for keyword in intent.keywords:
                    if isinstance(keyword, str):
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Sort by frequency and return top results
        sorted_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'keyword': keyword, 'count': count}
            for keyword, count in sorted_keywords
        ]

    async def update_intent(
        self,
        db: AsyncSession,
        intent_id: int,
        **kwargs
    ) -> Optional[QueryIntent]:
        """
        Update an existing query intent.

        Args:
            db: Database session
            intent_id: Intent ID to update
            **kwargs: Fields to update

        Returns:
            Updated QueryIntent if found, None otherwise
        """
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.utcnow()

        stmt = (
            update(QueryIntent)
            .where(QueryIntent.id == intent_id)
            .values(**kwargs)
            .returning(QueryIntent)
        )

        result = await db.execute(stmt)
        await db.flush()

        return result.scalar_one_or_none()

    async def delete_old_intents(
        self,
        db: AsyncSession,
        days: int = 90
    ) -> int:
        """
        Delete old query intents to clean up database.

        Args:
            db: Database session
            days: Age threshold in days

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = delete(QueryIntent).where(QueryIntent.created_at < cutoff_date)
        result = await db.execute(stmt)

        deleted_count = result.rowcount
        await db.flush()

        logger.info(f"Deleted {deleted_count} old query intents older than {days} days")
        return deleted_count

    async def search_intents(
        self,
        db: AsyncSession,
        query_text: Optional[str] = None,
        intent_type: Optional[str] = None,
        language: Optional[str] = None,
        min_confidence: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[QueryIntent], int]:
        """
        Search query intents with multiple filters.

        Args:
            db: Database session
            query_text: Text to search in original_query
            intent_type: Filter by intent type
            language: Filter by language
            min_confidence: Minimum confidence threshold
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum results
            offset: Results offset

        Returns:
            Tuple of (results list, total count)
        """
        # Build base query
        base_stmt = select(QueryIntent)
        count_stmt = select(func.count(QueryIntent.id))

        # Apply filters
        conditions = []

        if query_text:
            conditions.append(
                func.lower(QueryIntent.original_query).contains(func.lower(query_text))
            )

        if intent_type:
            conditions.append(QueryIntent.intent_type == intent_type)

        if language:
            conditions.append(QueryIntent.language == language)

        if min_confidence is not None:
            conditions.append(QueryIntent.confidence >= min_confidence)

        if start_date:
            conditions.append(QueryIntent.created_at >= start_date)

        if end_date:
            conditions.append(QueryIntent.created_at <= end_date)

        if conditions:
            base_stmt = base_stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        # Get total count
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get results with pagination
        base_stmt = base_stmt.order_by(desc(QueryIntent.created_at))
        base_stmt = base_stmt.offset(offset).limit(limit)

        result = await db.execute(base_stmt)
        intents = result.scalars().all()

        return intents, total

    async def get_intent_by_id(
        self,
        db: AsyncSession,
        intent_id: int
    ) -> Optional[QueryIntent]:
        """
        Get query intent by ID.

        Args:
            db: Database session
            intent_id: Intent ID

        Returns:
            QueryIntent if found, None otherwise
        """
        stmt = select(QueryIntent).where(QueryIntent.id == intent_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_similar_queries(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find similar queries based on text similarity.

        Args:
            db: Database session
            query: Query to find matches for
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of similar queries with similarity scores
        """
        # Simple text-based similarity - in production you might want to use
        # vector similarity or more sophisticated algorithms
        query_lower = query.lower()
        query_words = set(query_lower.split())

        stmt = select(QueryIntent).where(
            and_(
                QueryIntent.original_query.isnot(None),
                QueryIntent.confidence >= 0.7  # Only consider high confidence queries
            )
        ).limit(100)  # Get more candidates for similarity calculation

        result = await db.execute(stmt)
        intents = result.scalars().all()

        similar_queries = []
        for intent in intents:
            if intent.original_query:
                intent_lower = intent.original_query.lower()
                intent_words = set(intent_lower.split())

                # Calculate Jaccard similarity
                intersection = query_words.intersection(intent_words)
                union = query_words.union(intent_words)
                similarity = len(intersection) / len(union) if union else 0.0

                if similarity >= min_similarity:
                    similar_queries.append({
                        'query': intent.original_query,
                        'intent_type': intent.intent_type,
                        'confidence': intent.confidence,
                        'similarity': similarity,
                        'created_at': intent.created_at
                    })

        # Sort by similarity and limit results
        similar_queries.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_queries[:limit]