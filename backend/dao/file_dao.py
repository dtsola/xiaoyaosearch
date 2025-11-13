"""
File Data Access Object (DAO) implementation.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func

from model.file import File
from schemas.file import FileCreate, FileUpdate
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class FileDAO(BaseDAO[File, FileCreate, FileUpdate]):
    """File DAO with specific file-related operations."""

    def __init__(self):
        super().__init__(File)

    async def get_by_path(
        self,
        db: AsyncSession,
        *,
        path: str
    ) -> Optional[File]:
        """
        Get a file by its path.

        Args:
            db: Database session
            path: File path

        Returns:
            File object or None
        """
        try:
            query = select(File).where(File.path == path)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting file by path {path}: {e}")
            raise

    async def get_by_hash(
        self,
        db: AsyncSession,
        *,
        content_hash: str
    ) -> Optional[File]:
        """
        Get a file by its content hash.

        Args:
            db: Database session
            content_hash: File content hash

        Returns:
            File object or None
        """
        try:
            query = select(File).where(File.content_hash == content_hash)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting file by hash {content_hash}: {e}")
            raise

    async def get_by_directory(
        self,
        db: AsyncSession,
        *,
        directory_id: int,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "filename"
    ) -> List[File]:
        """
        Get files by directory.

        Args:
            db: Database session
            directory_id: Directory ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column to order by

        Returns:
            List of files
        """
        try:
            filters = {"directory_id": directory_id, "is_deleted": False}
            return await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                order_by=order_by,
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting files for directory {directory_id}: {e}")
            raise

    async def get_by_extension(
        self,
        db: AsyncSession,
        *,
        extensions: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Get files by extension.

        Args:
            db: Database session
            extensions: List of file extensions
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of files
        """
        try:
            filters = {"extension": extensions, "is_deleted": False}
            return await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting files by extensions {extensions}: {e}")
            raise

    async def get_by_content_type(
        self,
        db: AsyncSession,
        *,
        content_types: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Get files by content type.

        Args:
            db: Database session
            content_types: List of content types
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of files
        """
        try:
            filters = {"content_type": content_types, "is_deleted": False}
            return await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters
            )
        except Exception as e:
            logger.error(f"Error getting files by content types {content_types}: {e}")
            raise

    async def get_recent_files(
        self,
        db: AsyncSession,
        *,
        days: int = 7,
        limit: int = 50
    ) -> List[File]:
        """
        Get recently modified files.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of files to return

        Returns:
            List of recent files
        """
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = (
                select(File)
                .where(
                    and_(
                        File.modified_at >= cutoff_date,
                        File.is_deleted == False
                    )
                )
                .order_by(desc(File.modified_at))
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting recent files: {e}")
            raise

    async def get_popular_files(
        self,
        db: AsyncSession,
        *,
        limit: int = 50
    ) -> List[File]:
        """
        Get files sorted by access count.

        Args:
            db: Database session
            limit: Maximum number of files to return

        Returns:
            List of popular files
        """
        try:
            query = (
                select(File)
                .where(File.is_deleted == False)
                .order_by(desc(File.access_count), desc(File.last_accessed))
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting popular files: {e}")
            raise

    async def search_files(
        self,
        db: AsyncSession,
        *,
        query: str,
        directory_id: Optional[int] = None,
        extensions: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Search files by text content.

        Args:
            db: Database session
            query: Search query
            directory_id: Optional directory filter
            extensions: Optional extension filter
            content_types: Optional content type filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching files
        """
        try:
            # Build search conditions
            search_conditions = [
                File.filename.ilike(f"%{query}%"),
                File.content_text.ilike(f"%{query}%")
            ]

            base_query = select(File).where(
                and_(
                    File.is_deleted == False,
                    or_(*search_conditions)
                )
            )

            # Apply optional filters
            if directory_id:
                base_query = base_query.where(File.directory_id == directory_id)

            if extensions:
                base_query = base_query.where(File.extension.in_(extensions))

            if content_types:
                base_query = base_query.where(File.content_type.in_(content_types))

            # Order by relevance (search score) and limit
            query = base_query.order_by(
                desc(File.search_score),
                desc(File.access_count)
            ).offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            raise

    async def update_access_count(
        self,
        db: AsyncSession,
        *,
        file_id: int
    ) -> Optional[File]:
        """
        Increment file access count and update last accessed timestamp.

        Args:
            db: Database session
            file_id: File ID

        Returns:
            Updated file or None
        """
        try:
            from datetime import datetime

            file_obj = await self.get(db, obj_id=file_id)
            if file_obj:
                file_obj.access_count += 1
                file_obj.last_accessed = datetime.utcnow()
                db.add(file_obj)
                await db.flush()
                await db.refresh(file_obj)
            return file_obj
        except Exception as e:
            logger.error(f"Error updating access count for file {file_id}: {e}")
            raise

    async def get_unprocessed_files(
        self,
        db: AsyncSession,
        *,
        limit: int = 100
    ) -> List[File]:
        """
        Get files that haven't been processed yet.

        Args:
            db: Database session
            limit: Maximum number of files to return

        Returns:
            List of unprocessed files
        """
        try:
            query = (
                select(File)
                .where(
                    and_(
                        File.is_deleted == False,
                        File.is_processed == False
                    )
                )
                .order_by(File.created_at)
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting unprocessed files: {e}")
            raise

    async def mark_as_processed(
        self,
        db: AsyncSession,
        *,
        file_id: int,
        processing_status: str = "completed"
    ) -> Optional[File]:
        """
        Mark a file as processed.

        Args:
            db: Database session
            file_id: File ID
            processing_status: Processing status

        Returns:
            Updated file or None
        """
        try:
            file_obj = await self.get(db, obj_id=file_id)
            if file_obj:
                file_obj.is_processed = True
                file_obj.processing_status = processing_status
                db.add(file_obj)
                await db.flush()
                await db.refresh(file_obj)
            return file_obj
        except Exception as e:
            logger.error(f"Error marking file {file_id} as processed: {e}")
            raise

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        file_id: int
    ) -> Optional[File]:
        """
        Soft delete a file (mark as deleted but keep in database).

        Args:
            db: Database session
            file_id: File ID

        Returns:
            Updated file or None
        """
        try:
            file_obj = await self.get(db, obj_id=file_id)
            if file_obj:
                file_obj.is_deleted = True
                db.add(file_obj)
                await db.flush()
                await db.refresh(file_obj)
            return file_obj
        except Exception as e:
            logger.error(f"Error soft deleting file {file_id}: {e}")
            raise

    async def get_orphaned_files(
        self,
        db: AsyncSession,
        *,
        days: int = 30
    ) -> List[File]:
        """
        Get files that reference non-existent directories.

        Args:
            db: Database session
            days: Minimum days since modification

        Returns:
            List of orphaned files
        """
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = (
                select(File)
                .outerjoin(File.directory)
                .where(
                    and_(
                        File.directory_id.isnot(None),
                        File.directory.has(None),  # Directory doesn't exist
                        File.modified_at < cutoff_date
                    )
                )
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting orphaned files: {e}")
            raise

    async def get_storage_stats(
        self,
        db: AsyncSession,
        *,
        directory_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get storage statistics for files.

        Args:
            db: Database session
            directory_id: Optional directory filter

        Returns:
            Dictionary with storage statistics
        """
        try:
            base_query = select(File).where(File.is_deleted == False)

            if directory_id:
                base_query = base_query.where(File.directory_id == directory_id)

            # Total count and size
            count_query = select(func.count(File.id)).select_from(base_query.subquery())
            size_query = select(func.sum(File.size)).select_from(base_query.subquery())

            # Stats by content type
            type_stats_query = (
                select(
                    File.content_type,
                    func.count(File.id).label('count'),
                    func.sum(File.size).label('total_size')
                )
                .where(File.is_deleted == False)
                .group_by(File.content_type)
            )

            if directory_id:
                type_stats_query = type_stats_query.where(File.directory_id == directory_id)

            # Execute queries
            count_result = await db.execute(count_query)
            size_result = await db.execute(size_query)
            type_stats_result = await db.execute(type_stats_query)

            total_count = count_result.scalar() or 0
            total_size = size_result.scalar() or 0
            type_stats = type_stats_result.all()

            return {
                "total_files": total_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "by_content_type": [
                    {
                        "content_type": stat.content_type or "unknown",
                        "count": stat.count,
                        "total_size_bytes": stat.total_size or 0,
                        "total_size_mb": round((stat.total_size or 0) / (1024 * 1024), 2)
                    }
                    for stat in type_stats
                ]
            }
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            raise


# Create a singleton instance
file_dao = FileDAO()