"""
API请求数据模型
定义所有API接口的请求参数结构
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from app.schemas.enums import (
    InputType, SearchType, FileType, JobType,
    ModelType, ProviderType
)


class SearchRequest(BaseModel):
    """
    搜索请求模型

    用于执行文件搜索的请求参数
    """
    query: str = Field(..., description="搜索查询词", min_length=1, max_length=500)
    input_type: InputType = Field("text", description="输入类型")
    search_type: SearchType = Field("hybrid", description="搜索类型")
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="相似度阈值")
    file_types: Optional[List[FileType]] = Field(None, description="文件类型过滤")

    class Config:
        """Pydantic配置"""
        use_enum_values = True


class MultimodalRequest(BaseModel):
    """
    多模态搜索请求模型

    用于处理语音和图片搜索的请求参数
    """
    input_data: str = Field(..., description="Base64编码的文件数据")
    input_type: InputType = Field(..., description="输入类型voice或image")
    duration: Optional[int] = Field(30, ge=1, le=120, description="音频最长时长秒数")
    search_type: SearchType = Field(SearchType.HYBRID, description="搜索类型")
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="相似度阈值")

    @validator('input_type')
    def validate_multimodal_input(cls, v):
        """验证多模态输入类型"""
        if v not in [InputType.VOICE, InputType.IMAGE]:
            raise ValueError('多模态输入类型只能是voice或image')
        return v

    class Config:
        use_enum_values = True


class IndexCreateRequest(BaseModel):
    """
    索引创建请求模型

    用于创建文件索引的请求参数
    """
    folder_path: str = Field(..., description="索引文件夹路径")
    file_types: List[str] = Field(
        default=None,
        description="支持文件类型"
    )
    recursive: bool = Field(True, description="是否递归搜索子文件夹")

    @validator('folder_path')
    def validate_folder_path(cls, v):
        """验证文件夹路径"""
        if not v or not v.strip():
            raise ValueError('文件夹路径不能为空')
        return v.strip()


class IndexUpdateRequest(BaseModel):
    """
    索引更新请求模型

    用于更新文件索引的请求参数
    """
    folder_path: str = Field(..., description="索引文件夹路径")
    file_types: Optional[List[str]] = Field(None, description="支持文件类型")
    recursive: bool = Field(True, description="是否递归搜索子文件夹")


class AIModelConfigRequest(BaseModel):
    """
    AI模型配置请求模型

    用于配置AI模型参数的请求结构
    """
    model_type: ModelType = Field(..., description="模型类型")
    provider: ProviderType = Field(..., description="提供商类型")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    config: Dict[str, Any] = Field(..., description="模型配置参数")

    @validator('model_name')
    def validate_model_name(cls, v):
        """验证模型名称"""
        if not v or not v.strip():
            raise ValueError('模型名称不能为空')
        return v.strip()

    class Config:
        use_enum_values = True


class AIModelTestRequest(BaseModel):
    """
    AI模型测试请求模型

    用于测试AI模型连通性的请求参数
    """
    test_data: Optional[str] = Field("测试数据", description="测试数据")
    config_override: Optional[Dict[str, Any]] = Field(None, description="临时配置覆盖")


class SettingsUpdateRequest(BaseModel):
    """
    应用设置更新请求模型

    用于更新应用配置的请求参数
    """
    search: Optional[Dict[str, Any]] = Field(None, description="搜索相关设置")
    indexing: Optional[Dict[str, Any]] = Field(None, description="索引相关设置")
    ui: Optional[Dict[str, Any]] = Field(None, description="界面相关设置")
    ai_models: Optional[Dict[str, Any]] = Field(None, description="AI模型相关设置")


class SearchHistoryRequest(BaseModel):
    """
    搜索历史请求模型

    用于查询搜索历史的请求参数
    """
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")
    offset: int = Field(0, ge=0, description="偏移量")
    search_type: Optional[SearchType] = Field(None, description="搜索类型过滤")
    input_type: Optional[InputType] = Field(None, description="输入类型过滤")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYY-MM-DD)")

    class Config:
        use_enum_values = True


class FileListRequest(BaseModel):
    """
    文件列表请求模型

    用于查询已索引文件列表的请求参数
    """
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")
    offset: int = Field(0, ge=0, description="偏移量")
    file_type: Optional[FileType] = Field(None, description="文件类型过滤")
    search_query: Optional[str] = Field(None, min_length=1, max_length=100, description="文件名搜索")

    class Config:
        use_enum_values = True