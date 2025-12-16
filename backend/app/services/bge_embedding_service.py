"""
BGE-M3文本嵌入模型服务
提供中文文本向量化功能
"""
import asyncio
import os
import time
from typing import List, Dict, Any, Optional, Union

# 配置日志环境变量，抑制C++库的日志警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow日志级别
os.environ['GRPC_VERBOSITY'] = 'ERROR'    # gRPC日志级别
os.environ['GLOG_minloglevel'] = '2'      # Google日志最小级别
os.environ['GLOG_v'] = '0'               # Google日志详细程度
os.environ['PYTHONWARNINGS'] = 'ignore'  # 忽略Python警告

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
from app.utils.enum_helpers import get_enum_value
from app.core.config import get_settings
from app.core.logging_config import logger
settings = get_settings()


class BGEEmbeddingService(BaseAIModel):
    """
    BGE-M3文本嵌入服务

    BGE-M3是BAAI开发的多语言、多粒度、多功能嵌入模型
    特别针对中文优化，支持1024维向量输出
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化BGE-M3嵌入服务

        Args:
            config: 模型配置参数
        """
        default_config = {
            "model_name": "BAAI/bge-m3",
            "device": "cpu",
            "embedding_dim": 1024,
            "max_length": 8192,
            "normalize_embeddings": True,
            "batch_size": 32,
            "pooling_strategy": "cls",
            "use_sentence_transformers": False,  # 默认使用Transformers而不是SentenceTransformers
            "cache_dir": None,
            "trust_remote_code": True
        }

        if config:
            default_config.update(config)

        super().__init__(
            model_name=default_config["model_name"],
            model_type=ModelType.EMBEDDING,
            provider=ProviderType.LOCAL,
            config=default_config
        )

        # 模型相关属性
        self.tokenizer = None
        self.model = None
        self.sentence_transformer = None
        self.device = self._setup_device()

        logger.info(f"初始化BGE-M3嵌入服务，设备: {self.device}")

    def _setup_device(self) -> torch.device:
        """
        设置计算设备

        Returns:
            torch.device: 计算设备
        """
        device_str = self.config.get("device", "cpu")
        if device_str == "auto":
            device_str = "cuda" if torch.cuda.is_available() else "cpu"

        device = torch.device(device_str)

        if device_str == "cuda":
            logger.info(f"使用GPU设备: {torch.cuda.get_device_name()}")
        else:
            logger.info("使用CPU设备")

        return device

    async def load_model(self) -> bool:
        """
        加载BGE-M3模型

        Returns:
            bool: 加载是否成功
        """
        try:
            self.update_status(ModelStatus.LOADING)
            logger.info(f"开始加载BGE-M3模型: {self.model_name}")

            # 在线程池中执行模型加载（CPU密集型操作）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model_sync)

            self.update_status(ModelStatus.LOADED)
            logger.info(f"BGE-M3模型加载成功，嵌入维度: {self.config['embedding_dim']}")
            return True

        except Exception as e:
            error_msg = f"BGE-M3模型加载失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _load_model_sync(self):
        """同步加载模型"""
        model_name = self.config["model_name"]
        model_path = self.config.get("model_path")
        cache_dir = self.config.get("cache_dir")

        logger.info(f"BGE配置: model_name={model_name}, model_path={model_path}, use_sentence_transformers={self.config.get('use_sentence_transformers')}, cache_dir={cache_dir}")

        # 优先使用本地路径
        import os
        if model_path and os.path.exists(model_path):
            logger.info(f"✅ 使用本地模型路径: {model_path}")
            model_name = model_path
            use_sentence_transformers = False
            cache_dir = None  # 本地路径不需要缓存
        elif model_path:
            logger.warning(f"⚠️ 本地模型路径不存在，将使用网络下载: {model_path}")
            use_sentence_transformers = self.config.get("use_sentence_transformers", True)
        else:
            logger.info(f"🌐 使用网络模型: {model_name}")
            use_sentence_transformers = self.config.get("use_sentence_transformers", True)

        # 根据配置选择加载方式
        if use_sentence_transformers:
            logger.info("使用SentenceTransformers加载BGE-M3模型")
            self.sentence_transformer = SentenceTransformer(
                model_name,
                device=self.device,
                cache_folder=cache_dir
            )
            # 设置模型配置
            if self.config.get("normalize_embeddings", True):
                self.sentence_transformer.normalize_embeddings = True
        else:
            logger.info("使用Transformers库手动加载BGE-M3模型")

            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True
            )

            # 加载模型
            self.model = AutoModel.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )

            # 移动模型到指定设备
            self.model.to(self.device)
            self.model.eval()  # 设置为评估模式

    async def unload_model(self) -> bool:
        """
        卸载BGE-M3模型

        Returns:
            bool: 卸载是否成功
        """
        try:
            logger.info(f"开始卸载BGE-M3模型: {self.model_name}")

            # 清理内存
            if self.sentence_transformer:
                del self.sentence_transformer
                self.sentence_transformer = None

            if self.model:
                del self.model
                self.model = None

            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None

            # 清理GPU内存
            if self.device.type == "cuda":
                torch.cuda.empty_cache()

            self.update_status(ModelStatus.UNLOADED)
            logger.info("BGE-M3模型卸载成功")
            return True

        except Exception as e:
            error_msg = f"BGE-M3模型卸载失败: {str(e)}"
            logger.error(error_msg)
            return False

    async def predict(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        文本嵌入预测

        Args:
            texts: 输入文本或文本列表
            **kwargs: 其他预测参数
                - batch_size: 批处理大小
                - show_progress: 是否显示进度
                - normalize_embeddings: 是否归一化嵌入向量

        Returns:
            np.ndarray: 文本嵌入向量数组

        Raises:
            AIModelException: 预测失败时抛出异常
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 标准化输入
            if isinstance(texts, str):
                texts = [texts]

            if not texts:
                raise AIModelException("输入文本不能为空", model_name=self.model_name)

            # 获取预测参数
            batch_size = kwargs.get("batch_size", self.config.get("batch_size", 32))
            show_progress = kwargs.get("show_progress", False)
            normalize_embeddings = kwargs.get("normalize_embeddings", self.config.get("normalize_embeddings", True))

            logger.info(f"开始文本嵌入预测，文本数量: {len(texts)}，批大小: {batch_size}")

            # 在线程池中执行嵌入计算
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self._encode_texts_sync, texts, batch_size, show_progress, normalize_embeddings
            )

            self.record_usage()
            logger.info(f"文本嵌入预测完成，输出形状: {embeddings.shape}")
            return embeddings

        except Exception as e:
            error_msg = f"文本嵌入预测失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _encode_texts_sync(self, texts: List[str], batch_size: int, show_progress: bool, normalize_embeddings: bool) -> np.ndarray:
        """
        同步执行文本编码

        Args:
            texts: 文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度
            normalize_embeddings: 是否归一化

        Returns:
            np.ndarray: 嵌入向量数组
        """
        if self.sentence_transformer:
            # 使用SentenceTransformers编码
            embeddings = self.sentence_transformer.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                normalize_embeddings=normalize_embeddings,
                convert_to_numpy=True
            )
        else:
            # 手动使用Transformers编码
            embeddings = self._encode_with_transformers(texts, batch_size, normalize_embeddings)

        # BGE-M3实际输出1024维向量，更新验证逻辑
        embedding_dim = embeddings.shape[1]
        if embedding_dim == 1024:
            logger.info(f"✅ BGE-M3正确生成 {embedding_dim} 维嵌入向量")
        elif embedding_dim == 768:
            logger.info(f"✅ BGE-M3生成 {embedding_dim} 维嵌入向量（标准模式）")
        else:
            logger.warning(f"⚠️ BGE-M3嵌入维度异常: {embedding_dim} (期望1024维)")

        return embeddings

    def _encode_with_transformers(self, texts: List[str], batch_size: int, normalize_embeddings: bool) -> np.ndarray:
        """
        使用Transformers库进行编码

        Args:
            texts: 文本列表
            batch_size: 批处理大小
            normalize_embeddings: 是否归一化

        Returns:
            np.ndarray: 嵌入向量数组
        """
        all_embeddings = []

        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # tokenize
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.config.get("max_length", 8192),
                return_tensors="pt"
            )

            # 移动到设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 推理
            with torch.no_grad():
                outputs = self.model(**inputs)

                # 获取CLS向量或平均池化
                if self.config.get("pooling_strategy", "cls") == "cls":
                    embeddings = outputs.last_hidden_state[:, 0, :]  # [batch_size, hidden_size]
                else:
                    # 平均池化
                    attention_mask = inputs["attention_mask"]
                    token_embeddings = outputs.last_hidden_state
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

            # 转换为numpy
            embeddings = embeddings.cpu().numpy()
            all_embeddings.append(embeddings)

        # 合并所有批次
        final_embeddings = np.vstack(all_embeddings)

        # 归一化
        if normalize_embeddings:
            final_embeddings = final_embeddings / np.linalg.norm(final_embeddings, axis=1, keepdims=True)

        return final_embeddings

    async def compute_similarity(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
        """
        计算查询向量与语料库向量的相似度

        Args:
            query_embedding: 查询向量 [1, embedding_dim] 或 [embedding_dim]
            corpus_embeddings: 语料库向量 [n_docs, embedding_dim]

        Returns:
            np.ndarray: 相似度分数 [n_docs]
        """
        try:
            # 确保query_embedding是2D
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            # 计算余弦相似度
            similarities = np.dot(corpus_embeddings, query_embedding.T).flatten()

            return similarities

        except Exception as e:
            error_msg = f"相似度计算失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def search_similar(self, query: str, corpus_texts: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        搜索相似文本

        Args:
            query: 查询文本
            corpus_texts: 语料库文本列表
            top_k: 返回Top-K结果

        Returns:
            List[Dict[str, Any]]: 相似文本列表，包含文本内容和相似度分数
        """
        try:
            # 编码查询文本
            query_embedding = await self.predict(query)

            # 编码语料库文本
            corpus_embeddings = await self.predict(corpus_texts)

            # 计算相似度
            similarities = await self.compute_similarity(query_embedding, corpus_embeddings)

            # 获取Top-K结果
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                results.append({
                    "text": corpus_texts[idx],
                    "similarity": float(similarities[idx]),
                    "index": int(idx)
                })

            return results

        except Exception as e:
            error_msg = f"相似文本搜索失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "embedding_dim": self.config.get("embedding_dim", 1024),
            "max_length": self.config.get("max_length", 8192),
            "device": str(self.device),
            "normalize_embeddings": self.config.get("normalize_embeddings", True),
            "pooling_strategy": self.config.get("pooling_strategy", "cls"),
            "use_sentence_transformers": self.config.get("use_sentence_transformers", True),
            "batch_size": self.config.get("batch_size", 32)
        }

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        return "这是一个测试文本"

    async def benchmark_performance(self, test_texts: List[str], num_runs: int = 3) -> Dict[str, Any]:
        """
        性能基准测试

        Args:
            test_texts: 测试文本列表
            num_runs: 运行次数

        Returns:
            Dict[str, Any]: 性能测试结果
        """
        try:
            logger.info(f"开始BGE-M3性能基准测试，文本数量: {len(test_texts)}, 运行次数: {num_runs}")

            times = []
            for run in range(num_runs):
                start_time = time.time()
                await self.predict(test_texts)
                end_time = time.time()
                times.append(end_time - start_time)
                logger.info(f"第{run + 1}次运行耗时: {times[-1]:.3f}秒")

            avg_time = np.mean(times)
            throughput = len(test_texts) / avg_time

            results = {
                "model_name": self.model_name,
                "num_texts": len(test_texts),
                "num_runs": num_runs,
                "times": times,
                "avg_time": float(avg_time),
                "min_time": float(np.min(times)),
                "max_time": float(np.max(times)),
                "throughput": float(throughput),  # texts per second
                "device": str(self.device)
            }

            logger.info(f"性能基准测试完成，平均耗时: {avg_time:.3f}秒，吞吐量: {throughput:.1f} texts/s")
            return results

        except Exception as e:
            error_msg = f"性能基准测试失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)


# 创建BGE-M3服务实例的工厂函数
def create_bge_service(config: Dict[str, Any] = None) -> BGEEmbeddingService:
    """
    创建BGE-M3嵌入服务实例

    Args:
        config: 模型配置参数

    Returns:
        BGEEmbeddingService: BGE-M3服务实例
    """
    return BGEEmbeddingService(config or {})