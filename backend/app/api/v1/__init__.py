"""
API v1 路由包
提供模块化的API路由结构和统一的错误处理
"""

import logging
from fastapi import APIRouter

from app.api.v1.endpoints import search, files, directories, users, settings, database
from app.api.exceptions import (
    XiaoyaoSearchException,
    xiaoyao_search_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

logger = logging.getLogger(__name__)

# 创建API路由器
api_router = APIRouter(
    tags=["API v1"],
    responses={
        400: {"description": "请求参数错误"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
        404: {"description": "资源未找到"},
        422: {"description": "请求参数验证失败"},
        500: {"description": "服务器内部错误"}
    }
)

# 异常处理器在主应用中注册，不在路由器中注册

# 包含所有端点路由
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["搜索"],
    responses={
        200: {"description": "搜索成功"},
        400: {"description": "搜索参数错误"},
        500: {"description": "搜索服务异常"}
    }
)

api_router.include_router(
    files.router,
    prefix="/files",
    tags=["文件管理"],
    responses={
        200: {"description": "操作成功"},
        404: {"description": "文件不存在"},
        409: {"description": "文件冲突"}
    }
)

api_router.include_router(
    directories.router,
    prefix="/directories",
    tags=["目录管理"],
    responses={
        200: {"description": "操作成功"},
        404: {"description": "目录不存在"},
        409: {"description": "目录冲突"}
    }
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"],
    responses={
        200: {"description": "操作成功"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"}
    }
)

api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["设置管理"],
    responses={
        200: {"description": "操作成功"},
        400: {"description": "设置参数错误"},
        422: {"description": "设置格式错误"}
    }
)

api_router.include_router(
    database.router,
    prefix="/database",
    tags=["数据库管理"],
    responses={
        200: {"description": "操作成功"},
        500: {"description": "数据库操作失败"},
        503: {"description": "数据库不可用"}
    }
)

# API信息端点
@api_router.get("/info", summary="获取API信息", description="获取API版本和配置信息")
async def api_info():
    """获取API版本和配置信息"""
    from app.core.config import settings

    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "小遥搜索API v1 - 跨平台本地文件智能搜索服务",
        "environment": "development" if settings.DEBUG else "production",
        "docs_url": "/v1/docs",
        "redoc_url": "/v1/redoc",
        "openapi_url": "/v1/openapi.json",
        "endpoints": {
            "search": "/v1/search",
            "files": "/v1/files",
            "directories": "/v1/directories",
            "users": "/v1/users",
            "settings": "/v1/settings",
            "database": "/v1/database"
        }
    }