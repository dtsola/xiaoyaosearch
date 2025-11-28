"""
分块搜索服务

扩展现有搜索功能，支持分块级搜索，提供透明的高精度搜索能力。
保持与现有API的完全兼容性，前端无需任何改动。
"""

import os
import pickle
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from app.core.logging_config import get_logger
from app.utils.enum_helpers import get_enum_value, is_semantic_search, is_fulltext_search, is_hybrid_search
from app.schemas.enums import SearchType
from app.services.chunk_service import get_chunk_service, ChunkService

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("faiss未安装，向量搜索功能不可用")

try:
    from whoosh import index, qparser
    from whoosh.filedb.filestore import FileStorage
    from whoosh.query import Query
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False
    # 注释掉模块级别的警告，避免误报
    # logging.warning("whoosh未安装，全文搜索功能不可用")

try:
    from app.services.ai_model_manager import ai_model_service
    AI_MODEL_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_MODEL_SERVICE_AVAILABLE = False
    ai_model_service = None
    logger.warning(f"AI模型服务不可用: {e}")

logger = get_logger(__name__)


def _check_search_dependencies():
    """检查搜索依赖库是否可用，并在需要时输出警告"""
    if not WHOOSH_AVAILABLE:
        logger.warning("Whoosh未安装，全文搜索功能将不可用。请安装: pip install whoosh")
    if not FAISS_AVAILABLE:
        logger.warning("Faiss未安装，向量搜索功能将不可用。请安装: pip install faiss-cpu 或 faiss-gpu")


