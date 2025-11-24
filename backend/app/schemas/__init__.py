"""
Pydantic数据模型包初始化
导出所有请求和响应模型
"""

# 枚举类型
from app.schemas.enums import (
    InputType,
    SearchType,
    FileType,
    JobType,
    JobStatus,
    ModelType,
    ProviderType
)

# 请求模型
from app.schemas.requests import (
    SearchRequest,
    MultimodalRequest,
    IndexCreateRequest,
    IndexUpdateRequest,
    AIModelConfigRequest,
    AIModelTestRequest,
    SettingsUpdateRequest,
    SearchHistoryRequest,
    FileListRequest
)

# 响应模型
from app.schemas.responses import (
    SearchResult,
    SearchResponse,
    MultimodalResponse,
    FileInfo,
    IndexJobInfo,
    IndexCreateResponse,
    IndexListResponse,
    AIModelInfo,
    AIModelsResponse,
    AIModelTestResponse,
    SearchHistoryInfo,
    SearchHistoryResponse,
    FileInfoExtended,
    FileListResponse,
    SettingsResponse,
    HealthResponse,
    ErrorResponse,
    SuccessResponse
)

__all__ = [
    # 枚举类型
    "InputType",
    "SearchType",
    "FileType",
    "JobType",
    "JobStatus",
    "ModelType",
    "ProviderType",

    # 请求模型
    "SearchRequest",
    "MultimodalRequest",
    "IndexCreateRequest",
    "IndexUpdateRequest",
    "AIModelConfigRequest",
    "AIModelTestRequest",
    "SettingsUpdateRequest",
    "SearchHistoryRequest",
    "FileListRequest",

    # 响应模型
    "SearchResult",
    "SearchResponse",
    "MultimodalResponse",
    "FileInfo",
    "IndexJobInfo",
    "IndexCreateResponse",
    "IndexListResponse",
    "AIModelInfo",
    "AIModelsResponse",
    "AIModelTestResponse",
    "SearchHistoryInfo",
    "SearchHistoryResponse",
    "FileInfoExtended",
    "FileListResponse",
    "SettingsResponse",
    "HealthResponse",
    "ErrorResponse",
    "SuccessResponse"
]