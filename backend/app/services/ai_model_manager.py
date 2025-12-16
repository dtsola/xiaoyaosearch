"""
AI模型管理服务
统一管理和协调所有AI模型实例 - 修复版
"""
import asyncio
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import numpy as np

# 在导入任何AI模型库之前，配置环境变量以抑制日志警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow日志级别
os.environ['GRPC_VERBOSITY'] = 'ERROR'    # gRPC日志级别
os.environ['GLOG_minloglevel'] = '2'      # Google日志最小级别
os.environ['GLOG_v'] = '0'               # Google日志详细程度

from app.core.logging_config import logger

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, ModelManager, AIModelException
from app.utils.enum_helpers import get_enum_value
from app.core.config import get_settings
from app.services.bge_embedding_service import create_bge_service
from app.services.whisper_service import create_whisper_service
from app.services.clip_service import create_clip_service
from app.services.ollama_service import create_ollama_service
from app.models.ai_model import AIModelModel
from app.core.database import get_db, SessionLocal


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
            # 创建数据库会话
            db = SessionLocal()
            try:
                # 首先检查数据库中是否有模型配置
                total_models = db.query(AIModelModel).count()

                # 如果没有模型配置，先初始化默认配置
                if total_models == 0:
                    logger.info("数据库中没有AI模型配置，初始化默认配置")
                    await self._initialize_default_configs_to_db(db)

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

            finally:
                db.close()

        except Exception as e:
            logger.error(f"从数据库加载模型配置失败: {str(e)}")

    async def _initialize_default_configs_to_db(self, db):
        """
        将默认模型配置初始化到数据库

        Args:
            db: 数据库会话
        """
        try:
            import json
            from app.models.ai_model import AIModelModel

            logger.info("开始将默认AI模型配置初始化到数据库")

            # 获取默认配置
            default_configs = AIModelModel.get_default_configs()

            # 创建默认模型配置记录
            created_count = 0

            for config_key, config_data in default_configs.items():
                # 检查是否已存在相同的配置
                existing_model = db.query(AIModelModel).filter(
                    AIModelModel.model_type == config_data["model_type"],
                    AIModelModel.provider == config_data["provider"],
                    AIModelModel.model_name == config_data["model_name"]
                ).first()

                if not existing_model:
                    # 创建新的模型配置
                    new_model = AIModelModel(
                        model_type=config_data["model_type"],
                        provider=config_data["provider"],
                        model_name=config_data["model_name"],
                        config_json=json.dumps(config_data["config"], ensure_ascii=False),
                        is_active=True
                    )
                    db.add(new_model)
                    created_count += 1
                    logger.info(f"创建默认AI模型配置: {config_data['model_type']} - {config_data['model_name']}")
                else:
                    logger.info(f"AI模型配置已存在，跳过: {config_data['model_type']} - {config_data['model_name']}")

            # 提交所有更改
            db.commit()

            if created_count > 0:
                logger.info(f"成功初始化 {created_count} 个默认AI模型配置到数据库")
            else:
                logger.info("所有默认AI模型配置都已存在于数据库中")

        except Exception as e:
            logger.error(f"初始化默认AI模型配置到数据库失败: {str(e)}")
            db.rollback()
            raise

    async def _create_default_models(self):
        """创建默认模型实例"""
        try:
            # 从数据库配置动态创建模型实例
            for model_id, model_config in self.model_configs.items():
                model_type = model_config["model_type"]
                provider = model_config.get("provider", "local")
                config = model_config["config"]

                # 如果config是字符串，需要解析JSON
                if isinstance(config, str):
                    import json
                    config = json.loads(config)

                # 校验本地模型路径
                if provider == "local" and model_type in ["embedding", "speech", "vision"]:
                    await self._validate_and_fix_model_path(model_type, config, model_id)

                try:
                    if model_type == "embedding":
                        # 创建文本嵌入模型
                        bge_service = create_bge_service(config)
                        self.model_manager.register_model(model_id, bge_service)
                        self.default_models["embedding"] = model_id
                        # 立即加载模型
                        await self.model_manager.load_model(model_id)
                        logger.info(f"创建并加载embedding模型: {model_id}")

                    elif model_type == "speech":
                        # 创建语音识别模型
                        whisper_service = create_whisper_service(config)
                        self.model_manager.register_model(model_id, whisper_service)
                        self.default_models["speech"] = model_id
                        # 立即加载模型
                        await self.model_manager.load_model(model_id)
                        logger.info(f"创建并加载speech模型: {model_id}")

                    elif model_type == "vision":
                        # 创建图像理解模型
                        clip_service = create_clip_service(config)
                        self.model_manager.register_model(model_id, clip_service)
                        self.default_models["vision"] = model_id
                        # 立即加载模型
                        await self.model_manager.load_model(model_id)
                        logger.info(f"创建并加载vision模型: {model_id}")

                    elif model_type == "llm":
                        # 创建大语言模型
                        ollama_service = create_ollama_service(config)
                        self.model_manager.register_model(model_id, ollama_service)
                        self.default_models["llm"] = model_id
                        # 立即加载模型
                        await self.model_manager.load_model(model_id)
                        logger.info(f"创建并加载llm模型: {model_id}")

                except Exception as model_error:
                    logger.warning(f"创建{model_type}模型失败 ({model_id}): {str(model_error)}")

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

        # 记录调试信息
        model_type_str = get_enum_value(model_type)
        logger.debug(f"获取模型类型: {model_type_str}")
        logger.debug(f"当前默认模型映射: {self.default_models}")

        model_id = self.default_models.get(model_type_str)
        logger.debug(f"找到模型ID: {model_id}")

        if model_id:
            model = self.model_manager.get_model(model_id)
            logger.debug(f"获取到模型: {model}")
            return model

        logger.warning(f"未找到模型类型 {model_type_str} 的默认模型")
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

    async def batch_text_embedding(self, texts: List[str], batch_size: int = 32, **kwargs) -> List[List[float]]:
        """
        批量文本嵌入

        Args:
            texts: 文本列表
            batch_size: 批处理大小
            **kwargs: 其他参数

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []
        total_texts = len(texts)

        # 分批处理
        for i in range(0, total_texts, batch_size):
            batch_texts = texts[i:i + batch_size]
            try:
                batch_embeddings = await self.text_embedding(batch_texts, **kwargs)

                # 处理numpy数组返回值
                if isinstance(batch_embeddings, np.ndarray):
                    if batch_embeddings.ndim == 2:
                        # 标准情况: (batch_size, embedding_dim)
                        batch_list = batch_embeddings.tolist()
                        all_embeddings.extend(batch_list)
                    elif batch_embeddings.ndim == 1:
                        # 单个向量: (embedding_dim,)
                        all_embeddings.append(batch_embeddings.tolist())
                    else:
                        # 多维数组，展平处理
                        flattened = [emb.flatten().tolist() for emb in batch_embeddings]
                        all_embeddings.extend(flattened)
                elif isinstance(batch_embeddings, list):
                    # 如果是列表，需要检查元素类型
                    for emb in batch_embeddings:
                        if isinstance(emb, np.ndarray):
                            if emb.ndim > 1:
                                all_embeddings.append(emb.flatten().tolist())
                            else:
                                all_embeddings.append(emb.tolist())
                        else:
                            all_embeddings.append(emb)
                else:
                    # 其他类型，直接添加
                    all_embeddings.append(batch_embeddings)

            except Exception as e:
                logger.error(f"批量嵌入处理失败 (批次 {i//batch_size + 1}): {str(e)}")
                # 使用零向量作为fallback
                dummy_embedding = [0.0] * 1024  # BGE-M3标准维度
                for _ in batch_texts:
                    all_embeddings.append(dummy_embedding)

        return all_embeddings

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

    async def encode_image(self, image_input: Any) -> Any:
        """
        图像编码为特征向量

        Args:
            image_input: 图像输入

        Returns:
            Any: 图像特征向量
        """
        model = await self.get_model(ModelType.VISION)
        if not model:
            raise AIModelException("图像理解模型不可用")

        return await model.encode_image(image_input)

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

    async def reload_model(self, model_type: str) -> Dict[str, Any]:
        """
        热重载指定类型的模型

        Args:
            model_type: 模型类型 (embedding/speech/vision/llm)

        Returns:
            Dict[str, Any]: 重载结果
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"开始热重载模型: {model_type}")

            # 查找当前默认模型
            current_model_id = self.default_models.get(model_type)
            if not current_model_id:
                return {
                    "success": False,
                    "message": f"未找到{model_type}类型的默认模型",
                    "reload_time": 0
                }

            # 卸载当前模型
            logger.info(f"卸载当前模型: {current_model_id}")
            unload_success = await self.unload_model(current_model_id)
            if not unload_success:
                return {
                    "success": False,
                    "message": f"卸载模型失败: {current_model_id}",
                    "reload_time": 0
                }

            # 从数据库重新加载配置
            await self._load_model_configs_from_db()

            # 查找新的模型配置
            new_model_id = None
            new_model_config = None

            for model_id, config in self.model_configs.items():
                if config.get("model_type") == model_type and config.get("is_active", True):
                    # 选择最新的配置
                    if not new_model_config or config.get("id", 0) > new_model_config.get("id", 0):
                        new_model_id = model_id
                        new_model_config = config

            if not new_model_id or not new_model_config:
                return {
                    "success": False,
                    "message": f"未找到{model_type}类型的有效配置",
                    "reload_time": time.time() - start_time
                }

            # 创建并加载新模型
            logger.info(f"创建并加载新模型: {new_model_id}")
            config = new_model_config.get("config", {})
            if isinstance(config, str):
                import json
                config = json.loads(config)

            # 根据模型类型创建新模型实例
            new_model = None
            if model_type == "embedding":
                new_model = create_bge_service(config)
            elif model_type == "speech":
                new_model = create_whisper_service(config)
            elif model_type == "vision":
                new_model = create_clip_service(config)
            elif model_type == "llm":
                new_model = create_ollama_service(config)
            else:
                return {
                    "success": False,
                    "message": f"不支持的模型类型: {model_type}",
                    "reload_time": time.time() - start_time
                }

            # 注册新模型
            self.model_manager.register_model(new_model_id, new_model)

            # 加载新模型
            load_success = await self.model_manager.load_model(new_model_id)
            if not load_success:
                return {
                    "success": False,
                    "message": f"加载新模型失败: {new_model_id}",
                    "reload_time": time.time() - start_time
                }

            # 更新默认模型映射
            self.default_models[model_type] = new_model_id

            reload_time = time.time() - start_time
            logger.info(f"模型热重载成功: {model_type} -> {new_model_id}, 耗时: {reload_time:.3f}秒")

            return {
                "success": True,
                "message": f"{model_type}模型热重载成功",
                "reload_time": round(reload_time, 3),
                "old_model_id": current_model_id,
                "new_model_id": new_model_id
            }

        except Exception as e:
            logger.error(f"模型热重载失败: {model_type}, 错误: {str(e)}")
            return {
                "success": False,
                "message": f"模型热重载失败: {str(e)}",
                "reload_time": time.time() - start_time
            }

    async def reload_all_models(self) -> Dict[str, Any]:
        """
        热重载所有模型

        Returns:
            Dict[str, Any]: 重载结果
        """
        results = {}

        for model_type in ["embedding", "speech", "vision", "llm"]:
            results[model_type] = await self.reload_model(model_type)

        return results

    async def _validate_and_fix_model_path(self, model_type: str, config: dict, model_id: str):
        """
        校验并修复模型路径配置

        Args:
            model_type: 模型类型 (embedding/speech/vision)
            config: 模型配置字典
            model_id: 模型ID
        """
        import os

        model_path = config.get("model_path")
        model_name = config.get("model_name")

        if not model_path:
            logger.info(f"{model_type}模型配置中没有model_path，将使用网络模型: {model_name}")
            return

        # 检查本地路径是否存在
        if os.path.exists(model_path):
            logger.info(f"✅ {model_type}本地模型路径存在: {model_path}")
            # 验证模型文件完整性
            await self._verify_model_files(model_type, model_path, model_id)
        else:
            logger.warning(f"⚠️ {model_type}本地模型路径不存在: {model_path}")
            logger.warning(f"📁 尝试创建父目录: {os.path.dirname(model_path)}")

            # 尝试创建父目录
            parent_dir = os.path.dirname(model_path)
            try:
                os.makedirs(parent_dir, exist_ok=True)
                logger.info(f"✅ 成功创建模型目录: {parent_dir}")
            except PermissionError:
                logger.error(f"❌ 没有权限创建目录: {parent_dir}")
            except Exception as e:
                logger.error(f"❌ 创建目录失败: {parent_dir}, 错误: {str(e)}")

    async def _verify_model_files(self, model_type: str, model_path: str, model_id: str):
        """
        验证模型文件完整性

        Args:
            model_type: 模型类型
            model_path: 模型路径
            model_id: 模型ID
        """
        import os

        try:
            if os.path.isfile(model_path):
                # 单文件模型
                file_size = os.path.getsize(model_path)
                logger.info(f"📄 {model_type}模型文件: {model_path}, 大小: {file_size / (1024*1024):.1f}MB")
            elif os.path.isdir(model_path):
                # 目录模型，检查关键文件
                files = os.listdir(model_path)
                logger.info(f"📁 {model_type}模型目录: {model_path}, 文件数量: {len(files)}")

                # 根据模型类型检查必需文件
                required_files = self._get_required_model_files(model_type)
                missing_files = []

                for file_pattern in required_files:
                    found = any(file_pattern.replace('*', '') in f for f in files)
                    if not found:
                        missing_files.append(file_pattern)

                if missing_files:
                    logger.warning(f"⚠️ {model_type}模型可能缺少必要文件: {missing_files}")
                else:
                    logger.info(f"✅ {model_type}模型文件完整性检查通过")

        except Exception as e:
            logger.error(f"❌ 验证{model_type}模型文件失败: {str(e)}")

    def _get_required_model_files(self, model_type: str) -> list:
        """
        获取各类型模型的必需文件列表

        Args:
            model_type: 模型类型

        Returns:
            list: 必需文件模式列表
        """
        if model_type == "embedding":
            return ["config.json", "pytorch_model.bin"]
        elif model_type == "speech":
            return ["model.bin"]
        elif model_type == "vision":
            return ["config.json", "pytorch_model.bin"]
        else:
            return []

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.unload_all_models()


# 全局AI模型服务实例
ai_model_service = AIModelService()