"""
Tag Data Access Object (DAO) implementation.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, update

from model.tag import Tag
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class TagDAO(BaseDAO[Tag, Dict[str, Any], Dict[str, Any]]):
    """Tag DAO with specific tag-related operations."""

    def __init__(self):
        super().__init__(Tag)

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[Tag]:
        """
        Get a tag by name.

        Args:
            db: Database session
            name: Tag name

        Returns:
            Tag object or None
        """
        try:
            query = select(Tag).where(Tag.name == name)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting tag by name '{name}': {e}")
            raise

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        """
        Get tags by category.

        Args:
            db: Database session
            category: Tag category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tags
        """
        try:
            filters = {"category": category}
            return await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                order_by="usage_count",
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting tags by category '{category}': {e}")
            raise

    async def get_popular_tags(
        self,
        db: AsyncSession,
        *,
        limit: int = 50,
        category: Optional[str] = None
    ) -> List[Tag]:
        """
        Get popular tags by usage count.

        Args:
            db: Database session
            limit: Maximum number of tags to return
            category: Optional category filter

        Returns:
            List of popular tags
        """
        try:
            query = select(Tag).where(Tag.usage_count > 0)

            if category:
                query = query.where(Tag.category == category)

            query = query.order_by(desc(Tag.usage_count), Tag.name).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting popular tags: {e}")
            raise

    async def get_system_tags(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None
    ) -> List[Tag]:
        """
        Get system-generated tags.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            List of system tags
        """
        try:
            filters = {"is_system_tag": True}
            if category:
                filters["category"] = category

            return await self.get_multi(
                db=db,
                order_by="category,name",
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting system tags: {e}")
            raise

    async def get_user_tags(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None
    ) -> List[Tag]:
        """
        Get user-created tags.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            List of user tags
        """
        try:
            filters = {"is_system_tag": False}
            if category:
                filters["category"] = category

            return await self.get_multi(
                db=db,
                order_by="usage_count,name",
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting user tags: {e}")
            raise

    async def search_tags(
        self,
        db: AsyncSession,
        *,
        query: str,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        """
        Search tags by name or description.

        Args:
            db: Database session
            query: Search query
            category: Optional category filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching tags
        """
        try:
            search_conditions = [
                Tag.name.ilike(f"%{query}%"),
                Tag.description.ilike(f"%{query}%")
            ]

            base_query = select(Tag).where(or_(*search_conditions))

            if category:
                base_query = base_query.where(Tag.category == category)

            query = base_query.order_by(desc(Tag.usage_count), Tag.name).offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching tags: {e}")
            raise

    async def get_or_create_tag(
        self,
        db: AsyncSession,
        *,
        name: str,
        category: str = "user",
        description: Optional[str] = None,
        color: str = "#007bff",
        is_system_tag: bool = False
    ) -> Tag:
        """
        Get an existing tag or create a new one.

        Args:
            db: Database session
            name: Tag name
            category: Tag category
            description: Tag description
            color: Tag color
            is_system_tag: Whether this is a system tag

        Returns:
            Tag object
        """
        try:
            # Try to get existing tag
            existing_tag = await self.get_by_name(db, name=name)
            if existing_tag:
                return existing_tag

            # Create new tag
            tag_data = {
                "name": name,
                "category": category,
                "description": description,
                "color": color,
                "is_system_tag": is_system_tag,
                "usage_count": 0,
                "created_at": datetime.utcnow()
            }

            return await self.create(db, obj_in=tag_data)
        except Exception as e:
            logger.error(f"Error getting or creating tag '{name}': {e}")
            raise

    async def update_usage_count(
        self,
        db: AsyncSession,
        *,
        tag_id: int,
        increment: int = 1
    ) -> Optional[Tag]:
        """
        Update tag usage count.

        Args:
            db: Database session
            tag_id: Tag ID
            increment: Amount to increment usage count

        Returns:
            Updated tag or None
        """
        try:
            tag = await self.get(db, obj_id=tag_id)
            if tag:
                tag.usage_count += increment
                tag.last_used = datetime.utcnow()
                db.add(tag)
                await db.flush()
                await db.refresh(tag)
            return tag
        except Exception as e:
            logger.error(f"Error updating usage count for tag {tag_id}: {e}")
            raise

    async def get_categories(
        self,
        db: AsyncSession
    ) -> List[str]:
        """
        Get all unique tag categories.

        Args:
            db: Database session

        Returns:
            List of category names
        """
        try:
            query = select(Tag.category).where(Tag.category.isnot(None)).distinct().order_by(Tag.category)
            result = await db.execute(query)
            return [row.category for row in result.all()]
        except Exception as e:
            logger.error(f"Error getting tag categories: {e}")
            raise

    async def get_unused_tags(
        self,
        db: AsyncSession,
        *,
        days: int = 90
    ) -> List[Tag]:
        """
        Get tags that haven't been used recently.

        Args:
            db: Database session
            days: Number of days since last use

        Returns:
            List of unused tags
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = (
                select(Tag)
                .where(
                    or_(
                        Tag.last_used < cutoff_date,
                        Tag.last_used.is_(None),
                        Tag.usage_count == 0
                    )
                )
                .order_by(Tag.last_used.asc().nullsfirst())
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting unused tags: {e}")
            raise

    async def get_tag_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get tag statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with tag statistics
        """
        try:
            # Total tags
            total_query = select(func.count(Tag.id))
            total_result = await db.execute(total_query)
            total_tags = total_result.scalar() or 0

            # System vs user tags
            system_query = select(func.count(Tag.id)).where(Tag.is_system_tag == True)
            system_result = await db.execute(system_query)
            system_tags = system_result.scalar() or 0

            user_tags = total_tags - system_tags

            # Tags by category
            category_query = (
                select(
                    Tag.category,
                    func.count(Tag.id).label('count'),
                    func.sum(Tag.usage_count).label('total_usage')
                )
                .where(Tag.category.isnot(None))
                .group_by(Tag.category)
                .order_by(desc(func.sum(Tag.usage_count)))
            )
            category_result = await db.execute(category_query)
            category_stats = category_result.all()

            # Usage statistics
            usage_query = select(
                func.sum(Tag.usage_count).label('total_usage'),
                func.avg(Tag.usage_count).label('avg_usage'),
                func.max(Tag.usage_count).label('max_usage')
            )
            usage_result = await db.execute(usage_query)
            usage_stats = usage_result.first()

            return {
                "total_tags": total_tags,
                "system_tags": system_tags,
                "user_tags": user_tags,
                "by_category": [
                    {
                        "category": stat.category or "unknown",
                        "count": stat.count,
                        "total_usage": stat.total_usage or 0
                    }
                    for stat in category_stats
                ],
                "usage_statistics": {
                    "total_usage": usage_stats.total_usage or 0,
                    "average_usage": round(usage_stats.avg_usage, 2) if usage_stats.avg_usage else 0,
                    "max_usage": usage_stats.max_usage or 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting tag statistics: {e}")
            raise

    async def merge_tags(
        self,
        db: AsyncSession,
        *,
        source_tag_id: int,
        target_tag_id: int
    ) -> bool:
        """
        Merge one tag into another.

        Args:
            db: Database session
            source_tag_id: ID of tag to merge from
            target_tag_id: ID of tag to merge into

        Returns:
            True if merge was successful
        """
        try:
            source_tag = await self.get(db, obj_id=source_tag_id)
            target_tag = await self.get(db, obj_id=target_tag_id)

            if not source_tag or not target_tag:
                return False

            # Add usage count from source to target
            target_tag.usage_count += source_tag.usage_count
            target_tag.last_used = max(
                target_tag.last_used or datetime.utcnow(),
                source_tag.last_used or datetime.utcnow()
            )

            # Update all file-tag relationships to point to target tag
            from models.file_tag import FileTag
            update_query = (
                update(FileTag)
                .where(FileTag.tag_id == source_tag_id)
                .values(tag_id=target_tag_id)
            )
            await db.execute(update_query)

            # Delete the source tag
            await db.delete(source_tag)
            await db.flush()

            return True
        except Exception as e:
            logger.error(f"Error merging tags {source_tag_id} -> {target_tag_id}: {e}")
            await db.rollback()
            return False


# Create a singleton instance
tag_dao = TagDAO()