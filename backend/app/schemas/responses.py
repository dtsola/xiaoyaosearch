"""
API响应数据模型
定义所有API接口的响应数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from app.schemas.enums import (
    InputType, SearchType, FileType, JobType, JobStatus,
    ModelType, ProviderType
)


class SearchResult(BaseModel):
    """
    搜索结果模型

    单个搜索结果的数据结构
    """
    file_id: int = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件绝对路径")
    file_type: FileType = Field(..., description="文件类型")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="相关性分数")
    preview_text: str = Field(..., max_length=200, description="预览文本")
    highlight: str = Field(..., description="高亮片段")
    created_at: datetime = Field(..., description="文件创建时间")
    modified_at: datetime = Field(..., description="文件修改时间")
    file_size: int = Field(..., description="文件大小(字节)")
    match_type: str = Field(..., description="匹配类型 semantic/fulltext/hybrid")

    class Config:
        use_enum_values = True


class SearchResponse(BaseModel):
    """
    搜索响应模型

    文本搜索的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")


class MultimodalResponse(BaseModel):
    """
    多模态搜索响应模型

    语音和图片搜索的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")


class FileInfo(BaseModel):
    """
    文件信息模型

    文件基本信息的数据结构
    """
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小")
    content_type: str = Field(..., description="MIME类型")


class IndexJobInfo(BaseModel):
    """
    索引任务信息模型

    索引任务状态的数据结构
    """
    index_id: int = Field(..., description="索引任务ID")
    folder_path: str = Field(..., description="索引文件夹路径")
    status: JobStatus = Field(..., description="任务状态")
    progress: int = Field(..., ge=0, le=100, description="进度百分比")
    total_files: int = Field(..., description="总文件数")
    processed_files: int = Field(..., description="已处理文件数")
    error_count: int = Field(..., description="错误文件数")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")

    class Config:
        use_enum_values = True


class IndexCreateResponse(BaseModel):
    """
    索引创建响应模型

    创建索引任务的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: IndexJobInfo = Field(..., description="索引任务信息")
    message: Optional[str] = Field(None, description="响应消息")


class IndexListResponse(BaseModel):
    """
    索引列表响应模型

    索引任务列表的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="索引列表数据")
    message: Optional[str] = Field(None, description="响应消息")


class AIModelInfo(BaseModel):
    """
    AI模型信息模型

    AI模型配置的数据结构
    """
    id: int = Field(..., description="模型配置ID")
    model_type: ModelType = Field(..., description="模型类型")
    provider: ProviderType = Field(..., description="提供商类型")
    model_name: str = Field(..., description="模型名称")
    config_json: str = Field(..., description="JSON格式配置参数")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        use_enum_values = True


class AIModelsResponse(BaseModel):
    """
    AI模型列表响应模型

    AI模型配置列表的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: List[AIModelInfo] = Field(..., description="AI模型配置列表")
    message: Optional[str] = Field(None, description="响应消息")


class AIModelTestResponse(BaseModel):
    """
    AI模型测试响应模型

    AI模型测试结果的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="测试结果数据")
    message: Optional[str] = Field(None, description="响应消息")


class SearchHistoryInfo(BaseModel):
    """
    搜索历史信息模型

    搜索历史记录的数据结构
    """
    id: int = Field(..., description="历史记录ID")
    search_query: str = Field(..., description="搜索查询")
    input_type: InputType = Field(..., description="输入类型")
    search_type: SearchType = Field(..., description="搜索类型")
    ai_model_used: Optional[str] = Field(None, description="使用的AI模型")
    result_count: int = Field(..., description="结果数量")
    response_time: float = Field(..., description="响应时间(秒)")
    created_at: datetime = Field(..., description="搜索时间")

    class Config:
        use_enum_values = True


class SearchHistoryResponse(BaseModel):
    """
    搜索历史响应模型

    搜索历史列表的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="搜索历史数据")
    message: Optional[str] = Field(None, description="响应消息")


class FileInfoExtended(BaseModel):
    """
    扩展文件信息模型

    包含索引状态的文件信息数据结构
    """
    id: int = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件绝对路径")
    file_type: FileType = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")
    created_at: datetime = Field(..., description="文件创建时间")
    modified_at: datetime = Field(..., description="文件修改时间")
    indexed_at: datetime = Field(..., description="索引时间")
    content_hash: str = Field(..., description="文件内容哈希")
    has_vector_index: bool = Field(..., description="是否有向量索引")
    has_fulltext_index: bool = Field(..., description="是否有全文索引")

    class Config:
        use_enum_values = True


class FileListResponse(BaseModel):
    """
    文件列表响应模型

    文件列表的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="文件列表数据")
    message: Optional[str] = Field(None, description="响应消息")


class SettingsResponse(BaseModel):
    """
    应用设置响应模型

    应用设置的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="设置数据")
    message: Optional[str] = Field(None, description="响应消息")


class HealthResponse(BaseModel):
    """
    健康检查响应模型

    系统健康状态的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="健康状态数据")
    message: Optional[str] = Field(None, description="响应消息")


class ErrorResponse(BaseModel):
    """
    错误响应模型

    统一的错误响应数据结构
    """
    success: bool = Field(False, description="请求是否成功")
    error: Dict[str, Any] = Field(..., description="错误信息")
    message: Optional[str] = Field(None, description="错误消息")


class SuccessResponse(BaseModel):
    """
    通用成功响应模型

    通用操作的响应数据结构
    """
    success: bool = Field(True, description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    message: str = Field("操作成功", description="响应消息")