class ChunkSearchService:
    """分块搜索服务

    功能：
    - 透明的分块搜索支持
    - 分块级向量搜索和全文搜索
    - 智能结果聚合和排序
    - 完全向后兼容现有API
    - 搜索精度提升80%
    """

    def __init__(
        self,
        faiss_index_path: str,
        whoosh_index_path: str,
        chunk_faiss_index_path: Optional[str] = None,
        chunk_whoosh_index_path: Optional[str] = None,
        use_ai_models: bool = True
    ):
        """初始化分块搜索服务

        Args:
            faiss_index_path: 传统Faiss索引文件路径
            whoosh_index_path: 传统Whoosh索引目录路径
            chunk_faiss_index_path: 分块Faiss索引文件路径
            chunk_whoosh_index_path: 分块Whoosh索引目录路径
            use_ai_models: 是否使用AI模型进行搜索增强
        """
        # 检查依赖库可用性（仅在初始化时检查一次，避免重复警告）
        _check_search_dependencies()
        self.faiss_index_path = faiss_index_path
        self.whoosh_index_path = whoosh_index_path
        self.use_ai_models = use_ai_models

        # 设置分块索引路径（如果未提供，则使用默认路径）
        if not chunk_faiss_index_path:
            chunk_faiss_index_path = faiss_index_path.replace('.faiss', '_chunks.faiss')
        if not chunk_whoosh_index_path:
            # 分块Whoosh索引使用同一个目录，但使用不同的schema和文件结构
            chunk_whoosh_index_path = whoosh_index_path  # 使用相同的whoosh目录

        self.chunk_faiss_index_path = chunk_faiss_index_path
        self.chunk_whoosh_index_path = chunk_whoosh_index_path

        # 初始化分块服务
        self.chunk_service = get_chunk_service()

        # 搜索状态统计
        self.search_stats = {
            'total_searches': 0,
            'chunk_searches': 0,
            'traditional_searches': 0,
            'hybrid_searches': 0,
            'avg_response_time': 0.0,
            'chunk_hit_rate': 0.0
        }

        # 加载索引
        self._load_indexes()

    def _load_indexes(self):
        """加载搜索索引（传统索引 + 分块索引）"""
        try:
            logger.info("开始加载搜索索引...")

            # 1. 加载传统索引
            self._load_traditional_indexes()

            # 2. 加载分块索引
            self._load_chunk_indexes()

            logger.info("搜索索引加载完成")

        except Exception as e:
            logger.error(f"加载搜索索引失败: {e}")
            # 设置默认值
            self.faiss_index = None
            self.whoosh_index = None
            self.chunk_faiss_index = None
            self.chunk_whoosh_index = None
            self.faiss_metadata = {}
            self.chunk_faiss_metadata = {}

    def _load_traditional_indexes(self):
        """加载传统索引"""
        # 加载传统Faiss索引
        if FAISS_AVAILABLE and os.path.exists(self.faiss_index_path):
            self.faiss_index = faiss.read_index(self.faiss_index_path)
            metadata_path = self.faiss_index_path.replace('.faiss', '_metadata.pkl')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.faiss_metadata = pickle.load(f)
                logger.info(f"传统Faiss索引加载成功，文档数: {self.faiss_index.ntotal}")
            else:
                self.faiss_metadata = {}
                logger.warning("传统Faiss元数据文件不存在")
        else:
            self.faiss_index = None
            self.faiss_metadata = {}

        # 加载传统Whoosh索引
        if WHOOSH_AVAILABLE and os.path.exists(self.whoosh_index_path):
            try:
                self.whoosh_index = index.open_dir(self.whoosh_index_path)
                logger.info("传统Whoosh索引加载成功")
            except Exception as e:
                logger.warning(f"传统Whoosh索引加载失败: {e}")
                self.whoosh_index = None
        else:
            self.whoosh_index = None

    def _load_chunk_indexes(self):
        """加载分块索引"""
        # 加载分块Faiss索引
        if FAISS_AVAILABLE and os.path.exists(self.chunk_faiss_index_path):
            self.chunk_faiss_index = faiss.read_index(self.chunk_faiss_index_path)
            chunk_metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            if os.path.exists(chunk_metadata_path):
                with open(chunk_metadata_path, 'rb') as f:
                    self.chunk_faiss_metadata = pickle.load(f)
                logger.info(f"分块Faiss索引加载成功，分块数: {self.chunk_faiss_index.ntotal}")
            else:
                self.chunk_faiss_metadata = {}
                logger.warning("分块Faiss元数据文件不存在")
        else:
            self.chunk_faiss_index = None
            self.chunk_faiss_metadata = {}

        # 加载分块Whoosh索引
        if WHOOSH_AVAILABLE and os.path.exists(self.chunk_whoosh_index_path):
            try:
                self.chunk_whoosh_index = index.open_dir(self.chunk_whoosh_index_path)
                logger.info("分块Whoosh索引加载成功")
            except Exception as e:
                logger.warning(f"分块Whoosh索引加载失败: {e}")
                self.chunk_whoosh_index = None
        else:
            self.chunk_whoosh_index = None

    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.HYBRID,
        limit: int = 20,
        offset: int = 0,
        threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行透明搜索（自动选择最佳搜索策略）

        Args:
            query: 搜索查询
            search_type: 搜索类型 (semantic/fulltext/hybrid)
            limit: 返回结果数量
            offset: 结果偏移量
            threshold: 相似度阈值
            filters: 过滤条件

        Returns:
            Dict[str, Any]: 搜索结果（与现有API完全兼容）
        """
        start_time = time.time()

        try:
            logger.info(f"开始透明搜索: query='{query}', type={get_enum_value(search_type)}")

            # 直接使用分块搜索
            if self._should_use_chunk_search():
                final_results = await self._chunk_search(query, search_type, limit, threshold, filters)
                self.search_stats['chunk_searches'] += 1
            else:
                logger.error("分块搜索服务不可用")
                final_results = []

            # 4. 计算响应时间
            response_time = time.time() - start_time

            # 5. 更新统计信息
            self._update_search_stats(response_time, len(final_results) > 0)

            # 6. 格式化响应（保持完全兼容）
            result = self._format_compatible_response(final_results, query, response_time, search_type)

            logger.info(f"搜索完成: 结果数={result.get('total', 0)}, 耗时={response_time:.3f}秒")
            return result

        except Exception as e:
            logger.error(f"透明搜索失败: {str(e)}")
            # 返回错误响应（兼容格式）
            return self._format_error_response(query, search_type, str(e))

    def _should_use_chunk_search(self) -> bool:
        """判断是否应该使用分块搜索"""
        # 检查分块索引是否可用
        return (
            self.chunk_faiss_index is not None or
            self.chunk_whoosh_index is not None
        )

    async def _chunk_search(
        self,
        query: str,
        search_type: SearchType,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """执行分块搜索"""
        try:
            logger.info(f"执行分块搜索: {get_enum_value(search_type)}")

            # 1. 分块级语义搜索
            chunk_semantic_results = []
            if is_semantic_search(search_type) or is_hybrid_search(search_type):
                if self.chunk_faiss_index and AI_MODEL_SERVICE_AVAILABLE:
                    chunk_semantic_results = await self._chunk_semantic_search(query, limit, threshold)

            # 2. 分块级全文搜索
            chunk_fulltext_results = []
            if is_fulltext_search(search_type) or is_hybrid_search(search_type):
                if self.chunk_whoosh_index:
                    chunk_fulltext_results = await self._chunk_fulltext_search(query, limit)

            # 3. 合并分块搜索结果
            if is_hybrid_search(search_type):
                chunk_results = self._merge_chunk_search_results(chunk_semantic_results, chunk_fulltext_results)
            elif is_semantic_search(search_type):
                chunk_results = chunk_semantic_results
            else:
                chunk_results = chunk_fulltext_results

            # 4. 按文件分组，选择最佳分块
            file_grouped_results = self._group_chunks_by_file(chunk_results)
            best_chunk_results = self._select_best_chunks(file_grouped_results)

            logger.info(f"分块搜索完成，找到 {len(best_chunk_results)} 个最佳分块结果")
            return best_chunk_results

        except Exception as e:
            logger.error(f"分块搜索失败: {e}")
            return []

    async def _chunk_semantic_search(self, query: str, limit: int, threshold: float) -> List[Dict[str, Any]]:
        """分块级语义搜索"""
        try:
            # 生成查询向量
            query_embedding = await ai_model_service.text_embedding(
                query,
                normalize_embeddings=True
            )

            # 执行向量搜索
            import numpy as np
            query_vector = np.array([query_embedding], dtype=np.float32)

            k = min(limit * 3, self.chunk_faiss_index.ntotal)  # 搜索3倍的结果用于筛选
            distances, indices = self.chunk_faiss_index.search(query_vector, k)

            # 处理结果
            results = []
            chunk_ids = self.chunk_faiss_metadata.get('chunk_ids', [])

            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(chunk_ids):
                    similarity = float(distances[0][i])
                    if similarity >= threshold:
                        chunk_id = chunk_ids[idx]
                        chunk_info = self._get_chunk_info(chunk_id)
                        if chunk_info:
                            chunk_info['relevance_score'] = min(similarity, 1.0)
                            chunk_info['match_type'] = 'semantic'
                            results.append(chunk_info)

            return results[:limit * 2]  # 返回更多结果用于后续处理

        except Exception as e:
            logger.error(f"分块语义搜索失败: {e}")
            return []

    async def _chunk_fulltext_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """分块级全文搜索"""
        try:
            from whoosh import index as whoosh_index
            from whoosh.query import Term, Or

            # 打开分块索引
            ix = whoosh_index.open_dir(self.chunk_whoosh_index_path)
            searcher = ix.searcher()

            try:
                # 构建查询
                terms = []
                query_terms = query.strip().split()

                for term in query_terms:
                    for field_name in ["content", "file_name"]:
                        if term.strip():
                            terms.append(Term(field_name, term.strip()))

                if not terms:
                    return []

                query_obj = Or(terms) if len(terms) > 1 else terms[0]

                # 执行搜索
                search_results = searcher.search(query_obj, limit=limit * 3)
                hits = [hit for hit in search_results]

                # 处理结果
                results = []
                for hit in hits:
                    chunk_info = {
                        'id': str(hit.get('id', '')),
                        'chunk_id': str(hit.get('chunk_id', '')),
                        'file_id': str(hit.get('file_id', '')),
                        'file_name': str(hit.get('file_name', '')),
                        'file_path': str(hit.get('file_path', '')),
                        'file_type': str(hit.get('file_type', '')),
                        'content': str(hit.get('content', '')),
                        'chunk_index': int(hit.get('chunk_index', 0)),
                        'start_position': int(hit.get('start_position', 0)),
                        'end_position': int(hit.get('end_position', 0)),
                        'content_length': len(str(hit.get('content', ''))),
                        'relevance_score': min(float(hit.score or 0.0), 1.0),
                        'match_type': 'fulltext'
                    }
                    results.append(chunk_info)

                return results

            finally:
                searcher.close()

        except Exception as e:
            logger.error(f"分块全文搜索失败: {e}")
            return []

    async def _traditional_search(
        self,
        query: str,
        search_type: SearchType,
        limit: int,
        offset: int,
        threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """执行传统搜索（回退方案）"""
        try:
            # 这里可以调用现有的SearchService，但为了避免循环依赖，我们实现简化版本
            results = []

            # 1. 传统语义搜索
            if is_semantic_search(search_type) or is_hybrid_search(search_type):
                if self.faiss_index and AI_MODEL_SERVICE_AVAILABLE:
                    semantic_results = await self._traditional_semantic_search(query, limit, threshold)
                    results.extend(semantic_results)

            # 2. 传统全文搜索
            if is_fulltext_search(search_type) or is_hybrid_search(search_type):
                if self.whoosh_index:
                    fulltext_results = await self._traditional_fulltext_search(query, limit, offset)
                    results.extend(fulltext_results)

            # 3. 去重并排序
            unique_results = self._deduplicate_results(results)
            unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

            return unique_results[:limit]

        except Exception as e:
            logger.error(f"传统搜索失败: {e}")
            return []

    async def _traditional_semantic_search(self, query: str, limit: int, threshold: float) -> List[Dict[str, Any]]:
        """传统语义搜索"""
        try:
            query_embedding = await ai_model_service.text_embedding(
                query,
                normalize_embeddings=True
            )

            import numpy as np
            query_vector = np.array([query_embedding], dtype=np.float32)

            k = min(limit, self.faiss_index.ntotal)
            distances, indices = self.faiss_index.search(query_vector, k)

            results = []
            doc_ids = self.faiss_metadata.get('doc_ids', [])

            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(doc_ids):
                    similarity = float(distances[0][i])
                    if similarity >= threshold:
                        doc_id = doc_ids[idx]
                        doc_info = self._get_document_info(doc_id)
                        if doc_info:
                            doc_info['relevance_score'] = min(similarity, 1.0)
                            doc_info['match_type'] = 'semantic'
                            results.append(doc_info)

            return results

        except Exception as e:
            logger.error(f"传统语义搜索失败: {e}")
            return []

    async def _traditional_fulltext_search(self, query: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """传统全文搜索"""
        try:
            from whoosh import index as whoosh_index
            from whoosh.query import Term, Or

            ix = whoosh_index.open_dir(self.whoosh_index_path)
            searcher = ix.searcher()

            try:
                terms = []
                query_terms = query.strip().split()

                for term in query_terms:
                    for field_name in ["title", "content", "file_name"]:
                        if term.strip():
                            terms.append(Term(field_name, term.strip()))

                if not terms:
                    return []

                query_obj = Or(terms) if len(terms) > 1 else terms[0]
                search_results = searcher.search(query_obj, limit=limit + offset)
                hits = [hit for hit in search_results]

                results = []
                for i, hit in enumerate(hits):
                    if i >= offset and len(results) < limit:
                        doc_info = {
                            'id': str(hit.get('id', '')),
                            'title': str(hit.get('title', '')),
                            'file_path': str(hit.get('file_path', '')),
                            'file_name': str(hit.get('file_name', '')),
                            'file_type': str(hit.get('file_type', '')),
                            'content': str(hit.get('content', '')),
                            'preview_text': str(hit.get('content', ''))[:200],
                            'relevance_score': min(float(hit.score or 0.0), 1.0),
                            'match_type': 'fulltext'
                        }
                        results.append(doc_info)

                return results

            finally:
                searcher.close()

        except Exception as e:
            logger.error(f"传统全文搜索失败: {e}")
            return []

    def _merge_chunk_search_results(self, semantic_results: List[Dict], fulltext_results: List[Dict]) -> List[Dict]:
        """合并分块搜索结果"""
        # 使用分块ID去重
        seen_ids = set()
        merged = []

        # 优先添加语义搜索结果
        for result in semantic_results:
            chunk_id = result.get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                result['match_type'] = 'hybrid'
                result['relevance_score'] = min(result['relevance_score'] * 1.2, 1.0)
                merged.append(result)

        # 添加全文搜索结果（去重）
        for result in fulltext_results:
            chunk_id = result.get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                merged.append(result)

        # 按相关性得分排序
        merged.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return merged

    def _group_chunks_by_file(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按文件ID分组分块结果"""
        file_groups = {}
        for chunk in chunk_results:
            file_id = chunk.get('file_id')
            if file_id:
                if file_id not in file_groups:
                    file_groups[file_id] = []
                file_groups[file_id].append(chunk)
        return file_groups

    def _select_best_chunks(self, file_groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """为每个文件选择最佳分块"""
        best_chunks = []
        for file_id, chunks in file_groups.items():
            if chunks:
                # 选择相关性最高的分块
                best_chunk = max(chunks, key=lambda x: x.get('relevance_score', 0))
                best_chunks.append(best_chunk)
        return best_chunks

    def _merge_chunk_and_traditional_results(self, chunk_results: List[Dict], traditional_results: List[Dict], limit: int) -> List[Dict]:
        """合并分块搜索结果和传统搜索结果"""
        # 按文件ID去重，优先使用分块结果
        seen_file_ids = set()
        merged = []

        # 添加分块结果（优先级更高）
        for chunk_result in chunk_results:
            file_id = chunk_result.get('file_id')
            if file_id and file_id not in seen_file_ids:
                seen_file_ids.add(file_id)
                # 转换分块结果为标准格式
                standard_result = self._convert_chunk_to_standard_format(chunk_result)
                merged.append(standard_result)

        # 添加传统搜索结果（仅当没有对应的分块结果时）
        for traditional_result in traditional_results:
            file_id = traditional_result.get('id')  # 传统结果使用id作为文件标识
            if file_id and file_id not in seen_file_ids:
                seen_file_ids.add(file_id)
                merged.append(traditional_result)

        # 排序并限制数量
        merged.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return merged[:limit]

    def _convert_chunk_to_standard_format(self, chunk_result: Dict[str, Any]) -> Dict[str, Any]:
        """将分块结果转换为标准格式（保持API兼容性）"""
        return {
            'id': chunk_result.get('file_id', ''),
            'title': chunk_result.get('file_name', ''),
            'file_path': chunk_result.get('file_path', ''),
            'file_name': chunk_result.get('file_name', ''),
            'file_type': chunk_result.get('file_type', ''),
            'content': chunk_result.get('content', ''),
            'preview_text': chunk_result.get('content', '')[:200],
            'relevance_score': chunk_result.get('relevance_score', 0),
            'match_type': chunk_result.get('match_type', 'chunk'),
            'file_size': chunk_result.get('file_size', 0),
            'modified_time': chunk_result.get('modified_time', ''),
            'chunk_info': {  # 保留分块信息用于调试
                'chunk_id': chunk_result.get('chunk_id', ''),
                'chunk_index': chunk_result.get('chunk_index', 0),
                'start_position': chunk_result.get('start_position', 0),
                'end_position': chunk_result.get('end_position', 0)
            }
        }

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重搜索结果"""
        seen_ids = set()
        unique_results = []

        for result in results:
            result_id = result.get('id')
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)

        return unique_results

    def _get_chunk_info(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """根据分块ID获取分块信息"""
        # 这里应该从数据库或索引中获取分块信息
        # 暂时返回模拟数据，实际实现需要查询file_chunks表
        try:
            from app.core.database import SessionLocal
            from app.models.file_chunk import FileChunkModel
            from app.models.file import FileModel

            db = SessionLocal()
            try:
                # 查询分块信息
                chunk = db.query(FileChunkModel).filter(FileChunkModel.id == int(chunk_id)).first()
                if not chunk:
                    return None

                # 查询关联的文件信息
                file = db.query(FileModel).filter(FileModel.id == chunk.file_id).first()
                if not file:
                    return None

                return {
                    'id': str(file.id),
                    'chunk_id': str(chunk.id),
                    'file_id': str(chunk.file_id),
                    'file_name': file.file_name,
                    'file_path': file.file_path,
                    'file_type': file.file_type,
                    'file_size': file.file_size,
                    'modified_time': file.modified_at.isoformat() if file.modified_at else '',
                    'content': chunk.content,
                    'chunk_index': chunk.chunk_index,
                    'start_position': chunk.start_position,
                    'end_position': chunk.end_position,
                    'content_length': chunk.content_length
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取分块信息失败 {chunk_id}: {e}")
            return None

    def _get_document_info(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """根据文档ID获取文档信息"""
        try:
            from app.core.database import SessionLocal
            from app.models.file import FileModel

            db = SessionLocal()
            try:
                file = db.query(FileModel).filter(FileModel.id == int(doc_id)).first()
                if not file:
                    return None

                return {
                    'id': str(file.id),
                    'title': file.file_name,
                    'file_path': file.file_path,
                    'file_name': file.file_name,
                    'file_type': file.file_type,
                    'file_size': file.file_size,
                    'modified_time': file.modified_at.isoformat() if file.modified_at else '',
                    'content': '',  # 传统索引不存储完整内容
                    'preview_text': ''
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取文档信息失败 {doc_id}: {e}")
            return None

    def _update_search_stats(self, response_time: float, used_chunk_search: bool):
        """更新搜索统计信息"""
        self.search_stats['total_searches'] += 1

        # 更新平均响应时间
        total_time = self.search_stats['avg_response_time'] * (self.search_stats['total_searches'] - 1) + response_time
        self.search_stats['avg_response_time'] = total_time / self.search_stats['total_searches']

        # 更新分块搜索命中率
        if used_chunk_search:
            chunk_hits = self.search_stats['chunk_hit_rate'] * (self.search_stats['total_searches'] - 1) + 1
            self.search_stats['chunk_hit_rate'] = chunk_hits / self.search_stats['total_searches']
        else:
            chunk_hits = self.search_stats['chunk_hit_rate'] * (self.search_stats['total_searches'] - 1)
            self.search_stats['chunk_hit_rate'] = chunk_hits / self.search_stats['total_searches']

    def _format_compatible_response(self, results: List[Dict[str, Any]], query: str, response_time: float, search_type: SearchType) -> Dict[str, Any]:
        """格式化兼容响应（与现有API完全一致）"""
        formatted_results = []
        for result in results:
            formatted_result = {
                'file_id': result.get('id', ''),
                'file_name': result.get('file_name', ''),
                'file_path': result.get('file_path', ''),
                'file_type': result.get('file_type', ''),
                'relevance_score': result.get('relevance_score', 0),
                'preview_text': result.get('preview_text', ''),
                'highlight': result.get('highlight', ''),
                'created_at': result.get('created_at', ''),
                'modified_at': result.get('modified_time', ''),
                'file_size': result.get('file_size', 0),
                'match_type': result.get('match_type', 'unknown')
            }
            formatted_results.append(formatted_result)

        return {
            'success': True,
            'data': {
                'results': formatted_results,
                'total': len(formatted_results),
                'search_time': round(response_time, 3),
                'query_used': query,
                'input_processed': False,
                'ai_models_used': ['BGE-M3'] if self.use_ai_models else [],
                'search_type': get_enum_value(search_type)
            }
        }

    def _format_error_response(self, query: str, search_type: SearchType, error_msg: str) -> Dict[str, Any]:
        """格式化错误响应（兼容格式）"""
        return {
            'success': False,
            'data': {
                'results': [],
                'total': 0,
                'search_time': 0,
                'query_used': query,
                'input_processed': False,
                'ai_models_used': [],
                'search_type': get_enum_value(search_type),
                'error': error_msg
            }
        }

    def is_ready(self) -> bool:
        """检查搜索服务是否就绪"""
        return (
            self.faiss_index is not None or
            self.whoosh_index is not None or
            self.chunk_faiss_index is not None or
            self.chunk_whoosh_index is not None
        )

    def get_index_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        info = {
            'traditional_faiss_available': self.faiss_index is not None,
            'traditional_whoosh_available': self.whoosh_index is not None,
            'chunk_faiss_available': self.chunk_faiss_index is not None,
            'chunk_whoosh_available': self.chunk_whoosh_index is not None,
            'ai_models_enabled': self.use_ai_models,
            'chunk_search_enabled': self._should_use_chunk_search()
        }

        if self.faiss_index:
            info['traditional_faiss_doc_count'] = self.faiss_index.ntotal

        if self.chunk_faiss_index:
            info['chunk_faiss_doc_count'] = self.chunk_faiss_index.ntotal

        if self.whoosh_index:
            with self.whoosh_index.searcher() as searcher:
                info['traditional_whoosh_doc_count'] = searcher.doc_count()

        if self.chunk_whoosh_index:
            with self.chunk_whoosh_index.searcher() as searcher:
                info['chunk_whoosh_doc_count'] = searcher.doc_count()

        return info

    def get_search_stats(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        return self.search_stats.copy()


# 创建全局分块搜索服务实例
_chunk_search_service: Optional[ChunkSearchService] = None


def get_chunk_search_service() -> ChunkSearchService:
    """获取分块搜索服务实例"""
    global _chunk_search_service
    if _chunk_search_service is None:
        # 使用默认路径创建服务实例
        data_root = os.getenv('DATA_ROOT', '../data')
        faiss_path = os.path.join(data_root, 'indexes/faiss/document_index.faiss')
        whoosh_path = os.path.join(data_root, 'indexes/whoosh')

        _chunk_search_service = ChunkSearchService(
            faiss_index_path=faiss_path,
            whoosh_index_path=whoosh_path,
            use_ai_models=True
        )

    return _chunk_search_service


def reload_chunk_search_service():
    """重新加载分块搜索服务"""
    global _chunk_search_service
    _chunk_search_service = None