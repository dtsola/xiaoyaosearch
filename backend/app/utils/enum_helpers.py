"""
枚举类型处理的辅助函数
解决Pydantic模型中use_enum_values=True导致的枚举处理问题
"""
from typing import Union, Any
from app.schemas.enums import (
    InputType, SearchType, FileType, JobType, JobStatus,
    ModelType, ProviderType
)


def get_enum_value(enum_obj: Union[InputType, SearchType, FileType, JobType, JobStatus, ModelType, ProviderType, str]) -> str:
    """
    安全地获取枚举值，处理已序列化的字符串和枚举对象两种情况

    Args:
        enum_obj: 枚举对象或字符串值

    Returns:
        str: 枚举的字符串值
    """
    if enum_obj is None:
        return ""

    # 如果已经是字符串，直接返回
    if isinstance(enum_obj, str):
        return enum_obj

    # 如果是枚举对象，获取其value属性
    try:
        if hasattr(enum_obj, 'value'):
            return enum_obj.value
        return str(enum_obj)
    except Exception as e:
        # 如果出现任何错误，记录警告并返回字符串形式
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"获取枚举值时出错: {e}, 对象类型: {type(enum_obj)}, 对象值: {repr(enum_obj)}")
        return str(enum_obj) if enum_obj else ""


def get_enum_safe(enum_field: Any, default_value: str = "") -> str:
    """
    安全地获取枚举字段的值，提供默认值

    Args:
        enum_field: 可能是枚举对象、字符串或None
        default_value: 默认值

    Returns:
        str: 枚举值或默认值
    """
    if enum_field is None:
        return default_value
    return get_enum_value(enum_field)


def compare_enum_with_value(enum_obj: Union[InputType, SearchType, FileType, JobType, JobStatus, ModelType, ProviderType, str],
                           target_value: str) -> bool:
    """
    比较枚举对象与目标值

    Args:
        enum_obj: 枚举对象或字符串值
        target_value: 目标字符串值

    Returns:
        bool: 是否匹配
    """
    return get_enum_value(enum_obj) == target_value


def compare_enum_with_enum(enum_obj1: Union[InputType, SearchType, FileType, JobType, JobStatus, ModelType, ProviderType, str],
                          enum_obj2: Union[InputType, SearchType, FileType, JobType, JobStatus, ModelType, ProviderType, str]) -> bool:
    """
    比较两个枚举对象

    Args:
        enum_obj1: 第一个枚举对象或字符串值
        enum_obj2: 第二个枚举对象或字符串值

    Returns:
        bool: 是否匹配
    """
    return get_enum_value(enum_obj1) == get_enum_value(enum_obj2)


# 常用的枚举比较函数
def is_embedding_model(model_type: Union[ModelType, str]) -> bool:
    """检查是否为嵌入模型"""
    return compare_enum_with_value(model_type, "embedding")


def is_speech_model(model_type: Union[ModelType, str]) -> bool:
    """检查是否为语音模型"""
    return compare_enum_with_value(model_type, "speech")


def is_vision_model(model_type: Union[ModelType, str]) -> bool:
    """检查是否为视觉模型"""
    return compare_enum_with_value(model_type, "vision")


def is_llm_model(model_type: Union[ModelType, str]) -> bool:
    """检查是否为语言模型"""
    return compare_enum_with_value(model_type, "llm")


def is_local_provider(provider: Union[ProviderType, str]) -> bool:
    """检查是否为本地提供商"""
    return compare_enum_with_value(provider, "local")


def is_cloud_provider(provider: Union[ProviderType, str]) -> bool:
    """检查是否为云端提供商"""
    return compare_enum_with_value(provider, "cloud")


def is_semantic_search(search_type: Union[SearchType, str]) -> bool:
    """检查是否为语义搜索"""
    return compare_enum_with_value(search_type, "semantic")


def is_fulltext_search(search_type: Union[SearchType, str]) -> bool:
    """检查是否为全文搜索"""
    return compare_enum_with_value(search_type, "fulltext")


def is_hybrid_search(search_type: Union[SearchType, str]) -> bool:
    """检查是否为混合搜索"""
    return compare_enum_with_value(search_type, "hybrid")


def is_text_input(input_type: Union[InputType, str]) -> bool:
    """检查是否为文本输入"""
    return compare_enum_with_value(input_type, "text")


def is_voice_input(input_type: Union[InputType, str]) -> bool:
    """检查是否为语音输入"""
    return compare_enum_with_value(input_type, "voice")


def is_image_input(input_type: Union[InputType, str]) -> bool:
    """检查是否为图片输入"""
    return compare_enum_with_value(input_type, "image")


def is_pending_status(status: Union[JobStatus, str]) -> bool:
    """检查是否为等待状态"""
    return compare_enum_with_value(status, "pending")


def is_processing_status(status: Union[JobStatus, str]) -> bool:
    """检查是否为处理中状态"""
    return compare_enum_with_value(status, "processing")


def is_completed_status(status: Union[JobStatus, str]) -> bool:
    """检查是否为完成状态"""
    return compare_enum_with_value(status, "completed")


def is_failed_status(status: Union[JobStatus, str]) -> bool:
    """检查是否为失败状态"""
    return compare_enum_with_value(status, "failed")