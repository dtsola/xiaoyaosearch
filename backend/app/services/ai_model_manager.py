"""
AI模型管理服务
统一管理和协调所有AI模型实例 - 修复版
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

logger = logging.getLogger(__name__)

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, ModelManager, AIModelException
from app.utils.enum_helpers import get_enum_value
from app.core.config import get_settings

# 尝试导入AI模型服务，如果模块不存在则跳过
try:
    from app.services.bge_embedding_service import create_bge_service
    BGE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"BGE嵌入服务不可用: {e}")
    create_bge_service = None
    BGE_AVAILABLE = False

try:
    from app.services.whisper_service import create_whisper_service
    WHISPER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Whisper语音服务不可用: {e}")
    create_whisper_service = None
    WHISPER_AVAILABLE = False

try:
    from app.services.clip_service import create_clip_service
    CLIP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"CLIP图像服务不可用: {e}")
    create_clip_service = None
    CLIP_AVAILABLE = False

try:
    from app.services.ollama_service import create_ollama_service
    OLLAMA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Ollama服务不可用: {e}")
    create_ollama_service = None
    OLLAMA_AVAILABLE = False
from app.models.ai_model import AIModelModel
from app.core.database import get_db

logger = logging.getLogger(__name__)


class AIModelService:
    """
    AI模型管理服务

    负责AI模型的生命周期管理、配置管理和调用协调
    """

    def __init__(self):
        """初始化AI模型管理服务"""
        self.model_manager = ModelManager()
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        self.default_models: Dict[str, str] = {}  # model_type -> model_id

        logger.info("AI模型管理服务初始化完成")

    async def initialize(self):
        """
        初始化AI模型管理服务
        从数据库加载模型配置并创建模型实例
        """
        try:
            logger.info("开始初始化AI模型管理服务")

            # 从数据库加载模型配置
            await self._load_model_configs_from_db()

            # 创建默认模型实例
            await self._create_default_models()

            logger.info("AI模型管理服务初始化完成")

        except Exception as e:
            logger.error(f"AI模型管理服务初始化失败: {str(e)}")
            raise

    async def _load_model_configs_from_db(self):
        """从数据库加载模型配置"""
        try:
            with get_db() as db:
                # 查询所有活跃的模型配置
                model_configs = db.query(AIModelModel).filter(AIModelModel.is_active == True).all()

                for config in model_configs:
                    model_id = f"{config.provider}_{config.model_type}_{config.id}"
                    self.model_configs[model_id] = {
                        "id": config.id,
                        "model_type": config.model_type,
                        "provider": config.provider,
                        "model_name": config.model_name,
                        "config": config.config_json
                    }

                logger.info(f"从数据库加载了 {len(self.model_configs)} 个模型配置")

        except Exception as e:
            logger.warning(f"从数据库加载模型配置失败: {str(e)}，使用默认配置")
            self._set_default_configs()

    def _set_default_configs(self):
        """设置默认模型配置"""
        import os
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        self.model_configs = {
            "bge_m3_local": {
                "model_type": "embedding",
                "provider": "local",
                "model_name": "BAAI/bge-m3",
                "config": {
                    "model_name": str(project_root / "data" / "models" / "embedding" / "BAAI" / "bge-m3"),
                    "device": get_settings().ai.get_optimal_device(),
                    "embedding_dim": 1024,
                    "max_length": 8192,
                    "normalize_embeddings": True
                }
            },
            "whisper_local": {
                "model_type": "speech",
                "provider": "local",
                "model_name": str(project_root / "data" / "models" / "faster-whisper" / "Systran" / "faster-whisper-base"),
                "config": {
                    "model_size": "base",
                    "device": get_settings().ai.get_optimal_device(),
                    "language": "zh",
                    "max_duration": 30
                }
            },
            "clip_local": {
                "model_type": "vision",
                "provider": "local",
                "model_name": "OFA-Sys/chinese-clip-vit-base-patch16",
                "config": {
                    "model_name": str(project_root / "data" / "models" / "cn-clip" / "OFA-Sys" / "chinese-clip-vit-base-patch16"),
                    "device": get_settings().ai.get_optimal_device(),
                    "max_image_size": 512
                }
            },
            "ollama_local": {
                "model_type": "llm",
                "provider": "local",
                "model_name": "qwen2.5:1.5b",
                "config": {
                    "model_name": "qwen2.5:1.5b",
                    "base_url": "http://localhost:11434",
                    "temperature": 0.7
                }
            }
        }

    async def _create_default_models(self):
        """创建默认模型实例"""
        try:
            # 创建BGE-M3文本嵌入模型
            if "bge_m3_local" in self.model_configs:
                bge_config = self.model_configs["bge_m3_local"]["config"]
                bge_service = create_bge_service(bge_config)
                self.model_manager.register_model("bge_m3_local", bge_service)
                self.default_models["embedding"] = "bge_m3_local"

            # 创建FasterWhisper语音识别模型
            if "whisper_local" in self.model_configs:
                whisper_config = self.model_configs["whisper_local"]["config"]
                whisper_service = create_whisper_service(whisper_config)
                self.model_manager.register_model("whisper_local", whisper_service)
                self.default_models["speech"] = "whisper_local"

            # 创建CN-CLIP图像理解模型
            if "clip_local" in self.model_configs:
                clip_config = self.model_configs["clip_local"]["config"]
                clip_service = create_clip_service(clip_config)
                self.model_manager.register_model("clip_local", clip_service)
                self.default_models["vision"] = "clip_local"

            # 创建Ollama大语言模型
            if "ollama_local" in self.model_configs:
                ollama_config = self.model_configs["ollama_local"]["config"]
                ollama_service = create_ollama_service(ollama_config)
                self.model_manager.register_model("ollama_local", ollama_service)
                self.default_models["llm"] = "ollama_local"

            logger.info(f"创建了 {len(self.model_manager.models)} 个默认模型实例")

        except Exception as e:
            logger.error(f"创建默认模型实例失败: {str(e)}")

    async def load_model(self, model_id: str) -> bool:
        """
        加载指定模型

        Args:
            model_id: 模型ID

        Returns:
            bool: 加载是否成功
        """
        return await self.model_manager.load_model(model_id)

    async def unload_model(self, model_id: str) -> bool:
        """
        卸载指定模型

        Args:
            model_id: 模型ID

        Returns:
            bool: 卸载是否成功
        """
        return await self.model_manager.unload_model(model_id)

    async def get_model(self, model_type: Union[str, ModelType]) -> Optional[BaseAIModel]:
        """
        根据类型获取默认模型

        Args:
            model_type: 模型类型

        Returns:
            Optional[BaseAIModel]: 模型实例
        """
        if isinstance(model_type, str):
            model_type = ModelType(model_type)

        model_id = self.default_models.get(get_enum_value(model_type))
        if model_id:
            return self.model_manager.get_model(model_id)
        return None

    async def text_embedding(self, texts: Union[str, List[str]], **kwargs) -> Any:
        """
        文本嵌入

        Args:
            texts: 文本或文本列表
            **kwargs: 其他参数

        Returns:
            Any: 嵌入向量
        """
        model = await self.get_model(ModelType.EMBEDDING)
        if not model:
            raise AIModelException("文本嵌入模型不可用")

        return await model.predict(texts, **kwargs)

    async def speech_to_text(self, audio_input: Any, **kwargs) -> Dict[str, Any]:
        """
        语音转文字

        Args:
            audio_input: 音频输入
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 转录结果
        """
        model = await self.get_model(ModelType.SPEECH)
        if not model:
            raise AIModelException("语音识别模型不可用")

        return await model.predict(audio_input, **kwargs)

    async def image_understanding(self, image_input: Any, texts: List[str], **kwargs) -> Dict[str, Any]:
        """
        图像理解

        Args:
            image_input: 图像输入
            texts: 文本列表
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 理解结果
        """
        model = await self.get_model(ModelType.VISION)
        if not model:
            raise AIModelException("图像理解模型不可用")

        return await model.predict(image_input, texts, **kwargs)

    async def text_generation(self, messages: Union[str, List[Dict]], **kwargs) -> Dict[str, Any]:
        """
        文本生成

        Args:
            messages: 输入消息
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 生成结果
        """
        model = await self.get_model(ModelType.LLM)
        if not model:
            raise AIModelException("大语言模型不可用")

        return await model.predict(messages, **kwargs)

    async def multimodal_search(self, query: str, input_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        多模态搜索

        Args:
            query: 搜索查询
            input_type: 输入类型 (text/speech/image)
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 搜索结果
        """
        try:
            results = {
                "query": query,
                "input_type": input_type,
                "processing_time": 0,
                "results": [],
                "error": None
            }

            start_time = datetime.now()

            # 根据输入类型处理查询
            if input_type == "speech":
                # 语音转文字
                transcription_result = await self.speech_to_text(query, **kwargs)
                processed_query = transcription_result.get("text", "")
                results["transcription"] = transcription_result
            elif input_type == "image":
                # 图像理解生成搜索查询
                if "texts" not in kwargs:
                    kwargs["texts"] = ["描述这张图片的内容", "这张图片展示了什么"]
                vision_result = await self.image_understanding(query, **kwargs)
                processed_query = vision_result.get("best_match", {}).get("text", "")
                results["vision_understanding"] = vision_result
            else:
                # 文本查询直接使用
                processed_query = query

            if not processed_query:
                raise AIModelException("无法处理搜索查询")

            # 使用文本嵌入进行语义搜索
            embedding_result = await self.text_embedding(processed_query)
            results["embedding"] = embedding_result

            # 使用大语言模型优化查询（可选）
            if kwargs.get("use_llm_query_expansion", False):
                expansion_result = await self.text_generation([
                    {"role": "system", "content": "你是一个搜索助手，请帮用户优化搜索查询，提供更具体的搜索关键词。"},
                    {"role": "user", "content": f"请为以下搜索查询提供更好的关键词：{processed_query}"}
                ])
                results["query_expansion"] = expansion_result

            results["processed_query"] = processed_query
            results["processing_time"] = (datetime.now() - start_time).total_seconds()

            return results

        except Exception as e:
            logger.error(f"多模态搜索失败: {str(e)}")
            return {
                "query": query,
                "input_type": input_type,
                "processing_time": 0,
                "results": [],
                "error": str(e)
            }

    async def get_model_status(self) -> Dict[str, Any]:
        """
        获取所有模型状态

        Returns:
            Dict[str, Any]: 模型状态信息
        """
        return self.model_manager.get_status_summary()

    async def health_check(self) -> Dict[str, bool]:
        """
        健康检查所有模型

        Returns:
            Dict[str, bool]: 每个模型的健康状态
        """
        return await self.model_manager.health_check_all()

    async def load_all_models(self) -> Dict[str, bool]:
        """
        加载所有模型

        Returns:
            Dict[str, bool]: 每个模型的加载结果
        """
        return await self.model_manager.load_all_models()

    async def unload_all_models(self) -> Dict[str, bool]:
        """
        卸载所有模型

        Returns:
            Dict[str, bool]: 每个模型的卸载结果
        """
        return await self.model_manager.unload_all_models()

    async def register_model(self, model_id: str, model_config: Dict[str, Any]) -> bool:
        """
        注册新模型

        Args:
            model_id: 模型ID
            model_config: 模型配置

        Returns:
            bool: 注册是否成功
        """
        try:
            model_type = model_config.get("model_type")
            provider = model_config.get("provider")
            config = model_config.get("config", {})

            # 根据类型创建模型实例
            if model_type == "embedding":
                model = create_bge_service(config)
            elif model_type == "speech":
                model = create_whisper_service(config)
            elif model_type == "vision":
                model = create_clip_service(config)
            elif model_type == "llm":
                model = create_ollama_service(config)
            else:
                raise AIModelException(f"不支持的模型类型: {model_type}")

            # 注册模型
            self.model_manager.register_model(model_id, model)
            self.model_configs[model_id] = model_config

            logger.info(f"成功注册模型: {model_id}")
            return True

        except Exception as e:
            logger.error(f"注册模型失败: {model_id}, 错误: {str(e)}")
            return False

    async def unregister_model(self, model_id: str) -> bool:
        """
        注销模型

        Args:
            model_id: 模型ID

        Returns:
            bool: 注销是否成功
        """
        try:
            # 先卸载模型
            await self.unload_model(model_id)

            # 注销模型
            self.model_manager.unregister_model(model_id)
            self.model_configs.pop(model_id, None)

            # 移除默认模型映射
            for model_type, default_id in self.default_models.items():
                if default_id == model_id:
                    del self.default_models[model_type]
                    break

            logger.info(f"成功注销模型: {model_id}")
            return True

        except Exception as e:
            logger.error(f"注销模型失败: {model_id}, 错误: {str(e)}")
            return False

    async def set_default_model(self, model_type: str, model_id: str) -> bool:
        """
        设置默认模型

        Args:
            model_type: 模型类型
            model_id: 模型ID

        Returns:
            bool: 设置是否成功
        """
        if model_id not in self.model_manager.models:
            logger.error(f"模型不存在: {model_id}")
            return False

        self.default_models[model_type] = model_id
        logger.info(f"设置默认模型: {model_type} -> {model_id}")
        return True

    async def get_available_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取可用模型列表

        Returns:
            Dict[str, List[Dict[str, Any]]]: 按类型分组的模型列表
        """
        models_by_type = {}
        for model_type in ModelType:
            models_by_type[get_enum_value(model_type)] = []

        for model_id, model in self.model_manager.models.items():
            model_info = {
                "model_id": model_id,
                "model_name": model.model_name,
                "model_type": get_enum_value(model.model_type),
                "provider": get_enum_value(model.provider),
                "status": get_enum_value(model.status),
                "is_default": self.default_models.get(get_enum_value(model.model_type)) == model_id,
                "config": model.get_model_info()
            }
            models_by_type[get_enum_value(model.model_type)].append(model_info)

        return models_by_type

    async def benchmark_models(self, model_types: List[str] = None) -> Dict[str, Any]:
        """
        性能基准测试

        Args:
            model_types: 要测试的模型类型列表

        Returns:
            Dict[str, Any]: 性能测试结果
        """
        results = {}

        for model_id, model in self.model_manager.models.items():
            if model_types and get_enum_value(model.model_type) not in model_types:
                continue

            try:
                if model.model_type == ModelType.EMBEDDING:
                    # BGE-M3性能测试
                    test_texts = ["这是一个测试文本", "另一个测试文本"]
                    benchmark_result = await model.benchmark_performance(test_texts)
                elif model.model_type == ModelType.SPEECH:
                    # Whisper性能测试
                    test_files = []  # 需要提供测试音频文件
                    benchmark_result = {"message": "语音模型性能测试需要测试音频文件"}
                elif model.model_type == ModelType.VISION:
                    # CLIP性能测试
                    test_images = []  # 需要提供测试图片
                    benchmark_result = {"message": "视觉模型性能测试需要测试图片"}
                elif model.model_type == ModelType.LLM:
                    # Ollama性能测试
                    test_messages = ["你好", "请介绍一下自己"]
                    benchmark_result = await model.benchmark_performance(test_messages)
                else:
                    benchmark_result = {"message": "不支持的模型类型"}

                results[model_id] = benchmark_result

            except Exception as e:
                logger.error(f"模型 {model_id} 性能测试失败: {str(e)}")
                results[model_id] = {"error": str(e)}

        return results

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.unload_all_models()


# 全局AI模型服务实例
ai_model_service = AIModelService()