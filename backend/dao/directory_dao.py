"""
Directory Data Access Object (DAO) implementation.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func

from model.directory import Directory
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class DirectoryDAO(BaseDAO[Directory, Dict[str, Any], Dict[str, Any]]):
    """Directory DAO with specific directory-related operations."""

    def __init__(self):
        super().__init__(Directory)

    async def get_by_path(
        self,
        db: AsyncSession,
        *,
        path: str
    ) -> Optional[Directory]:
        """
        Get a directory by its path.

        Args:
            db: Database session
            path: Directory path

        Returns:
            Directory object or None
        """
        try:
            query = select(Directory).where(Directory.path == path)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting directory by path {path}: {e}")
            raise

    async def get_root_directories(
        self,
        db: AsyncSession,
        *,
        indexed_only: bool = True
    ) -> List[Directory]:
        """
        Get root directories (directories without parent).

        Args:
            db: Database session
            indexed_only: Whether to return only indexed directories

        Returns:
            List of root directories
        """
        try:
            query = select(Directory).where(Directory.parent_id.is_(None))

            if indexed_only:
                query = query.where(Directory.is_indexed == True)

            query = query.order_by(Directory.name)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting root directories: {e}")
            raise

    async def get_child_directories(
        self,
        db: AsyncSession,
        *,
        parent_id: int,
        indexed_only: bool = True
    ) -> List[Directory]:
        """
        Get child directories of a parent directory.

        Args:
            db: Database session
            parent_id: Parent directory ID
            indexed_only: Whether to return only indexed directories

        Returns:
            List of child directories
        """
        try:
            query = select(Directory).where(Directory.parent_id == parent_id)

            if indexed_only:
                query = query.where(Directory.is_indexed == True)

            query = query.order_by(Directory.name)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting child directories for parent {parent_id}: {e}")
            raise

    async def get_directory_tree(
        self,
        db: AsyncSession,
        *,
        root_id: Optional[int] = None,
        max_depth: int = 10,
        indexed_only: bool = True
    ) -> List[Directory]:
        """
        Get directory tree structure.

        Args:
            db: Database session
            root_id: Root directory ID (None for all root directories)
            max_depth: Maximum depth to traverse
            indexed_only: Whether to return only indexed directories

        Returns:
            List of directories in tree structure
        """
        try:
            if root_id:
                # Start from specific directory
                root_dir = await self.get(db, obj_id=root_id)
                if not root_dir:
                    return []
                return [root_dir] + await self._get_children_recursive(
                    db, root_id, max_depth - 1, indexed_only
                )
            else:
                # Start from all root directories
                root_dirs = await self.get_root_directories(db, indexed_only=indexed_only)
                all_dirs = []
                for root_dir in root_dirs:
                    all_dirs.append(root_dir)
                    children = await self._get_children_recursive(
                        db, root_dir.id, max_depth - 1, indexed_only
                    )
                    all_dirs.extend(children)
                return all_dirs
        except Exception as e:
            logger.error(f"Error getting directory tree: {e}")
            raise

    async def _get_children_recursive(
        self,
        db: AsyncSession,
        parent_id: int,
        remaining_depth: int,
        indexed_only: bool = True
    ) -> List[Directory]:
        """
        Recursively get child directories.

        Args:
            db: Database session
            parent_id: Parent directory ID
            remaining_depth: Remaining depth to traverse
            indexed_only: Whether to return only indexed directories

        Returns:
            List of child directories
        """
        if remaining_depth <= 0:
            return []

        children = await self.get_child_directories(db, parent_id=parent_id, indexed_only=indexed_only)
        all_children = []

        for child in children:
            all_children.append(child)
            grandchildren = await self._get_children_recursive(
                db, child.id, remaining_depth - 1, indexed_only
            )
            all_children.extend(grandchildren)

        return all_children

    async def search_directories(
        self,
        db: AsyncSession,
        *,
        query: str,
        parent_id: Optional[int] = None,
        indexed_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Directory]:
        """
        Search directories by name.

        Args:
            db: Database session
            query: Search query
            parent_id: Optional parent directory filter
            indexed_only: Whether to search only indexed directories
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching directories
        """
        try:
            search_conditions = [
                Directory.name.ilike(f"%{query}%"),
                Directory.path.ilike(f"%{query}%")
            ]

            base_query = select(Directory).where(or_(*search_conditions))

            if parent_id:
                base_query = base_query.where(Directory.parent_id == parent_id)

            if indexed_only:
                base_query = base_query.where(Directory.is_indexed == True)

            query = base_query.order_by(Directory.name).offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching directories: {e}")
            raise

    async def update_scan_status(
        self,
        db: AsyncSession,
        *,
        directory_id: int,
        scan_status: str,
        file_count: Optional[int] = None,
        total_size: Optional[int] = None
    ) -> Optional[Directory]:
        """
        Update directory scan status.

        Args:
            db: Database session
            directory_id: Directory ID
            scan_status: New scan status
            file_count: Optional file count
            total_size: Optional total size

        Returns:
            Updated directory or None
        """
        try:
            from datetime import datetime

            directory = await self.get(db, obj_id=directory_id)
            if directory:
                directory.scan_status = scan_status
                directory.last_scanned = datetime.utcnow()

                if file_count is not None:
                    directory.file_count = file_count

                if total_size is not None:
                    directory.total_size = total_size

                db.add(directory)
                await db.flush()
                await db.refresh(directory)
            return directory
        except Exception as e:
            logger.error(f"Error updating scan status for directory {directory_id}: {e}")
            raise

    async def get_directories_to_scan(
        self,
        db: AsyncSession,
        *,
        limit: int = 10
    ) -> List[Directory]:
        """
        Get directories that need to be scanned.

        Args:
            db: Database session
            limit: Maximum number of directories to return

        Returns:
            List of directories to scan
        """
        try:
            query = (
                select(Directory)
                .where(
                    and_(
                        Directory.is_indexed == True,
                        Directory.scan_status.in_(["pending", "failed"])
                    )
                )
                .order_by(Directory.last_scanned.asc().nullsfirst())
                .limit(limit)
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting directories to scan: {e}")
            raise

    async def get_directory_path(
        self,
        db: AsyncSession,
        *,
        directory_id: int
    ) -> str:
        """
        Get full path of a directory by traversing up the tree.

        Args:
            db: Database session
            directory_id: Directory ID

        Returns:
            Full path string
        """
        try:
            directory = await self.get(db, obj_id=directory_id)
            if not directory:
                return ""

            path_parts = []
            current_dir = directory

            while current_dir:
                path_parts.append(current_dir.name)
                if current_dir.parent_id:
                    current_dir = await self.get(db, obj_id=current_dir.parent_id)
                else:
                    break

            # Reverse to get correct order and join
            path_parts.reverse()
            return "/".join(path_parts)
        except Exception as e:
            logger.error(f"Error getting directory path for {directory_id}: {e}")
            raise

    async def get_scan_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get scanning statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with scan statistics
        """
        try:
            # Total indexed directories
            total_query = select(func.count(Directory.id)).where(Directory.is_indexed == True)
            total_result = await db.execute(total_query)
            total_indexed = total_result.scalar() or 0

            # Stats by scan status
            status_query = (
                select(
                    Directory.scan_status,
                    func.count(Directory.id).label('count')
                )
                .where(Directory.is_indexed == True)
                .group_by(Directory.scan_status)
            )
            status_result = await db.execute(status_query)
            status_stats = status_result.all()

            # Total files and size
            files_query = select(
                func.sum(Directory.file_count).label('total_files'),
                func.sum(Directory.total_size).label('total_size')
            ).where(Directory.is_indexed == True)
            files_result = await db.execute(files_query)
            files_stats = files_result.first()

            return {
                "total_indexed_directories": total_indexed,
                "scan_status_distribution": [
                    {
                        "status": stat.scan_status or "unknown",
                        "count": stat.count
                    }
                    for stat in status_stats
                ],
                "total_files": files_stats.total_files or 0,
                "total_size_bytes": files_stats.total_size or 0,
                "total_size_gb": round((files_stats.total_size or 0) / (1024 * 1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Error getting scan statistics: {e}")
            raise

    async def create_directory_hierarchy(
        self,
        db: AsyncSession,
        *,
        path: str,
        is_indexed: bool = True,
        scan_depth: int = 10
    ) -> Directory:
        """
        Create directory hierarchy for a given path.

        Args:
            db: Database session
            path: Directory path
            is_indexed: Whether directory should be indexed
            scan_depth: Maximum scan depth

        Returns:
            Created or existing directory object
        """
        try:
            import os
            from datetime import datetime

            # Split path into components
            path_parts = [part for part in path.split('/') if part]
            current_path = ""
            parent_id = None

            for i, part in enumerate(path_parts):
                current_path = "/" + "/".join(path_parts[:i + 1])

                # Check if directory already exists
                existing_dir = await self.get_by_path(db, path=current_path)
                if existing_dir:
                    parent_id = existing_dir.id
                    continue

                # Create new directory
                new_dir_data = {
                    "path": current_path,
                    "name": part,
                    "parent_id": parent_id,
                    "is_indexed": is_indexed,
                    "scan_depth": scan_depth,
                    "created_at": datetime.utcnow(),
                    "modified_at": datetime.utcnow()
                }

                new_dir = await self.create(db, obj_in=new_dir_data)
                parent_id = new_dir.id

            # Return the final directory in the hierarchy
            return await self.get_by_path(db, path=path)
        except Exception as e:
            logger.error(f"Error creating directory hierarchy for {path}: {e}")
            raise


# Create a singleton instance
directory_dao = DirectoryDAO()