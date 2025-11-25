"""
AI模型服务基类
定义所有AI模型服务的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
import traceback

from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """AI模型类型枚举"""
    EMBEDDING = "embedding"  # 文本嵌入模型
    SPEECH = "speech"       # 语音识别模型
    VISION = "vision"       # 图像理解模型
    LLM = "llm"            # 大语言模型


class ProviderType(Enum):
    """AI模型提供商类型枚举"""
    LOCAL = "local"  # 本地模型
    CLOUD = "cloud"  # 云端API


class ModelStatus(Enum):
    """AI模型状态枚举"""
    UNLOADED = "unloaded"    # 未加载
    LOADING = "loading"      # 加载中
    LOADED = "loaded"        # 已加载
    ERROR = "error"          # 错误状态


class AIModelException(Exception):
    """AI模型服务异常类"""
    def __init__(self, message: str, error_code: str = None, model_name: str = None):
        self.message = message
        self.error_code = error_code
        self.model_name = model_name
        super().__init__(self.message)


class BaseAIModel(ABC):
    """
    AI模型服务基类

    所有AI模型服务必须继承此基类并实现抽象方法
    """

    def __init__(self, model_name: str, model_type: ModelType, provider: ProviderType, config: Dict[str, Any]):
        """
        初始化AI模型服务

        Args:
            model_name: 模型名称
            model_type: 模型类型
            provider: 提供商类型
            config: 模型配置参数
        """
        self.model_name = model_name
        self.model_type = model_type
        self.provider = provider
        self.config = config
        self.status = ModelStatus.UNLOADED
        self.model = None
        self.load_time = None
        self.last_used_time = None
        self.error_message = None
        self.usage_count = 0

        logger.info(f"初始化{get_enum_value(model_type)}模型: {model_name} ({get_enum_value(provider)})")

    @abstractmethod
    async def load_model(self) -> bool:
        """
        加载模型

        Returns:
            bool: 加载是否成功

        Raises:
            AIModelException: 模型加载失败时抛出异常
        """
        pass

    @abstractmethod
    async def unload_model(self) -> bool:
        """
        卸载模型

        Returns:
            bool: 卸载是否成功
        """
        pass

    @abstractmethod
    async def predict(self, inputs: Any, **kwargs) -> Any:
        """
        模型推理预测

        Args:
            inputs: 输入数据
            **kwargs: 其他预测参数

        Returns:
            Any: 预测结果

        Raises:
            AIModelException: 预测失败时抛出异常
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息字典
        """
        pass

    async def health_check(self) -> bool:
        """
        模型健康检查

        Returns:
            bool: 模型是否健康可用
        """
        try:
            if self.status != ModelStatus.LOADED:
                return False

            # 执行简单的预测测试
            test_input = self._get_test_input()
            await self.predict(test_input)
            return True

        except Exception as e:
            logger.error(f"模型{self.model_name}健康检查失败: {str(e)}")
            return False

    def _get_test_input(self) -> Any:
        """
        获取健康检查的测试输入

        子类应该重写此方法提供合适的测试输入

        Returns:
            Any: 测试输入数据
        """
        return "测试输入"

    def update_status(self, status: ModelStatus, error_message: str = None):
        """
        更新模型状态

        Args:
            status: 新状态
            error_message: 错误信息（可选）
        """
        self.status = status
        self.error_message = error_message

        if status == ModelStatus.LOADED:
            self.load_time = datetime.now()
        elif status == ModelStatus.ERROR:
            logger.error(f"模型{self.model_name}状态错误: {error_message}")

    def record_usage(self):
        """记录模型使用"""
        self.usage_count += 1
        self.last_used_time = datetime.now()

    def get_status_info(self) -> Dict[str, Any]:
        """
        获取模型状态信息

        Returns:
            Dict[str, Any]: 状态信息字典
        """
        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "status": get_enum_value(self.status),
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "last_used_time": self.last_used_time.isoformat() if self.last_used_time else None,
            "usage_count": self.usage_count,
            "error_message": self.error_message,
            "config": self.config
        }

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.load_model()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.unload_model()

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<{self.__class__.__name__}(name={self.model_name}, type={get_enum_value(self.model_type)}, status={get_enum_value(self.status)})>"


class ModelManager:
    """
    AI模型管理器

    负责管理多个AI模型实例的生命周期
    """

    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        logger.info("AI模型管理器初始化完成")

    def register_model(self, model_id: str, model: BaseAIModel):
        """
        注册AI模型

        Args:
            model_id: 模型唯一标识
            model: AI模型实例
        """
        self.models[model_id] = model
        logger.info(f"注册AI模型: {model_id} -> {model.model_name}")

    def unregister_model(self, model_id: str):
        """
        注销AI模型

        Args:
            model_id: 模型唯一标识
        """
        if model_id in self.models:
            model = self.models.pop(model_id)
            logger.info(f"注销AI模型: {model_id} -> {model.model_name}")

    def get_model(self, model_id: str) -> Optional[BaseAIModel]:
        """
        获取AI模型实例

        Args:
            model_id: 模型唯一标识

        Returns:
            Optional[BaseAIModel]: 模型实例或None
        """
        return self.models.get(model_id)

    async def load_model(self, model_id: str) -> bool:
        """
        加载指定模型

        Args:
            model_id: 模型唯一标识

        Returns:
            bool: 加载是否成功
        """
        model = self.get_model(model_id)
        if model:
            return await model.load_model()
        return False

    async def unload_model(self, model_id: str) -> bool:
        """
        卸载指定模型

        Args:
            model_id: 模型唯一标识

        Returns:
            bool: 卸载是否成功
        """
        model = self.get_model(model_id)
        if model:
            return await model.unload_model()
        return False

    async def load_all_models(self) -> Dict[str, bool]:
        """
        加载所有模型

        Returns:
            Dict[str, bool]: 每个模型的加载结果
        """
        results = {}
        for model_id, model in self.models.items():
            try:
                results[model_id] = await model.load_model()
            except Exception as e:
                logger.error(f"加载模型{model_id}失败: {str(e)}")
                results[model_id] = False
        return results

    async def unload_all_models(self) -> Dict[str, bool]:
        """
        卸载所有模型

        Returns:
            Dict[str, bool]: 每个模型的卸载结果
        """
        results = {}
        for model_id, model in self.models.items():
            try:
                results[model_id] = await model.unload_model()
            except Exception as e:
                logger.error(f"卸载模型{model_id}失败: {str(e)}")
                results[model_id] = False
        return results

    async def health_check_all(self) -> Dict[str, bool]:
        """
        检查所有模型健康状态

        Returns:
            Dict[str, bool]: 每个模型的健康状态
        """
        results = {}
        for model_id, model in self.models.items():
            try:
                results[model_id] = await model.health_check()
            except Exception as e:
                logger.error(f"检查模型{model_id}健康状态失败: {str(e)}")
                results[model_id] = False
        return results

    def get_models_by_type(self, model_type: ModelType) -> List[BaseAIModel]:
        """
        根据类型获取模型列表

        Args:
            model_type: 模型类型

        Returns:
            List[BaseAIModel]: 模型列表
        """
        return [model for model in self.models.values() if model.model_type == model_type]

    def get_active_models(self) -> List[BaseAIModel]:
        """
        获取所有活跃的模型

        Returns:
            List[BaseAIModel]: 活跃模型列表
        """
        return [model for model in self.models.values() if model.status == ModelStatus.LOADED]

    def get_status_summary(self) -> Dict[str, Any]:
        """
        获取所有模型状态摘要

        Returns:
            Dict[str, Any]: 状态摘要
        """
        summary = {
            "total_models": len(self.models),
            "loaded_models": len([m for m in self.models.values() if m.status == ModelStatus.LOADED]),
            "error_models": len([m for m in self.models.values() if m.status == ModelStatus.ERROR]),
            "models": {}
        }

        for model_id, model in self.models.items():
            summary["models"][model_id] = model.get_status_info()

        return summary

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.load_all_models()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.unload_all_models()


# 全局模型管理器实例
model_manager = ModelManager()