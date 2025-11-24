"""
全局异常处理器
统一处理API接口中的异常，返回标准格式的错误响应
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union

from app.core.exceptions import XiaoyaoSearchException
from app.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)


async def xiaoyao_search_exception_handler(
    request: Request,
    exc: XiaoyaoSearchException
) -> JSONResponse:
    """
    处理小遥搜索自定义异常

    Args:
        request: FastAPI请求对象
        exc: 小遥搜索自定义异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"小遥搜索异常: {exc.error_code} - {exc.message}")

    # 根据异常类型确定HTTP状态码
    status_code_map = {
        "VALIDATION_ERROR": 400,
        "DATABASE_ERROR": 500,
        "AI_SERVICE_ERROR": 503,
        "INDEX_ERROR": 500,
        "SEARCH_ERROR": 500,
        "FILE_OPERATION_ERROR": 400,
        "MODEL_LOAD_ERROR": 503,
        "CONFIGURATION_ERROR": 500,
        "RESOURCE_NOT_FOUND": 404,
        "PERMISSION_DENIED": 403,
        "RATE_LIMIT_EXCEEDED": 429,
        "INSUFFICIENT_RESOURCE": 503,
        "UNKNOWN_ERROR": 500
    }

    status_code = status_code_map.get(exc.error_code, 500)

    error_response = ErrorResponse(
        error={
            "code": exc.error_code,
            "message": exc.message,
            "type": type(exc).__name__
        },
        message=f"操作失败: {exc.message}"
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.dict()
    )


async def http_exception_handler(
    request: Request,
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """
    处理HTTP异常

    Args:
        request: FastAPI请求对象
        exc: HTTP异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")

    error_code_map = {
        400: "VALIDATION_ERROR",
        401: "UNAUTHORIZED",
        403: "PERMISSION_DENIED",
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

    error_response = ErrorResponse(
        error={
            "code": error_code,
            "message": exc.detail,
            "type": "HTTPException"
        },
        message=f"HTTP错误 {exc.status_code}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求验证异常

    Args:
        request: FastAPI请求对象
        exc: 请求验证异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"请求验证异常: {exc.errors()}")

    # 格式化验证错误信息
    error_details = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_details.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })

    error_response = ErrorResponse(
        error={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": error_details,
            "type": "RequestValidationError"
        },
        message="请求参数格式不正确"
    )

    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    处理Pydantic验证异常

    Args:
        request: FastAPI请求对象
        exc: Pydantic验证异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"Pydantic验证异常: {exc.errors()}")

    error_response = ErrorResponse(
        error={
            "code": "VALIDATION_ERROR",
            "message": "数据验证失败",
            "details": exc.errors(),
            "type": "ValidationError"
        },
        message="数据格式验证失败"
    )

    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    处理SQLAlchemy异常

    Args:
        request: FastAPI请求对象
        exc: SQLAlchemy异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"数据库异常: {type(exc).__name__} - {str(exc)}")

    error_response = ErrorResponse(
        error={
            "code": "DATABASE_ERROR",
            "message": "数据库操作失败",
            "type": "SQLAlchemyError"
        },
        message="数据库操作异常，请稍后重试"
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    处理通用异常

    Args:
        request: FastAPI请求对象
        exc: 通用异常

    Returns:
        JSONResponse: 标准错误响应
    """
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}", exc_info=True)

    error_response = ErrorResponse(
        error={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "type": type(exc).__name__
        },
        message="服务器遇到未知错误，请联系管理员"
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


def setup_exception_handlers(app) -> None:
    """
    设置应用的全局异常处理器

    Args:
        app: FastAPI应用实例
    """
    # 自定义异常处理器
    app.add_exception_handler(XiaoyaoSearchException, xiaoyao_search_exception_handler)

    # HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # 验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)

    # 数据库异常处理器
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

    # 通用异常处理器（必须放在最后）
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("异常处理器设置完成")