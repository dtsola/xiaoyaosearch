"""
图像搜索服务
基于CLIP特征向量提供独立的图像搜索功能
采用完全基于特征向量的搜索方案，确保图像搜索基于真正的语义特征向量比对
"""
import asyncio
import logging
import os
import pickle
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
import faiss

from app.services.clip_service import get_clip_service
from app.core.logging_config import get_logger
from app.utils.enum_helpers import get_enum_value

logger = get_logger(__name__)


class ImageSearchService:
    """
    图像搜索服务

    基于CLIP特征向量的图像搜索实现，使用 chunk_index_service 构建的索引
    - 使用 chunk_index_service 已构建的图像索引
    - 完全基于特征向量的搜索，避免文本匹配错误
    - 专门负责图像搜索功能，索引构建由 chunk_index_service 处理
    """

    def __init__(self, index_path: str = None):
        """
        初始化图像搜索服务

        使用 chunk_index_service 已有的图像索引路径

        Args:
            index_path: 图像索引文件路径
        """
        self.clip_service = None
        # 使用 chunk_index_service 的索引路径
        base_path = index_path or "../data/indexes/faiss"
        self.index_path = os.path.join(base_path, "clip_image_index.faiss")
        self.metadata_path = os.path.join(base_path, "clip_image_metadata.pkl")

        # Faiss索引和元数据
        self.image_index = None
        self.image_metadata = {}  # {vector_id: {file_id, file_name, file_path, ...}}
        self.is_initialized = False
        self.vector_dimension = None  # CLIP图像向量维度

    async def initialize(self):
        """初始化图像搜索服务"""
        try:
            logger.info("初始化图像搜索服务")

            # 获取CLIP服务
            self.clip_service = get_clip_service()

            # 确保索引目录存在
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

            # 加载或创建图像索引
            await self._load_or_create_index()

            self.is_initialized = True
            logger.info("图像搜索服务初始化成功")

        except Exception as e:
            error_msg = f"图像搜索服务初始化失败: {str(e)}"
            logger.error(error_msg)
            self.is_initialized = False
            raise Exception(error_msg)

    async def _load_or_create_index(self):
        """加载或创建图像索引"""
        try:
            # 尝试加载现有索引
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                await self._load_existing_index()
            else:
                await self._create_new_index()

        except Exception as e:
            logger.warning(f"加载现有索引失败，创建新索引: {str(e)}")
            await self._create_new_index()

    async def _load_existing_index(self):
        """加载现有索引"""
        logger.info("加载现有图像索引")

        # 加载Faiss索引
        self.image_index = faiss.read_index(self.index_path)

        # 加载元数据
        with open(self.metadata_path, 'rb') as f:
            self.image_metadata = pickle.load(f)

        self.vector_dimension = self.image_index.d

        logger.info(f"图像索引加载成功，向量维度: {self.vector_dimension}, 图像数量: {len(self.image_metadata)}")

    async def _create_new_index(self):
        """创建新索引"""
        logger.info("创建新的图像索引")

        # 获取CLIP图像向量维度
        if not self.clip_service.is_ready():
            logger.info("CLIP模型未加载，开始加载...")
            await self.clip_service.load_model()

        # 创建一个测试向量来确定维度
        test_vector = await self._get_clip_vector_dimension()
        self.vector_dimension = len(test_vector)

        # 兜底检查：如果维度仍为0，使用CLIP默认维度
        if self.vector_dimension == 0:
            self.vector_dimension = 512
            logger.warning("使用CLIP默认向量维度: 512")

        # 创建Faiss索引（使用内积索引，适合余弦相似度）
        self.image_index = faiss.IndexFlatIP(self.vector_dimension)
        self.image_metadata = {}

        logger.info(f"新图像索引创建成功，向量维度: {self.vector_dimension}")

    async def _get_clip_vector_dimension(self) -> np.ndarray:
        """获取CLIP图像向量维度"""
        # 创建一个虚拟图像来测试向量维度
        try:
            from PIL import Image
            import numpy as np

            # 创建一个小的测试图像
            test_image = Image.new('RGB', (224, 224), color='white')
            test_vector = await self.clip_service.encode_image(test_image)
            return test_vector

        except Exception as e:
            # 如果失败，使用CLIP的默认维度
            logger.warning(f"无法测试CLIP向量维度，使用默认值: {str(e)}")
            return np.zeros(512)  # Chinese-CLIP的常见维度

    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        return True

    async def add_image(self, file_path: str, file_id: int, file_name: str) -> bool:
        """
        检查图像是否存在于索引中（只读模式）

        注意：索引构建由 chunk_index_service 负责，此服务只负责搜索

        Args:
            file_path: 图像文件路径
            file_id: 文件ID
            file_name: 文件名

        Returns:
            bool: 图像是否已存在于索引中
        """
        try:
            if not self.is_ready():
                logger.error("图像搜索服务未就绪")
                return False

            # 检查是否为图像文件
            if not self._is_image_file(file_path):
                logger.debug(f"跳过非图像文件: {file_path}")
                return True

            # 检查文件是否已存在
            existing_vector_id = self._find_image_by_path(file_path)
            if existing_vector_id is not None:
                logger.debug(f"图像已存在于索引中: {file_path}")
                return True

            logger.warning(f"图像不在索引中，需要通过 chunk_index_service 重建索引: {file_path}")
            return False

        except Exception as e:
            logger.error(f"检查图像失败 {file_path}: {str(e)}")
            return False

    def _is_image_file(self, file_path: str) -> bool:
        """检查文件是否为图像文件"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        return Path(file_path).suffix.lower() in image_extensions

    def _find_image_by_path(self, file_path: str) -> Optional[int]:
        """根据文件路径查找图像的向量ID"""
        for vector_id, metadata in self.image_metadata.items():
            if metadata.get('file_path') == file_path:
                return vector_id
        return None

    async def search_similar_images(
        self,
        query_vector: np.ndarray,
        limit: int = 20,
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用图像向量搜索相似图片

        Args:
            query_vector: 查询图像的特征向量
            limit: 返回结果数量限制
            threshold: 相似度阈值（余弦相似度）

        Returns:
            Dict[str, Any]: 搜索结果
        """
        start_time = time.time()

        if not self.is_ready():
            return {
                "success": False,
                "error": "图像搜索服务未就绪",
                "data": {"results": [], "total": 0, "search_time": 0}
            }

        try:
            logger.info(f"开始图像向量搜索，限制: {limit}, 阈值: {threshold}")

            # 确保向量维度已正确设置
            if self.vector_dimension is None:
                self.vector_dimension = len(query_vector)
                logger.info(f"设置图像向量维度: {self.vector_dimension}")

            # 确保查询向量维度正确
            if len(query_vector) != self.vector_dimension:
                error_msg = f"查询向量维度不匹配: 期望{self.vector_dimension}, 实际{len(query_vector)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "data": {"results": [], "total": 0, "search_time": 0}
                }

            # 归一化查询向量（用于余弦相似度）
            query_vector = query_vector / np.linalg.norm(query_vector)

            # 检查索引是否有图像
            if self.image_index.ntotal == 0:
                logger.info("图像索引为空")
                return {
                    "success": True,
                    "data": {
                        "results": [],
                        "total": 0,
                        "search_time": time.time() - start_time,
                        "query_type": "image_vector",
                        "index_status": "empty"
                    }
                }

            # 执行向量搜索
            query_vector = np.array([query_vector], dtype=np.float32)
            k = min(limit * 2, self.image_index.ntotal)  # 搜索更多结果用于过滤

            similarities, vector_ids = self.image_index.search(query_vector, k)

            # 处理搜索结果
            results = []
            for i, vector_id in enumerate(vector_ids[0]):
                if len(results) >= limit:
                    break

                similarity = float(similarities[0][i])

                # 过滤低相似度结果
                if similarity < threshold:
                    continue

                # 获取图像元数据
                metadata = self.image_metadata.get(int(vector_id))
                if metadata is None:
                    continue

                results.append({
                    'file_id': metadata['file_id'],
                    'file_name': metadata['file_name'],
                    'file_path': metadata['file_path'],
                    'file_type': metadata.get('file_type', 'image'),
                    'file_size': metadata.get('file_size', 0),
                    'created_at': metadata.get('created_at', ''),
                    'modified_at': metadata.get('modified_at', ''),
                    'similarity': similarity,
                    'vector_id': int(vector_id)
                })

            search_time = time.time() - start_time
            logger.info(f"图像搜索完成，找到 {len(results)} 个相似图片，耗时: {search_time:.3f}s")

            return {
                "success": True,
                "data": {
                    "results": results,
                    "total": len(results),
                    "search_time": search_time,
                    "query_type": "image_vector",
                    "threshold": threshold,
                    "index_size": self.image_index.ntotal
                }
            }

        except Exception as e:
            error_msg = f"图像搜索执行失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": {"results": [], "total": 0, "search_time": time.time() - start_time}
            }

    async def save_index(self) -> bool:
        """
        保存图像索引到磁盘

        Returns:
            bool: 保存是否成功
        """
        try:
            if not self.is_ready():
                logger.error("图像搜索服务未就绪，无法保存索引")
                return False

            logger.info(f"保存图像索引到: {self.index_path}")

            # 保存Faiss索引
            faiss.write_index(self.image_index, self.index_path)

            # 保存元数据
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.image_metadata, f)

            logger.info(f"图像索引保存成功，包含 {len(self.image_metadata)} 个图像")
            return True

        except Exception as e:
            logger.error(f"保存图像索引失败: {str(e)}")
            return False

    async def get_index_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        if not self.is_ready():
            return {
                "initialized": False,
                "total_images": 0,
                "vector_dimension": 0,
                "index_path": self.index_path
            }

        return {
            "initialized": True,
            "total_images": len(self.image_metadata),
            "vector_dimension": self.vector_dimension,
            "index_path": self.index_path,
            "faiss_index_total": self.image_index.ntotal if self.image_index else 0,
            "clip_service_ready": self.clip_service.is_ready() if self.clip_service else False
        }


# 全局实例
_image_search_service = None


def get_image_search_service() -> ImageSearchService:
    """
    获取图像搜索服务实例

    Returns:
        ImageSearchService: 图像搜索服务实例
    """
    global _image_search_service

    if _image_search_service is None:
        _image_search_service = ImageSearchService()

    return _image_search_service


async def ensure_image_search_service() -> ImageSearchService:
    """
    确保图像搜索服务已初始化

    Returns:
        ImageSearchService: 已初始化的图像搜索服务实例
    """
    service = get_image_search_service()

    if not service.is_initialized:
        await service.initialize()

    return service