"""
Ollama大语言模型集成服务
提供本地大语言模型调用
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List, Union
import aiohttp
from dataclasses import dataclass
import os

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """聊天消息数据类"""
    role: str  # system, user, assistant
    content: str
    images: Optional[List[str]] = None  # Base64编码的图片


class OllamaLLMService(BaseAIModel):
    """
    Ollama大语言模型服务

    提供本地大语言模型调用，支持多种开源模型
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化Ollama大语言模型服务

        Args:
            config: 模型配置参数
        """
        default_config = {
            "model_name": "qwen:7b",  # 默认使用qwen
            "base_url": "http://localhost:11434",
            "timeout": 60,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "num_predict": 2048,
            "num_ctx": 2048,
            "seed": None
        }

        if config:
            # 处理配置字段兼容性
            if "model" in config and "model_name" not in config:
                config["model_name"] = config["model"]
            default_config.update(config)

        super().__init__(
            model_name=default_config["model_name"],
            model_type=ModelType.LLM,
            provider=ProviderType.LOCAL,
            config=default_config
        )

        self.session = None
        self.model_info = None

        logger.info(f"初始化Ollama大语言模型服务，模型: {self.config['model_name']}")

    async def load_model(self) -> bool:
        """
        加载Ollama模型（检查模型是否可用）

        Returns:
            bool: 加载是否成功
        """
        try:
            self.update_status(ModelStatus.LOADING)
            logger.info(f"开始检查Ollama模型: {self.model_name}")

            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 60))
            )

            # 检查Ollama服务是否可用
            await self._check_ollama_service()

            # 检查模型是否存在
            await self._check_model_exists()

            # 获取模型信息
            await self._get_model_info()

            self.update_status(ModelStatus.LOADED)
            logger.info(f"Ollama模型检查成功，模型: {self.model_name}")
            return True

        except Exception as e:
            error_msg = f"Ollama模型检查失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def unload_model(self) -> bool:
        """
        卸载Ollama模型

        Returns:
            bool: 卸载是否成功
        """
        try:
            logger.info(f"开始卸载Ollama模型: {self.model_name}")

            # 关闭HTTP会话
            if self.session:
                await self.session.close()
                self.session = None

            self.update_status(ModelStatus.UNLOADED)
            logger.info("Ollama模型卸载成功")
            return True

        except Exception as e:
            error_msg = f"Ollama模型卸载失败: {str(e)}"
            logger.error(error_msg)
            return False

    async def predict(self, messages: Union[str, List[Message], List[Dict]], **kwargs) -> Dict[str, Any]:
        """
        大语言模型预测

        Args:
            messages: 输入消息，可以是字符串、Message对象列表或字典列表
            **kwargs: 其他预测参数
                - temperature: 温度参数
                - max_tokens: 最大生成token数

        Returns:
            Dict[str, Any]: 生成结果，包含生成文本、使用token数等

        Raises:
            AIModelException: 预测失败时抛出异常
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
            max_tokens = kwargs.get("max_tokens", self.config.get("num_predict", 2048))

            logger.info(f"开始Ollama本地模型预测，消息数量: {len(standardized_messages)}")

            # 直接使用本地Ollama预测
            result = await self._predict_with_ollama(standardized_messages, **kwargs)

            self.record_usage()
            logger.info(f"大语言模型预测完成，生成文本长度: {len(result['content'])}")
            return result

        except Exception as e:
            error_msg = f"大语言模型预测失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _standardize_messages(self, messages: Union[str, List[Message], List[Dict]]) -> List[Dict]:
        """
        标准化消息格式

        Args:
            messages: 输入消息

        Returns:
            List[Dict]: 标准化的消息列表
        """
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            if messages and isinstance(messages[0], Message):
                return [{"role": msg.role, "content": msg.content, "images": msg.images} for msg in messages]
            elif messages and isinstance(messages[0], dict):
                return messages
            else:
                raise AIModelException(f"不支持的消息格式: {type(messages[0])}", model_name=self.model_name)
        else:
            raise AIModelException(f"不支持的消息类型: {type(messages)}", model_name=self.model_name)

    async def _predict_with_ollama(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """使用本地Ollama模型进行预测"""
        if not self.session:
            raise AIModelException("HTTP会话未初始化", model_name=self.model_name)

        # 构建请求参数
        request_data = {
            "model": self.model_name,
            "messages": messages,
            "options": {
                "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                "top_p": kwargs.get("top_p", self.config.get("top_p", 0.9)),
                "top_k": kwargs.get("top_k", self.config.get("top_k", 40)),
                "repeat_penalty": kwargs.get("repeat_penalty", self.config.get("repeat_penalty", 1.1)),
                "num_predict": kwargs.get("max_tokens", self.config.get("num_predict", 2048)),
                "num_ctx": self.config.get("num_ctx", 2048),
                "seed": kwargs.get("seed", self.config.get("seed"))
            },
            "stream": False  # 不使用流式响应
        }

        # 发送请求
        url = f"{self.config['base_url']}/api/chat"
        async with self.session.post(url, json=request_data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise AIModelException(f"Ollama API请求失败: {response.status} - {error_text}", model_name=self.model_name)

            result = await response.json()

        # 处理响应
        return {
            "content": result.get("message", {}).get("content", ""),
            "model": self.model_name,
            "provider": "local",
            "done": result.get("done", False),
            "total_duration": result.get("total_duration", 0) / 1e9,  # 转换为秒
            "load_duration": result.get("load_duration", 0) / 1e9,
            "prompt_eval_count": result.get("prompt_eval_count", 0),
            "prompt_eval_duration": result.get("prompt_eval_duration", 0) / 1e9,
            "eval_count": result.get("eval_count", 0),
            "eval_duration": result.get("eval_duration", 0) / 1e9,
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
            }
        }

    async def _check_ollama_service(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            url = f"{self.config['base_url']}/api/tags"
            async with self.session.get(url) as response:
                if response.status == 200:
                    logger.info("Ollama服务连接正常")
                    return True
                else:
                    raise AIModelException(f"Ollama服务不可用，状态码: {response.status}", model_name=self.model_name)
        except Exception as e:
            raise AIModelException(f"无法连接到Ollama服务: {str(e)}", model_name=self.model_name)

    async def _check_model_exists(self) -> bool:
        """检查模型是否存在"""
        try:
            url = f"{self.config['base_url']}/api/tags"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    model_names = [model.get("name", "").split(":")[0] for model in models]

                    if self.model_name.split(":")[0] in model_names:
                        logger.info(f"模型 {self.model_name} 存在")
                        return True
                    else:
                        # 尝试拉取模型
                        logger.info(f"模型 {self.model_name} 不存在，尝试拉取...")
                        return await self._pull_model()
                else:
                    raise AIModelException(f"获取模型列表失败，状态码: {response.status}", model_name=self.model_name)
        except Exception as e:
            raise AIModelException(f"检查模型存在性失败: {str(e)}", model_name=self.model_name)

    async def _pull_model(self) -> bool:
        """拉取模型"""
        try:
            url = f"{self.config['base_url']}/api/pull"
            request_data = {"name": self.model_name}

            logger.info(f"开始拉取模型: {self.model_name}")
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    # 流式读取拉取进度
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode())
                                status = data.get("status", "")
                                if "download" in status.lower():
                                    logger.info(f"模型拉取进度: {status}")
                            except json.JSONDecodeError:
                                pass

                    logger.info(f"模型 {self.model_name} 拉取完成")
                    return True
                else:
                    raise AIModelException(f"拉取模型失败，状态码: {response.status}", model_name=self.model_name)
        except Exception as e:
            raise AIModelException(f"拉取模型失败: {str(e)}", model_name=self.model_name)

    async def _get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            url = f"{self.config['base_url']}/api/show"
            request_data = {"name": self.model_name}

            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    self.model_info = await response.json()
                    logger.info(f"获取到模型信息: {self.model_info.get('modelfile', 'N/A')[:100]}...")
                    return self.model_info
                else:
                    logger.warning(f"获取模型信息失败，状态码: {response.status}")
                    return {}
        except Exception as e:
            logger.warning(f"获取模型信息异常: {str(e)}")
            return {}

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

    async def stream_chat(self, message: str, history: Optional[List[Dict]] = None, **kwargs):
        """
        流式聊天接口（仅本地Ollama支持）

        Args:
            message: 用户消息
            history: 聊天历史
            **kwargs: 其他参数

        Yields:
            str: 流式文本片段
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 构建消息
            messages = []
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": message})

            # 构建请求
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                    "num_predict": kwargs.get("max_tokens", self.config.get("num_predict", 2048))
                },
                "stream": True
            }

            # 发送流式请求
            url = f"{self.config['base_url']}/api/chat"
            async with self.session.post(url, json=request_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AIModelException(f"Ollama流式API请求失败: {response.status} - {error_text}", model_name=self.model_name)

                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode())
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            error_msg = f"流式聊天失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息
        """
        info = {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "base_url": self.config.get("base_url", "http://localhost:11434"),
            "temperature": self.config.get("temperature", 0.7),
            "top_p": self.config.get("top_p", 0.9),
            "top_k": self.config.get("top_k", 40),
            "num_predict": self.config.get("num_predict", 2048),
            "num_ctx": self.config.get("num_ctx", 2048),
            "model_info": self.model_info
        }

        return info

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        return "你好，请简单介绍一下你自己。"

    async def benchmark_performance(self, test_messages: List[str], num_runs: int = 3) -> Dict[str, Any]:
        """
        性能基准测试

        Args:
            test_messages: 测试消息列表
            num_runs: 运行次数

        Returns:
            Dict[str, Any]: 性能测试结果
        """
        try:
            logger.info(f"开始Ollama性能基准测试，消息数量: {len(test_messages)}, 运行次数: {num_runs}")

            times = []
            total_tokens = 0
            for run in range(num_runs):
                run_tokens = 0
                for message in test_messages:
                    start_time = time.time()
                    result = await self.predict(message)
                    end_time = time.time()

                    run_time = end_time - start_time
                    times.append(run_time)
                    run_tokens += result.get("usage", {}).get("total_tokens", 0)

                total_tokens += run_tokens
                logger.info(f"第{run + 1}次运行完成，总token数: {run_tokens}")

            avg_time = np.mean(times)
            avg_tokens_per_request = total_tokens / (num_runs * len(test_messages))
            throughput = len(test_messages) / avg_time

            results = {
                "model_name": self.model_name,
                "num_messages": len(test_messages),
                "num_runs": num_runs,
                "total_tokens": total_tokens,
                "avg_tokens_per_request": avg_tokens_per_request,
                "times": times,
                "avg_time": float(avg_time),
                "min_time": float(np.min(times)),
                "max_time": float(np.max(times)),
                "throughput": float(throughput),  # messages per second
                "tokens_per_second": float(total_tokens / sum(times)),
                "provider": "local"
            }

            logger.info(f"性能基准测试完成，平均耗时: {avg_time:.3f}秒，吞吐量: {throughput:.1f} msg/s")
            return results

        except Exception as e:
            error_msg = f"性能基准测试失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)


# 创建Ollama服务实例的工厂函数
def create_ollama_service(config: Dict[str, Any] = None,
                          model_name: Optional[str] = None) -> OllamaLLMService:
    """
    创建Ollama大语言模型服务实例

    Args:
        config: 模型配置参数
        model_name: 数据库 ai_models.model_name 列中的模型名称

    Returns:
        OllamaLLMService: Ollama服务实例

    Note:
        数据库中的 model_name 列是模型名称的唯一事实来源，
        config_json 里的 model_name 可能仍是初始化时的默认值（如 qwen2.5:1.5b），
        若不覆盖，用户在前端改了模型名后，测试和实际调用仍会使用旧模型。
    """
    merged_config = dict(config) if isinstance(config, dict) else {}
    if model_name:
        merged_config["model_name"] = model_name
    return OllamaLLMService(merged_config)