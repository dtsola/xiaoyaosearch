"""
Database configuration and session management.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from sqlalchemy.engine import Engine

from core.config import settings

logger = logging.getLogger(__name__)

# SQLite-specific configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # Enable SQLite foreign key support and WAL mode for better performance
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable SQLite foreign keys and WAL mode."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and performance
        cursor.execute("PRAGMA cache_size=10000")  # Increase cache size
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temporary tables in memory
        cursor.close()

# Create async engine with configuration appropriate for database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,  # SQLite specific
            "timeout": 30,  # Connection timeout in seconds
        }
    )
else:
    # Configuration for other databases (PostgreSQL, MySQL, etc.)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        # General connection pool settings for non-SQLite databases
        pool_size=10,  # Number of connections to keep open
        max_overflow=20,  # Additional connections when pool is full
        pool_timeout=30,  # Timeout getting connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

# Create async session factory with better configuration
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session for dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions with transaction management.

    Usage:
        async with get_db_session() as session:
            # Database operations here
            result = await session.execute(query)

    Yields:
        AsyncSession: Database session with automatic transaction management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseManager:
    """Database manager for advanced operations."""

    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.session_factory() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def close(self):
        """Close database connections."""
        await self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()