"""
自定义异常类定义
定义应用中使用的各种异常类型
"""


class XiaoyaoSearchException(Exception):
    """
    小遥搜索基础异常类
    """
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        super().__init__(self.message)


class ValidationException(XiaoyaoSearchException):
    """
    数据验证异常
    """
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseException(XiaoyaoSearchException):
    """
    数据库操作异常
    """
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class AIServiceException(XiaoyaoSearchException):
    """
    AI服务异常
    """
    def __init__(self, message: str, model_type: str = None):
        self.model_type = model_type
        super().__init__(message, "AI_SERVICE_ERROR")


class IndexException(XiaoyaoSearchException):
    """
    索引操作异常
    """
    def __init__(self, message: str):
        super().__init__(message, "INDEX_ERROR")


class SearchException(XiaoyaoSearchException):
    """
    搜索操作异常
    """
    def __init__(self, message: str):
        super().__init__(message, "SEARCH_ERROR")


class FileOperationException(XiaoyaoSearchException):
    """
    文件操作异常
    """
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message, "FILE_OPERATION_ERROR")


class ModelLoadException(AIServiceException):
    """
    模型加载异常
    """
    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        super().__init__(message, "MODEL_LOAD_ERROR")


class ConfigurationException(XiaoyaoSearchException):
    """
    配置异常
    """
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")


class ResourceNotFoundException(XiaoyaoSearchException):
    """
    资源未找到异常
    """
    def __init__(self, resource_type: str, resource_id: str = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type}未找到"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, "RESOURCE_NOT_FOUND")


class PermissionDeniedException(XiaoyaoSearchException):
    """
    权限拒绝异常
    """
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "PERMISSION_DENIED")


class RateLimitExceededException(XiaoyaoSearchException):
    """
    频率限制异常
    """
    def __init__(self, message: str = "请求频率超限"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


class InsufficientResourceException(XiaoyaoSearchException):
    """
    资源不足异常
    """
    def __init__(self, resource_type: str, message: str = None):
        self.resource_type = resource_type
        if not message:
            message = f"{resource_type}不足"
        super().__init__(message, "INSUFFICIENT_RESOURCE")