"""
OpenAI兼容的大语言模型服务
支持所有兼容OpenAI API标准的供应商（OpenAI、阿里云、DeepSeek、Moonshot等）
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

import aiohttp

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """聊天消息数据类"""
    role: str  # system, user, assistant
    content: str


class OpenAILLMService(BaseAIModel):
    """
    OpenAI兼容的大语言模型服务

    支持所有兼容OpenAI API标准的供应商：
    - OpenAI 官方
    - 阿里云通义千问
    - DeepSeek
    - Moonshot
    - 其他兼容 OpenAI API 标准的服务
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化OpenAI兼容大语言模型服务

        Args:
            config: 模型配置参数，包含：
                - api_key: API密钥 (必需)
                - endpoint: API端点地址 (可选，默认 https://api.openai.com/v1)
                - model: 模型名称 (必需)
                - timeout: 请求超时时间(秒)
                - temperature: 温度参数
                - max_tokens: 最大生成token数
        """
        if config is None:
            config = {}

        # 验证必需参数
        if "api_key" not in config or not config["api_key"]:
            raise ValueError("api_key 是必需参数")

        if "model" not in config or not config["model"]:
            raise ValueError("model 是必需参数")

        # 默认配置
        default_config = {
            "endpoint": "https://api.openai.com/v1",
            "timeout": 60,
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 1.0,
        }

        default_config.update(config)

        # MiniMax 特殊处理：temperature 范围为 (0.0, 1.0]，不能为 0
        model_name = default_config.get("model", "")
        if model_name.lower().startswith("minimax"):
            if default_config.get("temperature", 0.7) <= 0:
                default_config["temperature"] = 1.0
            # MiniMax 默认使用海外端点
            if default_config.get("endpoint") == "https://api.openai.com/v1":
                default_config["endpoint"] = "https://api.minimax.io/v1"

        super().__init__(
            model_name=default_config["model"],
            model_type=ModelType.LLM,
            provider=ProviderType.CLOUD,
            config=default_config
        )

        self.session: Optional[aiohttp.ClientSession] = None
        self.api_key = self.config["api_key"]
        self.endpoint = self.config["endpoint"].rstrip('/')
        self.model = self.config["model"]

        # 日志中脱敏API密钥
        masked_key = f"{self.api_key[:7]}...{self.api_key[-4:]}" if len(self.api_key) > 11 else "***"
        logger.info(f"初始化OpenAI兼容服务，模型: {self.model}, 端点: {self.endpoint}, API密钥: {masked_key}")

    async def load_model(self) -> bool:
        """加载模型（验证API连接）"""
        try:
            self.update_status(ModelStatus.LOADING)
            logger.info(f"开始验证OpenAI兼容API连接: {self.endpoint}")

            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 60))
            )

            # 发送测试请求验证连接
            await self._test_connection()

            self.update_status(ModelStatus.LOADED)
            logger.info(f"OpenAI兼容API连接验证成功: {self.model}")
            return True

        except Exception as e:
            error_msg = f"OpenAI兼容API连接失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def unload_model(self) -> bool:
        """卸载模型"""
        try:
            logger.info(f"开始卸载OpenAI兼容服务: {self.model}")

            # 关闭HTTP会话
            if self.session:
                await self.session.close()
                self.session = None

            self.update_status(ModelStatus.UNLOADED)
            logger.info("OpenAI兼容服务卸载成功")
            return True

        except Exception as e:
            error_msg = f"卸载OpenAI兼容服务失败: {str(e)}"
            logger.error(error_msg)
            return False

    async def predict(self, messages: Union[str, List[Message], List[Dict]], **kwargs) -> Dict[str, Any]:
        """
        大语言模型预测

        Args:
            messages: 输入消息
            **kwargs: 预测参数

        Returns:
            Dict[str, Any]: 生成结果
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 标准化消息格式
            standardized_messages = self._standardize_messages(messages)

            # 获取预测参数
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2048))
            top_p = kwargs.get("top_p", self.config.get("top_p", 1.0))

            # MiniMax 特殊处理：temperature 范围为 (0.0, 1.0]，不能为 0
            if self.model.lower().startswith("minimax") and temperature <= 0:
                temperature = 1.0

            logger.info(f"开始OpenAI兼容API预测，消息数量: {len(standardized_messages)}")

            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": standardized_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }

            # 发送请求
            url = f"{self.endpoint}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with self.session.post(url, json=request_data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AIModelException(
                        f"OpenAI兼容API请求失败: {response.status} - {error_text}",
                        model_name=self.model_name
                    )

                result = await response.json()

            # 处理响应
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")

            usage = result.get("usage", {})

            self.record_usage()
            logger.info(f"OpenAI兼容API预测完成，生成文本长度: {len(content)}")

            return {
                "content": content,
                "model": self.model,
                "provider": "cloud",
                "finish_reason": choice.get("finish_reason"),
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            }

        except Exception as e:
            error_msg = f"OpenAI兼容API预测失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _standardize_messages(self, messages: Union[str, List[Message], List[Dict]]) -> List[Dict]:
        """标准化消息格式"""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            if messages and isinstance(messages[0], Message):
                return [{"role": msg.role, "content": msg.content} for msg in messages]
            elif messages and isinstance(messages[0], dict):
                return messages
            else:
                raise AIModelException(f"不支持的消息格式: {type(messages[0])}", model_name=self.model_name)
        else:
            raise AIModelException(f"不支持的消息类型: {type(messages)}", model_name=self.model_name)

    async def _test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 发送一个简单的测试请求
            url = f"{self.endpoint}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            }

            async with self.session.post(url, json=request_data, headers=headers) as response:
                if response.status == 200:
                    logger.info("OpenAI兼容API连接测试成功")
                    return True
                else:
                    error_text = await response.text()
                    raise AIModelException(f"API连接测试失败: {response.status} - {error_text}")

        except Exception as e:
            raise AIModelException(f"连接测试异常: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        # 脱敏API密钥
        masked_key = f"{self.api_key[:7]}...{self.api_key[-4:]}" if len(self.api_key) > 11 else "***"

        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "endpoint": self.endpoint,
            "model": self.model,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 2048),
            "top_p": self.config.get("top_p", 1.0),
            "api_key": masked_key,
        }

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        return "你好，请简单介绍一下你自己。"

    async def chat(self, message: str, history: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        简化的聊天接口

        Args:
            message: 用户消息
            history: 聊天历史
            **kwargs: 其他参数

        Returns:
            str: 模型回复
        """
        messages = []

        # 添加历史消息
        if history:
            messages.extend(history)

        # 添加当前消息
        messages.append({"role": "user", "content": message})

        # 发送请求
        result = await self.predict(messages, **kwargs)
        return result.get("content", "")


# 工厂函数
def create_openai_compatible_service(config: Dict[str, Any]) -> OpenAILLMService:
    """
    创建OpenAI兼容大语言模型服务实例

    Args:
        config: 模型配置参数

    Returns:
        OpenAILLMService: OpenAI兼容服务实例
    """
    return OpenAILLMService(config)