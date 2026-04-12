# backend/app/schemas/glossary.py
"""
术语库相关的Pydantic模式定义
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


# ==================== 术语库Schema ====================

class GlossaryCollectionBase(BaseModel):
    """术语库基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="术语库名称")
    description: Optional[str] = Field(None, description="术语库描述")
    icon: Optional[str] = Field(None, max_length=50, description="图标（emoji）")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")


class GlossaryCollectionCreate(GlossaryCollectionBase):
    """创建术语库请求模式"""
    pass


class GlossaryCollectionUpdate(GlossaryCollectionBase):
    """更新术语库请求模式"""
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class GlossaryCollectionResponse(GlossaryCollectionBase):
    """术语库响应模式"""
    id: int
    is_enabled: bool
    term_count: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryCollectionListResponse(BaseModel):
    """术语库列表响应模式"""
    items: List[GlossaryCollectionResponse]
    total: int
    page: int
    page_size: int


# ==================== 术语Schema ====================

class GlossaryTermBase(BaseModel):
    """术语基础模式"""
    term: str = Field(..., min_length=1, max_length=100, description="术语名称")
    synonyms: List[str] = Field(..., min_length=1, description="同义词列表")
    description: Optional[str] = Field(None, description="术语描述")
    examples: Optional[List[str]] = Field(None, description="示例用法")

    @field_validator('synonyms')
    @classmethod
    def validate_synonyms(cls, v):
        """验证同义词列表"""
        if not v or len(v) == 0:
            raise ValueError('同义词列表不能为空')
        # 去重
        return list(set(v))


class GlossaryTermCreate(GlossaryTermBase):
    """创建术语请求模式"""
    pass


class GlossaryTermUpdate(BaseModel):
    """更新术语请求模式"""
    term: Optional[str] = Field(None, min_length=1, max_length=100, description="术语名称")
    synonyms: Optional[List[str]] = Field(None, min_length=1, description="同义词列表")
    description: Optional[str] = Field(None, description="术语描述")
    examples: Optional[List[str]] = Field(None, description="示例用法")
    is_enabled: Optional[bool] = Field(None, description="是否启用")

    @field_validator('synonyms')
    @classmethod
    def validate_synonyms_optional(cls, v):
        """验证同义词列表（可选）"""
        if v is not None and len(v) == 0:
            raise ValueError('同义词列表不能为空')
        # 去重
        return list(set(v)) if v else v


class GlossaryTermResponse(GlossaryTermBase):
    """术语响应模式"""
    id: int
    collection_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryTermListResponse(BaseModel):
    """术语列表响应模式"""
    collection_id: int
    collection_name: str
    items: List[GlossaryTermResponse]
    total: int
    page: int
    page_size: int


# ==================== 查询扩展Schema ====================

class GlossaryExpandRequest(BaseModel):
    """查询扩展请求模式"""
    query: str = Field(..., min_length=1, description="查询词")
    collection_ids: Optional[List[int]] = Field(None, description="术语库ID列表，null表示全部")


class MatchedTerm(BaseModel):
    """匹配的术语"""
    id: int
    term: str
    synonyms: List[str]
    collection_id: int
    collection_name: str


class GlossaryExpandResponse(BaseModel):
    """查询扩展响应模式"""
    original_query: str
    matched_terms: List[MatchedTerm]
    expanded_queries: List[str]
    used_collections: List[str]


# ==================== CSV导入导出Schema ====================

class GlossaryImportResponse(BaseModel):
    """CSV导入响应模式"""
    imported_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="失败数量")
    errors: List[dict] = Field(default_factory=list, description="错误详情")


# ==================== 用户设置Schema ====================

class GlossarySettingsUpdate(BaseModel):
    """术语库设置更新模式"""
    enable_expansion: bool = Field(..., description="是否启用术语扩展")
    default_mode: str = Field(..., pattern="^(all|custom)$", description="默认模式：all或custom")
    selected_collections: Optional[List[int]] = Field(None, description="选中的术语库ID列表（仅custom模式）")
