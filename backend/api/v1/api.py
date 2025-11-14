"""
Main API router for version 1 endpoints.
"""

from fastapi import APIRouter

from api.v1.endpoints import files, directories, search, user_settings, tags, ai

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["files"]
)
api_router.include_router(
    directories.router,
    prefix="/directories",
    tags=["directories"]
)
api_router.include_router(
    user_settings.router,
    prefix="/settings",
    tags=["settings"]
)
api_router.include_router(
    tags.router,
    prefix="/tags",
    tags=["tags"]
)
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"]
)