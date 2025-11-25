"""
搜索服务

整合向量搜索和全文搜索，提供统一的搜索接口。
支持语义搜索、全文搜索和混合搜索模式。
"""

import os
import pickle
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from app.utils.enum_helpers import get_enum_value, is_semantic_search, is_fulltext_search, is_hybrid_search

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
    logging.warning("whoosh未安装，全文搜索功能不可用")

from app.core.logging_config import get_logger
from app.schemas.enums import SearchType

logger = get_logger(__name__)

try:
    from app.services.ai_model_manager import ai_model_service
    AI_MODEL_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_MODEL_SERVICE_AVAILABLE = False
    ai_model_service = None
    logger.warning(f"AI模型服务不可用: {e}")


class SearchService:
    """统一搜索服务

    功能：
    - 向量搜索（使用BGE-M3嵌入和Faiss索引）
    - 全文搜索（使用Whoosh索引）
    - 混合搜索（向量+全文结果融合）
    - 搜索结果排序和过滤
    """

    def __init__(
        self,
        faiss_index_path: str,
        whoosh_index_path: str,
        use_ai_models: bool = True
    ):
        """初始化搜索服务

        Args:
            faiss_index_path: Faiss索引文件路径
            whoosh_index_path: Whoosh索引目录路径
            use_ai_models: 是否使用AI模型进行搜索
        """
        self.faiss_index_path = faiss_index_path
        self.whoosh_index_path = whoosh_index_path
        self.use_ai_models = use_ai_models

        # 搜索状态
        self.search_stats = {
            'total_searches': 0,
            'vector_searches': 0,
            'fulltext_searches': 0,
            'hybrid_searches': 0,
            'avg_response_time': 0.0
        }

        # 加载索引
        self._load_indexes()

    def _load_indexes(self):
        """加载搜索索引"""
        try:
            # 加载Faiss索引
            if FAISS_AVAILABLE and os.path.exists(self.faiss_index_path):
                self.faiss_index = faiss.read_index(self.faiss_index_path)

                # 加载元数据
                metadata_path = self.faiss_index_path.replace('.faiss', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'rb') as f:
                        self.faiss_metadata = pickle.load(f)
                    logger.info(f"Faiss索引加载成功，文档数: {self.faiss_index.ntotal}")
                else:
                    logger.warning("Faiss元数据文件不存在")
                    self.faiss_metadata = {}
            else:
                self.faiss_index = None
                self.faiss_metadata = {}
                logger.warning("Faiss索引不存在")

            # 加载Whoosh索引
            if WHOOSH_AVAILABLE and os.path.exists(self.whoosh_index_path):
                try:
                    # 直接使用路径字符串打开索引
                    self.whoosh_index = index.open_dir(self.whoosh_index_path)
                    logger.info("Whoosh全文索引加载成功")
                except Exception as whoosh_error:
                    logger.warning(f"Whoosh索引打开失败，尝试创建存储: {whoosh_error}")
                    try:
                        # 如果直接打开失败，尝试使用FileStorage
                        storage = FileStorage(self.whoosh_index_path)
                        self.whoosh_index = index.open_dir(storage)
                        logger.info("Whoosh全文索引加载成功（使用FileStorage）")
                    except Exception as storage_error:
                        logger.error(f"Whoosh索引加载完全失败: {storage_error}")
                        self.whoosh_index = None
            else:
                self.whoosh_index = None
                logger.warning("Whoosh索引不存在")

        except Exception as e:
            logger.error(f"加载搜索索引失败: {e}")
            self.faiss_index = None
            self.whoosh_index = None

    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.HYBRID,
        limit: int = 20,
        offset: int = 0,
        threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行搜索

        Args:
            query: 搜索查询
            search_type: 搜索类型 (semantic/fulltext/hybrid)
            limit: 返回结果数量
            offset: 结果偏移量
            threshold: 相似度阈值
            filters: 过滤条件

        Returns:
            Dict[str, Any]: 搜索结果
        """
        start_time = datetime.now()

        try:
            # 使用枚举辅助函数确保类型安全
            logger.info(f"DEBUG: search_type={search_type}, type={type(search_type)}")
            search_type_str = get_enum_value(search_type)
            logger.info(f"开始搜索: query='{query}', type={search_type_str}")

            # 根据搜索类型执行搜索
            if is_semantic_search(search_type):
                results = await self._semantic_search(query, limit, offset, threshold, filters)
                self.search_stats['vector_searches'] += 1
            elif is_fulltext_search(search_type):
                results = await self._fulltext_search(query, limit, offset, filters)
                self.search_stats['fulltext_searches'] += 1
            else:  # HYBRID
                results = await self._hybrid_search(query, limit, offset, threshold, filters)
                self.search_stats['hybrid_searches'] += 1

            # 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()

            # 更新统计信息
            self.search_stats['total_searches'] += 1
            total_time = self.search_stats['avg_response_time'] * (self.search_stats['total_searches'] - 1) + response_time
            self.search_stats['avg_response_time'] = total_time / self.search_stats['total_searches']

            # 添加搜索元数据
            results['search_time'] = round(response_time, 3)
            results['query_used'] = query
            results['search_type'] = get_enum_value(search_type)
            results['total_found'] = results.get('total', 0)

            logger.info(f"搜索完成: 结果数={results.get('total', 0)}, 耗时={response_time:.3f}秒")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'total': 0,
                'search_time': 0,
                'query_used': query,
                'search_type': get_enum_value(search_type)
            }

    async def _semantic_search(
        self,
        query: str,
        limit: int,
        offset: int,
        threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """语义搜索"""
        if not self.faiss_index or not self.use_ai_models:
            return {'success': False, 'results': [], 'total': 0, 'message': '向量搜索不可用'}

        try:
            # 使用AI模型生成查询向量
            if not AI_MODEL_SERVICE_AVAILABLE:
                return {'success': False, 'results': [], 'total': 0, 'message': 'AI模型服务不可用'}

            query_embedding = await ai_model_service.text_embedding(
                query,
                normalize_embeddings=True
            )

            # 执行向量搜索
            import numpy as np
            query_vector = np.array([query_embedding], dtype=np.float32)

            # 搜索最相似的向量
            k = min(limit + offset, self.faiss_index.ntotal)
            distances, indices = self.faiss_index.search(query_vector, k)

            # 处理结果
            results = []
            doc_ids = self.faiss_metadata.get('doc_ids', [])

            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(doc_ids):
                    similarity = float(distances[0][i])
                    if similarity >= threshold and i >= offset:
                        doc_id = doc_ids[idx]
                        doc_info = self._get_document_info(doc_id)
                        if doc_info:
                            results.append({
                                **doc_info,
                                'relevance_score': similarity,
                                'match_type': 'semantic',
                                'highlight': self._generate_highlight(doc_info, query)
                            })

            return {
                'success': True,
                'results': results,
                'total': len(results)
            }

        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return {'success': False, 'results': [], 'total': 0, 'error': str(e)}

    async def _fulltext_search(
        self,
        query: str,
        limit: int,
        offset: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """全文搜索"""
        if not self.whoosh_index:
            return {'success': False, 'results': [], 'total': 0, 'message': '全文搜索不可用'}

        try:
            results = []

            with self.whoosh_index.searcher() as searcher:
                # 构建查询
                parser = qparser.MultifieldParser(
                    ["title", "content", "file_name"],
                    self.whoosh_index.schema
                )
                query_obj = parser.parse(query)

                # 执行搜索
                search_results = searcher.search(query_obj, limit=limit + offset)

                # 处理结果
                for i, hit in enumerate(search_results):
                    if i >= offset:
                        doc_info = {
                            'id': hit['id'],
                            'title': hit.get('title', ''),
                            'file_path': hit.get('file_path', ''),
                            'file_name': hit.get('file_name', ''),
                            'file_type': hit.get('file_type', ''),
                            'file_size': hit.get('file_size', 0),
                            'modified_time': hit.get('modified_time'),
                            'preview_text': hit.highlights("content"),
                            'relevance_score': hit.score,
                            'match_type': 'fulltext',
                            'highlight': hit.highlights("content")
                        }
                        results.append(doc_info)

            return {
                'success': True,
                'results': results,
                'total': len(search_results)
            }

        except Exception as e:
            logger.error(f"全文搜索失败: {e}")
            return {'success': False, 'results': [], 'total': 0, 'error': str(e)}

    async def _hybrid_search(
        self,
        query: str,
        limit: int,
        offset: int,
        threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """混合搜索（向量+全文）"""
        try:
            # 并行执行语义搜索和全文搜索
            semantic_results = await self._semantic_search(query, limit, offset, threshold, filters)
            fulltext_results = await self._fulltext_search(query, limit, offset, filters)

            # 合并和重排序结果
            merged_results = self._merge_search_results(
                semantic_results.get('results', []),
                fulltext_results.get('results', []),
                limit
            )

            return {
                'success': True,
                'results': merged_results,
                'total': len(merged_results),
                'semantic_count': len(semantic_results.get('results', [])),
                'fulltext_count': len(fulltext_results.get('results', []))
            }

        except Exception as e:
            logger.error(f"混合搜索失败: {e}")
            return {'success': False, 'results': [], 'total': 0, 'error': str(e)}

    def _merge_search_results(
        self,
        semantic_results: List[Dict],
        fulltext_results: List[Dict],
        limit: int
    ) -> List[Dict]:
        """合并搜索结果"""
        # 使用文档ID去重
        seen_ids = set()
        merged = []

        # 优先添加语义搜索结果
        for result in semantic_results:
            doc_id = result.get('id')
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                # 混合搜索的得分更高
                result['relevance_score'] = min(result['relevance_score'] * 1.2, 1.0)
                result['match_type'] = 'hybrid'
                merged.append(result)

        # 添加全文搜索结果（去重）
        for result in fulltext_results:
            doc_id = result.get('id')
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                merged.append(result)

        # 按相关性得分排序
        merged.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return merged[:limit]

    def _get_document_info(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """根据文档ID获取文档信息"""
        try:
            # 从Whoosh索引中获取详细文档信息
            if self.whoosh_index:
                with self.whoosh_index.searcher() as searcher:
                    # 根据ID查找文档
                    from whoosh import query
                    q = query.Term("id", doc_id)
                    results = searcher.search(q, limit=1)

                    if results:
                        hit = results[0]
                        return {
                            'id': hit['id'],
                            'title': hit.get('title', ''),
                            'file_path': hit.get('file_path', ''),
                            'file_name': hit.get('file_name', ''),
                            'file_type': hit.get('file_type', ''),
                            'file_size': hit.get('file_size', 0),
                            'modified_time': hit.get('modified_time'),
                            'preview_text': hit.get('content', '')[:200] + '...' if hit.get('content') else ''
                        }

            return None

        except Exception as e:
            logger.error(f"获取文档信息失败 {doc_id}: {e}")
            return None

    def _generate_highlight(self, doc_info: Dict[str, Any], query: str) -> str:
        """生成搜索高亮"""
        try:
            preview = doc_info.get('preview_text', '')
            if not preview:
                return ''

            # 简单的高亮实现
            query_words = query.lower().split()
            words = preview.lower().split()

            highlighted_words = []
            for word in words:
                if any(q_word in word for q_word in query_words):
                    highlighted_words.append(f"<em>{word}</em>")
                else:
                    highlighted_words.append(word)

            return ' '.join(highlighted_words[:50])  # 限制长度

        except Exception as e:
            logger.error(f"生成高亮失败: {e}")
            return doc_info.get('preview_text', '')[:100]

    def get_search_stats(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        return self.search_stats.copy()

    def is_ready(self) -> bool:
        """检查搜索服务是否就绪"""
        return (self.faiss_index is not None) or (self.whoosh_index is not None)

    def get_index_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        info = {
            'faiss_available': self.faiss_index is not None,
            'whoosh_available': self.whoosh_index is not None,
            'ai_models_enabled': self.use_ai_models
        }

        if self.faiss_index:
            info['faiss_doc_count'] = self.faiss_index.ntotal
            info['faiss_dimension'] = self.faiss_index.d if hasattr(self.faiss_index, 'd') else 'unknown'

        if self.whoosh_index:
            with self.whoosh_index.searcher() as searcher:
                info['whoosh_doc_count'] = searcher.doc_count()

        return info


# 创建全局搜索服务实例
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """获取搜索服务实例"""
    global _search_service
    if _search_service is None:
        # 使用默认路径创建服务实例
        data_root = os.getenv('DATA_ROOT', '../data')
        faiss_path = os.path.join(data_root, 'indexes/faiss/document_index.faiss')
        whoosh_path = os.path.join(data_root, 'indexes/whoosh')

        _search_service = SearchService(
            faiss_index_path=faiss_path,
            whoosh_index_path=whoosh_path,
            use_ai_models=True
        )

    return _search_service


def reload_search_service():
    """重新加载搜索服务（索引更新后调用）"""
    global _search_service
    _search_service = None