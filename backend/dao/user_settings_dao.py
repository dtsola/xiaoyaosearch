"""
User Settings Data Access Object (DAO) implementation.
"""

import logging
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func

from model.user_settings import UserSettings
from dao.base import BaseDAO

logger = logging.getLogger(__name__)


class UserSettingsDAO(BaseDAO[UserSettings, Dict[str, Any], Dict[str, Any]]):
    """User Settings DAO with specific settings operations."""

    def __init__(self):
        super().__init__(UserSettings)

    async def get_by_key(
        self,
        db: AsyncSession,
        *,
        key: str
    ) -> Optional[UserSettings]:
        """
        Get a setting by key.

        Args:
            db: Database session
            key: Setting key

        Returns:
            UserSettings object or None
        """
        try:
            query = select(UserSettings).where(UserSettings.key == key)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting setting by key '{key}': {e}")
            raise

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category: str
    ) -> List[UserSettings]:
        """
        Get settings by category.

        Args:
            db: Database session
            category: Setting category

        Returns:
            List of settings
        """
        try:
            filters = {"category": category}
            return await self.get_multi(
                db=db,
                filters=filters,
                order_by="key"
            )
        except Exception as e:
            logger.error(f"Error getting settings by category '{category}': {e}")
            raise

    async def get_setting_value(
        self,
        db: AsyncSession,
        *,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get setting value with default fallback.

        Args:
            db: Database session
            key: Setting key
            default: Default value if setting doesn't exist

        Returns:
            Setting value or default
        """
        try:
            setting = await self.get_by_key(db, key=key)
            if setting:
                return self._parse_value(setting.value, setting.data_type)
            return default
        except Exception as e:
            logger.error(f"Error getting setting value for '{key}': {e}")
            raise

    async def set_setting(
        self,
        db: AsyncSession,
        *,
        key: str,
        value: Any,
        category: str = "general",
        description: Optional[str] = None,
        data_type: str = "string"
    ) -> UserSettings:
        """
        Set a setting value.

        Args:
            db: Database session
            key: Setting key
            value: Setting value
            category: Setting category
            description: Setting description
            data_type: Data type (string, integer, boolean, json)

        Returns:
            Created or updated setting
        """
        try:
            from datetime import datetime

            # Check if setting exists
            existing_setting = await self.get_by_key(db, key=key)

            setting_data = {
                "key": key,
                "value": self._serialize_value(value, data_type),
                "category": category,
                "description": description,
                "data_type": data_type,
                "updated_at": datetime.utcnow()
            }

            if existing_setting:
                # Update existing setting
                updated_setting = await self.update(db, db_obj=existing_setting, obj_in=setting_data)
                return updated_setting
            else:
                # Create new setting
                setting_data["created_at"] = datetime.utcnow()
                new_setting = await self.create(db, obj_in=setting_data)
                return new_setting
        except Exception as e:
            logger.error(f"Error setting value for '{key}': {e}")
            raise

    async def get_settings_dict(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get settings as a dictionary.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            Dictionary of setting key-value pairs
        """
        try:
            filters = {}
            if category:
                filters["category"] = category

            settings = await self.get_multi(db=db, filters=filters)

            result = {}
            for setting in settings:
                result[setting.key] = self._parse_value(setting.value, setting.data_type)

            return result
        except Exception as e:
            logger.error(f"Error getting settings dict: {e}")
            raise

    async def delete_setting(
        self,
        db: AsyncSession,
        *,
        key: str
    ) -> bool:
        """
        Delete a setting by key.

        Args:
            db: Database session
            key: Setting key

        Returns:
            True if setting was deleted, False if not found
        """
        try:
            setting = await self.get_by_key(db, key=key)
            if setting:
                await db.delete(setting)
                await db.flush()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting setting '{key}': {e}")
            raise

    async def get_categories(
        self,
        db: AsyncSession
    ) -> List[str]:
        """
        Get all unique setting categories.

        Args:
            db: Database session

        Returns:
            List of category names
        """
        try:
            query = select(UserSettings.category).where(UserSettings.category.isnot(None)).distinct().order_by(UserSettings.category)
            result = await db.execute(query)
            return [row.category for row in result.all()]
        except Exception as e:
            logger.error(f"Error getting setting categories: {e}")
            raise

    async def reset_category(
        self,
        db: AsyncSession,
        *,
        category: str,
        defaults: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Reset all settings in a category to defaults.

        Args:
            db: Database session
            category: Category to reset
            defaults: Default values to set

        Returns:
            Number of settings reset
        """
        try:
            from datetime import datetime

            if defaults:
                # Update with provided defaults
                updated_count = 0
                for key, value in defaults.items():
                    await self.set_setting(
                        db=db,
                        key=key,
                        value=value,
                        category=category
                    )
                    updated_count += 1
                return updated_count
            else:
                # Delete all settings in category
                query = select(UserSettings).where(UserSettings.category == category)
                result = await db.execute(query)
                settings = result.scalars().all()

                for setting in settings:
                    await db.delete(setting)

                await db.flush()
                return len(settings)
        except Exception as e:
            logger.error(f"Error resetting category '{category}': {e}")
            raise

    async def backup_settings(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a backup of settings.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            Dictionary containing settings backup
        """
        try:
            from datetime import datetime

            filters = {}
            if category:
                filters["category"] = category

            settings = await self.get_multi(db=db, filters=filters)

            backup = {
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "settings": [
                    {
                        "key": setting.key,
                        "value": setting.value,
                        "data_type": setting.data_type,
                        "description": setting.description,
                        "category": setting.category,
                        "created_at": setting.created_at.isoformat() if setting.created_at else None,
                        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
                    }
                    for setting in settings
                ]
            }

            return backup
        except Exception as e:
            logger.error(f"Error creating settings backup: {e}")
            raise

    async def restore_settings(
        self,
        db: AsyncSession,
        *,
        backup: Dict[str, Any],
        overwrite: bool = False
    ) -> int:
        """
        Restore settings from backup.

        Args:
            db: Database session
            backup: Settings backup dictionary
            overwrite: Whether to overwrite existing settings

        Returns:
            Number of settings restored
        """
        try:
            restored_count = 0

            for setting_data in backup.get("settings", []):
                key = setting_data["key"]

                # Check if setting exists and overwrite is False
                if not overwrite:
                    existing = await self.get_by_key(db, key=key)
                    if existing:
                        continue

                # Restore setting
                await self.set_setting(
                    db=db,
                    key=setting_data["key"],
                    value=self._parse_value(setting_data["value"], setting_data["data_type"]),
                    category=setting_data["category"],
                    description=setting_data.get("description"),
                    data_type=setting_data["data_type"]
                )
                restored_count += 1

            return restored_count
        except Exception as e:
            logger.error(f"Error restoring settings from backup: {e}")
            raise

    async def get_setting_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get settings statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with settings statistics
        """
        try:
            # Total settings
            total_query = select(func.count(UserSettings.id))
            total_result = await db.execute(total_query)
            total_settings = total_result.scalar() or 0

            # Settings by category
            category_query = (
                select(
                    UserSettings.category,
                    func.count(UserSettings.id).label('count')
                )
                .where(UserSettings.category.isnot(None))
                .group_by(UserSettings.category)
                .order_by(UserSettings.category)
            )
            category_result = await db.execute(category_query)
            category_stats = category_result.all()

            # Settings by data type
            type_query = (
                select(
                    UserSettings.data_type,
                    func.count(UserSettings.id).label('count')
                )
                .group_by(UserSettings.data_type)
                .order_by(UserSettings.data_type)
            )
            type_result = await db.execute(type_query)
            type_stats = type_result.all()

            return {
                "total_settings": total_settings,
                "by_category": [
                    {
                        "category": stat.category or "unknown",
                        "count": stat.count
                    }
                    for stat in category_stats
                ],
                "by_data_type": [
                    {
                        "data_type": stat.data_type or "unknown",
                        "count": stat.count
                    }
                    for stat in type_stats
                ]
            }
        except Exception as e:
            logger.error(f"Error getting settings statistics: {e}")
            raise

    def _parse_value(self, value: str, data_type: str) -> Any:
        """
        Parse a string value according to data type.

        Args:
            value: String value to parse
            data_type: Data type (string, integer, boolean, json)

        Returns:
            Parsed value
        """
        try:
            if value is None:
                return None

            if data_type == "integer":
                return int(value)
            elif data_type == "boolean":
                return value.lower() in ("true", "1", "yes", "on")
            elif data_type == "json":
                import json
                return json.loads(value)
            else:  # string or unknown
                return value
        except Exception as e:
            logger.warning(f"Error parsing value '{value}' as {data_type}: {e}")
            return value

    def _serialize_value(self, value: Any, data_type: str) -> str:
        """
        Serialize a value to string according to data type.

        Args:
            value: Value to serialize
            data_type: Data type (string, integer, boolean, json)

        Returns:
            Serialized string value
        """
        try:
            if value is None:
                return ""

            if data_type == "json":
                import json
                return json.dumps(value, default=str)
            else:  # string, integer, boolean
                return str(value)
        except Exception as e:
            logger.warning(f"Error serializing value '{value}' as {data_type}: {e}")
            return str(value)


# Create a singleton instance
user_settings_dao = UserSettingsDAO()