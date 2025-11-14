"""
LLM Cache Data Access Object for caching LLM responses.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from model.llm_cache import LLMCache
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class LLMCacheDAO(BaseDAO[LLMCache, Dict[str, Any], Dict[str, Any]]):
    """Data Access Object for LLMCache model."""

    def __init__(self):
        """Initialize LLMCache DAO."""
        super().__init__(LLMCache)

    def _generate_cache_key(self, prompt: str, system_prompt: Optional[str] = None,
                           llm_provider: str = "mock", llm_model: str = "gpt-3.5-turbo") -> str:
        """
        Generate a cache key for the request.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            llm_provider: LLM provider name
            llm_model: LLM model name

        Returns:
            Cache key string
        """
        # Create a deterministic key from prompt and parameters
        key_data = {
            'prompt': prompt,
            'system_prompt': system_prompt or '',
            'provider': llm_provider,
            'model': llm_model
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _generate_prompt_hash(self, prompt: str) -> str:
        """
        Generate a hash for faster prompt lookups.

        Args:
            prompt: User prompt

        Returns:
            Prompt hash string
        """
        return hashlib.md5(prompt.encode()).hexdigest()

    async def get_cache(
        self,
        db: AsyncSession,
        prompt: str,
        system_prompt: Optional[str] = None,
        llm_provider: str = "mock",
        llm_model: str = "gpt-3.5-turbo"
    ) -> Optional[LLMCache]:
        """
        Get cached LLM response.

        Args:
            db: Database session
            prompt: User prompt
            system_prompt: System prompt
            llm_provider: LLM provider name
            llm_model: LLM model name

        Returns:
            Cached LLMCache if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(prompt, system_prompt, llm_provider, llm_model)

        stmt = select(LLMCache).where(LLMCache.cache_key == cache_key)
        result = await db.execute(stmt)
        cache_entry = result.scalar_one_or_none()

        if cache_entry and cache_entry.is_valid:
            # Record cache hit
            cache_entry.record_hit()
            await db.flush()

            logger.debug(f"Cache hit for key: {cache_key[:16]}...")
            return cache_entry
        elif cache_entry and not cache_entry.is_valid:
            # Remove expired cache entry
            await db.delete(cache_entry)
            await db.flush()

        logger.debug(f"Cache miss for key: {cache_key[:16]}...")
        return None

    async def set_cache(
        self,
        db: AsyncSession,
        prompt: str,
        response_content: str,
        llm_provider: str = "mock",
        llm_model: str = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None,
        structured_data: Optional[Dict[str, Any]] = None,
        function_calls: Optional[List[Dict[str, Any]]] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        response_time_ms: int = 0,
        cost_usd: float = 0.0,
        finish_reason: Optional[str] = None,
        confidence_score: Optional[float] = None,
        quality_score: Optional[float] = None,
        ttl_seconds: int = 3600,
        request_metadata: Optional[Dict[str, Any]] = None,
        response_metadata: Optional[Dict[str, Any]] = None
    ) -> LLMCache:
        """
        Cache an LLM response.

        Args:
            db: Database session
            prompt: User prompt
            response_content: LLM response content
            llm_provider: LLM provider name
            llm_model: LLM model name
            system_prompt: System prompt
            structured_data: Parsed structured response
            function_calls: Function calls if any
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total tokens used
            response_time_ms: Response time in milliseconds
            cost_usd: Cost in USD
            finish_reason: Reason for completion
            confidence_score: Response confidence score
            quality_score: Response quality score
            ttl_seconds: Time to live in seconds
            request_metadata: Additional request metadata
            response_metadata: Additional response metadata

        Returns:
            Created LLMCache instance
        """
        cache_key = self._generate_cache_key(prompt, system_prompt, llm_provider, llm_model)
        prompt_hash = self._generate_prompt_hash(prompt)

        # Check if entry already exists
        existing_cache = await self.get_cache(db, prompt, system_prompt, llm_provider, llm_model)
        if existing_cache:
            logger.debug(f"Cache entry already exists for key: {cache_key[:16]}...")
            return existing_cache

        cache_entry = LLMCache(
            cache_key=cache_key,
            prompt_hash=prompt_hash,
            llm_provider=llm_provider,
            llm_model=llm_model,
            system_prompt=system_prompt,
            response_content=response_content,
            structured_data=structured_data,
            function_calls=function_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_time_ms=response_time_ms,
            cost_usd=cost_usd,
            finish_reason=finish_reason,
            confidence_score=confidence_score,
            quality_score=quality_score,
            ttl_seconds=ttl_seconds,
            request_metadata=request_metadata,
            response_metadata=response_metadata
        )

        cache_entry.set_expiration(ttl_seconds)

        db.add(cache_entry)
        await db.flush()
        await db.refresh(cache_entry)

        logger.debug(f"Cached response for key: {cache_key[:16]}...")
        return cache_entry

    async def invalidate_cache(
        self,
        db: AsyncSession,
        prompt: str,
        system_prompt: Optional[str] = None,
        llm_provider: str = "mock",
        llm_model: str = "gpt-3.5-turbo"
    ) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            db: Database session
            prompt: User prompt
            system_prompt: System prompt
            llm_provider: LLM provider name
            llm_model: LLM model name

        Returns:
            True if entry was invalidated, False if not found
        """
        cache_key = self._generate_cache_key(prompt, system_prompt, llm_provider, llm_model)

        stmt = delete(LLMCache).where(LLMCache.cache_key == cache_key)
        result = await db.execute(stmt)

        deleted_count = result.rowcount
        await db.flush()

        if deleted_count > 0:
            logger.debug(f"Invalidated cache entry for key: {cache_key[:16]}...")
            return True

        return False

    async def cleanup_expired_cache(
        self,
        db: AsyncSession,
        batch_size: int = 100
    ) -> int:
        """
        Clean up expired cache entries.

        Args:
            db: Database session
            batch_size: Number of entries to delete per batch

        Returns:
            Number of deleted entries
        """
        # Find expired entries
        expired_stmt = select(LLMCache.id).where(
            or_(
                LLMCache.expires_at < datetime.utcnow(),
                and_(
                    LLMCache.expires_at.is_(None),
                    LLMCache.created_at < datetime.utcnow() - timedelta(seconds=3600)
                )
            )
        ).limit(batch_size)

        result = await db.execute(expired_stmt)
        expired_ids = [row[0] for row in result.fetchall()]

        if not expired_ids:
            return 0

        # Delete expired entries
        delete_stmt = delete(LLMCache).where(LLMCache.id.in_(expired_ids))
        delete_result = await db.execute(delete_stmt)

        deleted_count = delete_result.rowcount
        await db.flush()

        logger.info(f"Cleaned up {deleted_count} expired cache entries")
        return deleted_count

    async def get_cache_statistics(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get cache statistics and performance metrics.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total cache entries
        total_stmt = select(func.count(LLMCache.id))
        total_result = await db.execute(total_stmt)
        total_entries = total_result.scalar() or 0

        # Entries in period
        period_stmt = select(func.count(LLMCache.id)).where(
            LLMCache.created_at >= cutoff_date
        )
        period_result = await db.execute(period_stmt)
        period_entries = period_result.scalar() or 0

        # Cache hits statistics
        hits_stmt = select(
            func.sum(LLMCache.hit_count).label('total_hits'),
            func.avg(LLMCache.hit_count).label('avg_hits'),
            func.max(LLMCache.hit_count).label('max_hits')
        )
        hits_result = await db.execute(hits_stmt)
        hits_row = hits_result.first()

        # Provider and model statistics
        provider_stmt = select(
            LLMCache.llm_provider,
            LLMCache.llm_model,
            func.count(LLMCache.id).label('count'),
            func.sum(LLMCache.hit_count).label('total_hits'),
            func.sum(LLMCache.total_tokens).label('total_tokens'),
            func.sum(LLMCache.cost_usd).label('total_cost')
        ).group_by(LLMCache.llm_provider, LLMCache.llm_model)

        provider_result = await db.execute(provider_stmt)
        providers = []
        for row in provider_result:
            providers.append({
                'provider': row.llm_provider,
                'model': row.llm_model,
                'count': row.count,
                'total_hits': row.total_hits or 0,
                'total_tokens': row.total_tokens or 0,
                'total_cost': float(row.total_cost or 0.0)
            })

        # Cache efficiency
        efficiency_stmt = select(
            func.count(LLMCache.id).label('total'),
            func.sum(func.case([(LLMCache.hit_count > 0, 1)], else_=0)).label('hit_entries')
        )
        efficiency_result = await db.execute(efficiency_stmt)
        efficiency_row = efficiency_result.first()

        total_cache_entries = efficiency_row.total or 0
        hit_entries = efficiency_row.hit_entries or 0
        hit_rate = (hit_entries / total_cache_entries * 100) if total_cache_entries > 0 else 0.0

        # Cost savings
        cost_savings_stmt = select(
            func.sum(
                LLMCache.cost_usd * LLMCache.hit_count
            ).label('total_savings')
        )
        cost_savings_result = await db.execute(cost_savings_stmt)
        total_savings = float(cost_savings_result.scalar() or 0.0)

        return {
            'period_days': days,
            'total_entries': total_entries,
            'period_entries': period_entries,
            'total_hits': int(hits_row.total_hits or 0),
            'avg_hits_per_entry': float(hits_row.avg_hits or 0.0),
            'max_hits_per_entry': int(hits_row.max_hits or 0),
            'hit_rate_percent': round(hit_rate, 2),
            'total_cost_savings_usd': round(total_savings, 4),
            'providers': providers,
            'generated_at': datetime.utcnow().isoformat()
        }

    async def get_popular_cache_entries(
        self,
        db: AsyncSession,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most popular cache entries by hit count.

        Args:
            db: Database session
            limit: Maximum number of entries

        Returns:
            List of popular cache entries
        """
        stmt = select(LLMCache).where(
            LLMCache.hit_count > 0
        ).order_by(desc(LLMCache.hit_count)).limit(limit)

        result = await db.execute(stmt)
        entries = result.scalars().all()

        popular_entries = []
        for entry in entries:
            popular_entries.append({
                'cache_key': entry.cache_key[:32] + "...",  # Truncated for readability
                'llm_provider': entry.llm_provider,
                'llm_model': entry.llm_model,
                'hit_count': entry.hit_count,
                'efficiency_score': entry.efficiency_score,
                'cost_savings': entry.cost_savings,
                'created_at': entry.created_at,
                'last_accessed': entry.last_accessed
            })

        return popular_entries

    async def clear_cache_by_provider(
        self,
        db: AsyncSession,
        provider: str,
        model: Optional[str] = None
    ) -> int:
        """
        Clear cache entries for a specific provider/model.

        Args:
            db: Database session
            provider: LLM provider name
            model: Specific model name (optional)

        Returns:
            Number of deleted entries
        """
        conditions = [LLMCache.llm_provider == provider]

        if model:
            conditions.append(LLMCache.llm_model == model)

        stmt = delete(LLMCache).where(and_(*conditions))
        result = await db.execute(stmt)

        deleted_count = result.rowcount
        await db.flush()

        logger.info(f"Cleared {deleted_count} cache entries for provider: {provider}, model: {model}")
        return deleted_count

    async def extend_cache_ttl(
        self,
        db: AsyncSession,
        prompt: str,
        additional_seconds: int,
        system_prompt: Optional[str] = None,
        llm_provider: str = "mock",
        llm_model: str = "gpt-3.5-turbo"
    ) -> bool:
        """
        Extend TTL for a specific cache entry.

        Args:
            db: Database session
            prompt: User prompt
            additional_seconds: Additional seconds to extend TTL
            system_prompt: System prompt
            llm_provider: LLM provider name
            llm_model: LLM model name

        Returns:
            True if TTL was extended, False if entry not found
        """
        cache_entry = await self.get_cache(db, prompt, system_prompt, llm_provider, llm_model)

        if cache_entry:
            cache_entry.extend_ttl(additional_seconds)
            await db.flush()

            logger.debug(f"Extended TTL for cache entry by {additional_seconds} seconds")
            return True

        return False