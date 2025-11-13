"""
Base Data Access Object (DAO) class with common CRUD operations.
"""

import logging
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Generic type variables
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base DAO class with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """
        Initialize DAO with a SQLAlchemy model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(
        self,
        db: AsyncSession,
        obj_id: int | str,
        *,
        for_update: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single object by ID.

        Args:
            db: Database session
            obj_id: Object ID
            for_update: Whether to lock for update

        Returns:
            Object instance or None
        """
        try:
            query = select(self.model).where(self.model.id == obj_id)
            if for_update:
                query = query.with_for_update()

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with ID {obj_id}: {e}")
            raise

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        filters: Dict[str, Any] | None = None
    ) -> List[ModelType]:
        """
        Get multiple objects with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column to order by (with optional direction)
            filters: Dictionary of filters to apply

        Returns:
            List of objects
        """
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        if isinstance(value, list):
                            # Handle list values with IN clause
                            query = query.where(getattr(self.model, key).in_(value))
                        else:
                            query = query.where(getattr(self.model, key) == value)

            # Apply ordering
            if order_by:
                if order_by.startswith('-'):
                    # Descending order
                    column_name = order_by[1:]
                    if hasattr(self.model, column_name):
                        query = query.order_by(getattr(self.model, column_name).desc())
                else:
                    # Ascending order
                    if hasattr(self.model, order_by):
                        query = query.order_by(getattr(self.model, order_by))
            else:
                # Default ordering by ID
                query = query.order_by(self.model.id)

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__} objects: {e}")
            raise

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Create a new object.

        Args:
            db: Database session
            obj_in: Creation schema or dictionary

        Returns:
            Created object
        """
        try:
            if isinstance(obj_in, BaseModel):
                obj_data = obj_in.model_dump()
            else:
                obj_data = obj_in

            db_obj = self.model(**obj_data)
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            await db.rollback()
            raise

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing object.

        Args:
            db: Database session
            db_obj: Existing object to update
            obj_in: Update schema or dictionary

        Returns:
            Updated object
        """
        try:
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            await db.rollback()
            raise

    async def remove(
        self,
        db: AsyncSession,
        *,
        obj_id: int | str
    ) -> Optional[ModelType]:
        """
        Remove an object by ID.

        Args:
            db: Database session
            obj_id: Object ID

        Returns:
            Removed object or None
        """
        try:
            obj = await self.get(db, obj_id=obj_id)
            if obj:
                await db.delete(obj)
                await db.flush()
            return obj
        except SQLAlchemyError as e:
            logger.error(f"Error removing {self.model.__name__} with ID {obj_id}: {e}")
            await db.rollback()
            raise

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any] | None = None
    ) -> int:
        """
        Count objects with optional filters.

        Args:
            db: Database session
            filters: Dictionary of filters to apply

        Returns:
            Number of objects
        """
        try:
            query = select(func.count(self.model.id))

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, key).in_(value))
                        else:
                            query = query.where(getattr(self.model, key) == value)

            result = await db.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__} objects: {e}")
            raise

    async def exists(
        self,
        db: AsyncSession,
        *,
        obj_id: int | str,
        filters: Dict[str, Any] | None = None
    ) -> bool:
        """
        Check if an object exists.

        Args:
            db: Database session
            obj_id: Object ID
            filters: Additional filters to check

        Returns:
            True if object exists, False otherwise
        """
        try:
            query = select(func.count(self.model.id)).where(self.model.id == obj_id)

            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)

            result = await db.execute(query)
            count = result.scalar()
            return count > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {obj_id}: {e}")
            raise

    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        obj_list: List[CreateSchemaType | Dict[str, Any]]
    ) -> List[ModelType]:
        """
        Create multiple objects in bulk.

        Args:
            db: Database session
            obj_list: List of creation schemas or dictionaries

        Returns:
            List of created objects
        """
        try:
            db_objs = []
            for obj_in in obj_list:
                if isinstance(obj_in, BaseModel):
                    obj_data = obj_in.model_dump()
                else:
                    obj_data = obj_in

                db_obj = self.model(**obj_data)
                db_objs.append(db_obj)

            db.add_all(db_objs)
            await db.flush()

            # Refresh all objects to get their IDs
            for obj in db_objs:
                await db.refresh(obj)

            return db_objs
        except SQLAlchemyError as e:
            logger.error(f"Error bulk creating {self.model.__name__} objects: {e}")
            await db.rollback()
            raise

    async def search_text(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search objects by text fields.

        Args:
            db: Database session
            search_term: Search term
            fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching objects
        """
        try:
            # Build search conditions
            search_conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    search_conditions.append(attr.ilike(f"%{search_term}%"))

            if not search_conditions:
                return []

            # Combine search conditions with OR
            query = select(self.model).where(or_(*search_conditions))
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching {self.model.__name__} objects: {e}")
            raise