"""
Data Access Object (DAO) package.

This package provides a clean abstraction layer for database operations
using the DAO pattern with async support.
"""

from .base import BaseDAO
from .file_dao import FileDAO, file_dao
from .directory_dao import DirectoryDAO, directory_dao
from .search_history_dao import SearchHistoryDAO, search_history_dao
from .tag_dao import TagDAO, tag_dao
from .user_settings_dao import UserSettingsDAO, user_settings_dao

__all__ = [
    "BaseDAO",
    "FileDAO",
    "file_dao",
    "DirectoryDAO",
    "directory_dao",
    "SearchHistoryDAO",
    "search_history_dao",
    "TagDAO",
    "tag_dao",
    "UserSettingsDAO",
    "user_settings_dao",
]