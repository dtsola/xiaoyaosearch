"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine
from db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Cleanup resources
    await engine.dispose()


# Create FastAPI application with lifespan management
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


# Include API routers
from api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Run the application when executed directly
if __name__ == "__main__":
    import uvicorn

    print(f"启动 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"API 文档: http://{settings.HOST}:{settings.PORT}{settings.API_V1_STR}/docs")

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )