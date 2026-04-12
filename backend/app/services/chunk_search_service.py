"""
分块搜索服务
"""

import os
import pickle
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.core.logging_config import get_logger, logger
from app.utils.enum_helpers import get_enum_value, is_semantic_search, is_fulltext_search, is_hybrid_search
from app.schemas.enums import SearchType
from app.services.chunk_service import get_chunk_service, ChunkService
from typing import Optional, List, Dict, Any
import faiss
import numpy as np
from whoosh import index, qparser
from whoosh.filedb.filestore import FileStorage
from whoosh.query import Query
from app.services.ai_model_manager import ai_model_service
from app.services.glossary_service import GlossaryService
from app.services.glossary_service import GlossaryService


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
        chunk_faiss_index_path: str,
        chunk_whoosh_index_path: str,
        use_ai_models: bool = True,
        enable_glossary_expansion: bool = False,
        glossary_collection_ids: Optional[List[int]] = None,
        max_expansion_terms: int = 3
    ):
        """初始化分块搜索服务

        Args:
            chunk_faiss_index_path: 分块Faiss索引文件路径
            chunk_whoosh_index_path: 分块Whoosh索引目录路径
            use_ai_models: 是否使用AI模型进行搜索增强
            enable_glossary_expansion: 是否启用术语扩展
            glossary_collection_ids: 使用的术语库ID列表，None表示全部
            max_expansion_terms: 术语扩展最大词数（包含原词），默认3
        """
        self.use_ai_models = use_ai_models
        self.enable_glossary_expansion = enable_glossary_expansion
        self.glossary_collection_ids = glossary_collection_ids
        self.max_expansion_terms = max(1, min(max_expansion_terms, 20))  # 限制在1-20之间

        self.chunk_faiss_index_path = chunk_faiss_index_path
        self.chunk_whoosh_index_path = chunk_whoosh_index_path

        # 初始化分块服务
        self.chunk_service = get_chunk_service()

        # 初始化术语扩展服务
        self.glossary_service = GlossaryService()

        # 搜索状态统计
        self.search_stats = {
            'total_searches': 0,
            'chunk_searches': 0,
            'hybrid_searches': 0,
            'avg_response_time': 0.0,
            'chunk_hit_rate': 0.0,
            'glossary_expansions': 0,
            'glossary_matches': 0,
            'expansion_searches_used': 0,
            'expansion_avg_terms': 0
        }

        # 加载索引
        self._load_indexes()

    def _load_indexes(self):
        """加载搜索索引（分块索引）"""
        try:
            logger.info("开始加载搜索索引...")

            # 加载分块索引
            self._load_chunk_indexes()

            logger.info("搜索索引加载完成")

        except Exception as e:
            logger.error(f"加载搜索索引失败: {e}")
            # 设置默认值
            self.chunk_faiss_index = None
            self.chunk_whoosh_index = None
            self.chunk_faiss_metadata = {}

  
    def _load_chunk_indexes(self):
        """加载分块索引"""
        # 加载分块Faiss索引
        if os.path.exists(self.chunk_faiss_index_path):
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
        if os.path.exists(self.chunk_whoosh_index_path):
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
        glossary_info = None
        queries_used = [query]  # 记录实际使用的查询词

        try:
            # 术语扩展并并发搜索
            if self.enable_glossary_expansion:
                try:
                    glossary_result = self.glossary_service.expand_query(
                        query,
                        self.glossary_collection_ids
                    )

                    if glossary_result.matched_terms:
                        logger.info(f"术语扩展匹配: {len(glossary_result.matched_terms)} 个术语")

                        # 准备扩展查询词列表（限制数量）
                        expanded_queries = [query]  # 原始查询始终包含
                        for exp_query in glossary_result.expanded_queries[1:]:
                            if exp_query != query and len(expanded_queries) < self.max_expansion_terms:
                                expanded_queries.append(exp_query)

                        if len(expanded_queries) > 1:
                            logger.info(f"执行术语扩展并发搜索: {len(expanded_queries)} 个查询词")
                            logger.info(f"查询词列表: {expanded_queries}")
                            self.search_stats['glossary_expansions'] += 1
                            self.search_stats['glossary_matches'] += len(glossary_result.matched_terms)
                            self.search_stats['expansion_searches_used'] += 1
                            self.search_stats['expansion_avg_terms'] = (
                                self.search_stats['expansion_avg_terms'] * (self.search_stats['expansion_searches_used'] - 1) + len(expanded_queries)
                            ) / self.search_stats['expansion_searches_used']

                            queries_used = expanded_queries
                            glossary_info = glossary_result

                            # 并发搜索所有查询词
                            should_use_chunk = self._should_use_chunk_search()
                            if should_use_chunk:
                                search_tasks = [
                                    self._chunk_search(q, search_type, limit, threshold, filters)
                                    for q in expanded_queries
                                ]
                                all_results = await asyncio.gather(*search_tasks)

                                # 合并结果
                                final_results = self._merge_expansion_search_results(all_results)
                                logger.info(f"术语扩展搜索完成，合并后结果数量: {len(final_results)}")
                            else:
                                logger.error("分块搜索服务不可用")
                                final_results = []
                        else:
                            # 扩展词与原词重复，使用原词搜索
                            logger.info("扩展词与原词重复，使用原词搜索")
                            final_results = await self._chunk_search(query, search_type, limit, threshold, filters)
                            glossary_info = glossary_result
                    else:
                        # 没有匹配的术语，使用原词搜索
                        final_results = await self._chunk_search(query, search_type, limit, threshold, filters)
                except Exception as e:
                    logger.warning(f"术语扩展失败: {str(e)}，使用原词搜索")
                    final_results = await self._chunk_search(query, search_type, limit, threshold, filters)
            else:
                # 未启用术语扩展，直接搜索
                logger.info(f"开始透明搜索: query='{query}', type={get_enum_value(search_type)}")

                # 调试信息
                should_use_chunk = self._should_use_chunk_search()
                logger.info(f"是否使用分块搜索: {should_use_chunk}")
                logger.info(f"chunk_faiss_index存在: {self.chunk_faiss_index is not None}")
                logger.info(f"chunk_whoosh_index存在: {self.chunk_whoosh_index is not None}")

                # 直接使用分块搜索
                if should_use_chunk:
                    logger.info("执行分块搜索...")
                    final_results = await self._chunk_search(query, search_type, limit, threshold, filters)
                    logger.info(f"分块搜索完成，结果数量: {len(final_results)}")
                    self.search_stats['chunk_searches'] += 1
                else:
                    logger.error("分块搜索服务不可用")
                    final_results = []

            # 计算响应时间
            response_time = time.time() - start_time

            # 更新统计信息
            self._update_search_stats(response_time, len(final_results) > 0)

            # 格式化响应（保持完全兼容）
            result = self._format_compatible_response(
                final_results,
                query,
                response_time,
                search_type,
                glossary_info,
                queries_used
            )

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
                if self.chunk_faiss_index:
                    chunk_semantic_results = await self._chunk_semantic_search(query, limit, threshold, filters)

            # 2. 分块级全文搜索
            chunk_fulltext_results = []
            if is_fulltext_search(search_type) or is_hybrid_search(search_type):
                if self.chunk_whoosh_index:
                    chunk_fulltext_results = await self._chunk_fulltext_search(query, limit, filters)

            # 3. 合并分块搜索结果
            if is_hybrid_search(search_type):
                chunk_results = self._merge_chunk_search_results(chunk_semantic_results, chunk_fulltext_results)
            elif is_semantic_search(search_type):
                chunk_results = chunk_semantic_results
            else:
                chunk_results = chunk_fulltext_results

            logger.info(f"搜索结果统计: 语义={len(chunk_semantic_results)}, 全文={len(chunk_fulltext_results)}, 合并后={len(chunk_results)}")

            # 4. 按文件分组，选择最佳分块
            file_grouped_results = self._group_chunks_by_file(chunk_results)
            best_chunk_results = self._select_best_chunks(file_grouped_results)

            logger.info(f"分块搜索完成，找到 {len(best_chunk_results)} 个最佳分块结果")
            return best_chunk_results

        except Exception as e:
            logger.error(f"分块搜索失败: {e}")
            return []

    def _map_file_type_to_enum(self, file_type: str) -> str:
        """将文件类型映射到枚举值

        Args:
            file_type: 原始文件类型（可能是扩展名如 'jpg' 或类型如 'image'）

        Returns:
            str: 映射后的枚举值
        """
        if not file_type:
            logger.warning(f"文件类型为空，默认归类为document")
            return 'document'

        file_type_lower = file_type.lower()

        # 如果已经是标准类型，直接返回
        if file_type_lower in ['video', 'audio', 'document', 'image']:
            return file_type_lower

        # 文档类型（扩展名）
        document_types = {
            'pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'rtf', 'odt', 'ods', 'odp', 'md', 'markdown', 'tex', 'latex',
            'csv', 'json', 'xml', 'html', 'htm', 'epub', 'mobi', 'azw'
        }

        # 视频类型（扩展名）
        video_types = {
            'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp',
            'mpg', 'mpeg', 'ogv', 'ts', 'mts', 'm2ts', 'vob', 'f4v'
        }

        # 音频类型（扩展名）
        audio_types = {
            'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus',
            'aiff', 'au', 'ra', 'amr', 'ac3', 'dts', 'mka'
        }

        # 图片类型（扩展名）
        image_types = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp',
            'svg', 'ico', 'psd', 'ai', 'eps', 'raw', 'cr2', 'nef', 'arw'
        }

        if file_type_lower in document_types:
            return 'document'
        elif file_type_lower in video_types:
            return 'video'
        elif file_type_lower in audio_types:
            return 'audio'
        elif file_type_lower in image_types:
            return 'image'
        else:
            logger.warning(f"未知的文件类型 '{file_type}'，默认归类为document")
            return 'document'

    async def _chunk_semantic_search(self, query: str, limit: int, threshold: float, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """分块级语义搜索"""
        try:
            # 检查索引是否可用
            if self.chunk_faiss_index is None:
                logger.warning("分块Faiss索引未加载，跳过语义搜索")
                return []

            if self.chunk_faiss_index.ntotal == 0:
                logger.warning("分块Faiss索引为空，跳过语义搜索")
                return []

            # 生成查询向量
            query_embedding = await ai_model_service.text_embedding(
                query,
                normalize_embeddings=True
            )

            # 执行向量搜索
            import numpy as np

            # 检查查询向量的维度和形状
            query_embedding = np.array(query_embedding, dtype=np.float32)
            logger.debug(f"查询嵌入向量形状: {query_embedding.shape}")

            # 确保查询向量是二维的 (1, d)
            if len(query_embedding.shape) == 1:
                query_vector = query_embedding.reshape(1, -1)
            else:
                query_vector = query_embedding

            logger.debug(f"查询向量最终形状: {query_vector.shape}")
            logger.debug(f"Faiss索引维度: {self.chunk_faiss_index.d}")

            k = min(limit * 3, self.chunk_faiss_index.ntotal)  # 搜索3倍的结果用于筛选

            # 检查向量维度是否匹配
            if query_vector.shape[1] != self.chunk_faiss_index.d:
                logger.error(f"向量维度不匹配: 查询向量={query_vector.shape[1]}, 索引={self.chunk_faiss_index.d}")
                return []

            # 安全的搜索操作 - 直接解包返回值
            distances, indices = self.chunk_faiss_index.search(query_vector, k)

            # 检查返回值的形状
            if distances is None or indices is None:
                logger.error("Faiss搜索返回空值")
                return []

            # 确保返回的数组形状正确
            if hasattr(distances, 'shape') and hasattr(indices, 'shape'):
                logger.debug(f"搜索返回形状 - distances: {distances.shape}, indices: {indices.shape}")
            else:
                logger.error("Faiss搜索返回的数组没有shape属性")
                return []

            # 处理结果
            results = []
            chunk_ids = self.chunk_faiss_metadata.get('chunk_ids', [])

            # 确保indices是二维数组
            if len(indices.shape) == 1:
                indices = indices.reshape(1, -1)
                distances = distances.reshape(1, -1)

            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(chunk_ids):
                    similarity = float(distances[0][i])
                    if similarity >= threshold:
                        chunk_id = chunk_ids[idx]
                        chunk_info = self._get_chunk_info(chunk_id, query)
                        if chunk_info:
                            # 应用文件类型过滤
                            if filters and 'file_types' in filters and filters['file_types']:
                                # 将文件类型映射到枚举值
                                mapped_file_type = self._map_file_type_to_enum(chunk_info.get('file_type', ''))
                                if mapped_file_type not in filters['file_types']:
                                    continue  # 跳过不符合过滤条件的文件

                            chunk_info['relevance_score'] = min(similarity, 1.0)
                            chunk_info['match_type'] = 'semantic'
                            results.append(chunk_info)

            logger.info(f"搜索完成: 结果数={len(results)}")

            return results[:limit * 2]  # 返回更多结果用于后续处理

        except Exception as e:
            logger.error(f"分块语义搜索失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return []

    async def _chunk_fulltext_search(self, query: str, limit: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """分块级全文搜索"""
        try:
            from whoosh import index as whoosh_index
            from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
            from whoosh.query import And, Or, Term
            from app.core.database import SessionLocal
            from app.models.file import FileModel

            # 打开分块索引
            ix = whoosh_index.open_dir(self.chunk_whoosh_index_path)
            searcher = ix.searcher()

            try:
                query_str = query.strip()
                logger.info(f"执行全文搜索: '{query_str}'")

                # 创建多字段查询解析器，同时搜索内容和文件名
                parser = MultifieldParser(["content", "file_name"],
                                        ix.schema, group=OrGroup)

                # 设置查询为模糊搜索，支持中文
                # 对于中文，我们使用通配符和短语查询
                if len(query_str) == 1:
                    # 单个字符，使用通配符搜索
                    query_obj = parser.parse(f"*{query_str}*")
                else:
                    # 多个字符，尝试精确匹配和模糊匹配
                    exact_query = parser.parse(f'"{query_str}"')  # 短语查询
                    fuzzy_terms = []

                    # 为每个字段创建通配符查询
                    for field in ["content", "file_name"]:
                        fuzzy_terms.append(Term(field, query_str))
                        fuzzy_terms.append(parser.parse(f"{field}:*{query_str}*"))

                    # 组合查询：精确匹配或模糊匹配
                    if fuzzy_terms:
                        query_obj = Or([exact_query] + fuzzy_terms)
                    else:
                        query_obj = exact_query

                logger.debug(f"全文搜索查询对象: {query_obj}")

                # 执行搜索
                search_results = searcher.search(query_obj, limit=limit * 3)
                hits = [hit for hit in search_results]

                logger.info(f"全文搜索找到 {len(hits)} 个结果")

                # 收集所有 file_id，批量从数据库读取 source_type 和 source_url
                file_ids = set()
                for hit in hits:
                    file_id = hit.get('file_id')
                    if file_id:
                        file_ids.add(int(file_id))

                # 批量查询数据库获取数据源信息
                file_source_info = {}
                if file_ids:
                    db = SessionLocal()
                    try:
                        files = db.query(FileModel).filter(FileModel.id.in_(file_ids)).all()
                        for file in files:
                            file_source_info[file.id] = {
                                'source_type': file.source_type,
                                'source_url': file.source_url
                            }
                    finally:
                        db.close()

                # 处理结果
                results = []
                for hit in hits:
                    # 获取实际存储的内容
                    content = hit.get('content', '')
                    if not content:
                        content = hit.get('content_stored', '')

                    # 获取文件类型
                    file_type = str(hit.get('file_type', ''))

                    # 应用文件类型过滤
                    if filters and 'file_types' in filters and filters['file_types']:
                        # 将文件类型映射到枚举值
                        mapped_file_type = self._map_file_type_to_enum(file_type)
                        # file_types 是 FileType 枚举列表，需要转换为字符串比较
                        filter_types = [ft.value if hasattr(ft, 'value') else str(ft) for ft in filters['file_types']]
                        if mapped_file_type not in filter_types:
                            file_name = str(hit.get('file_name', ''))
                            logger.debug(f"文件 {file_name} 被过滤: 原始类型={file_type}, 映射类型={mapped_file_type}, 过滤条件={filter_types}")
                            continue  # 跳过不符合过滤条件的文件

                    # 获取文件ID用于查询数据源信息
                    file_id = int(hit.get('file_id', 0))
                    source_info = file_source_info.get(file_id, {'source_type': None, 'source_url': None})

                    # 从索引获取基本信息，从数据库获取数据源信息
                    chunk_info = {
                        'id': str(hit.get('file_id', '')),
                        'chunk_id': str(hit.get('chunk_id', '')),
                        'file_id': str(hit.get('file_id', '')),
                        'file_name': str(hit.get('file_name', '')),
                        'file_path': str(hit.get('file_path', '')),
                        'file_type': file_type,
                        'file_size': int(hit.get('file_size', 0)),
                        'content': content,
                        'chunk_index': int(hit.get('chunk_index', 0)),
                        'start_position': int(hit.get('start_position', 0)),
                        'end_position': int(hit.get('end_position', 0)),
                        'content_length': int(hit.get('content_length', 0)),
                        'created_at': hit.get('created_at'),
                        'modified_time': hit.get('modified_time'),
                        'relevance_score': min(float(hit.score or 0.0), 1.0),
                        'match_type': 'fulltext',
                        # 数据源信息（从数据库读取，保持与语义搜索一致）
                        'source_type': source_info['source_type'],
                        'source_url': source_info['source_url']
                    }

                    # 生成预览文本和高亮
                    if content:
                        chunk_info['preview_text'] = self._generate_preview_text(content)
                        chunk_info['highlight'] = self._generate_highlight(content, query_str)

                    results.append(chunk_info)
                    logger.debug(f"添加分块结果: file_id={chunk_info['file_id']}, file_name={chunk_info['file_name']}, score={chunk_info['relevance_score']}")

                return results

            finally:
                searcher.close()

        except Exception as e:
            logger.error(f"分块全文搜索失败: {e}")
            return []

    
    
    
    def _merge_chunk_search_results(self, semantic_results: List[Dict], fulltext_results: List[Dict]) -> List[Dict]:
        """合并分块搜索结果

        合并策略：
        1. 语义搜索结果：优先添加，提升10%权重
        2. 全文搜索结果：补充添加，降权49%（突出语义搜索优势）
        3. 使用chunk_id去重
        """
        seen_ids = set()
        merged = []

        # 优先添加语义搜索结果
        for result in semantic_results:
            chunk_id = result.get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                result['match_type'] = 'hybrid'
                # 语义搜索轻微提升10%权重
                result['relevance_score'] = min(result['relevance_score'] * 1.1, 1.0)
                merged.append(result)

        # 添加全文搜索结果（去重）
        for result in fulltext_results:
            chunk_id = result.get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                # 全文搜索降权49%
                result['relevance_score'] = result['relevance_score'] * 0.51
                merged.append(result)

        # 按相关性得分排序
        merged.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return merged

    def _group_chunks_by_file(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按文件ID分组分块结果"""
        file_groups = {}
        logger.info(f"开始分组 {len(chunk_results)} 个分块结果")
        for chunk in chunk_results:
            file_id = chunk.get('file_id')
            logger.info(f"处理分块: chunk_id={chunk.get('chunk_id')}, file_id={file_id}, file_name={chunk.get('file_name')}")
            if file_id:
                if file_id not in file_groups:
                    file_groups[file_id] = []
                file_groups[file_id].append(chunk)
            else:
                logger.warning(f"发现没有file_id的分块: {chunk.get('chunk_id', 'unknown')}")
        logger.info(f"分组完成: {len(file_groups)} 个文件组")
        return file_groups

    def _select_best_chunks(self, file_groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """为每个文件选择最佳分块"""
        best_chunks = []
        logger.info(f"开始为 {len(file_groups)} 个文件组选择最佳分块")
        for file_id, chunks in file_groups.items():
            logger.info(f"文件组 {file_id} 有 {len(chunks)} 个分块")
            if chunks:
                # 选择相关性最高的分块
                best_chunk = max(chunks, key=lambda x: x.get('relevance_score', 0))
                best_chunks.append(best_chunk)
                logger.info(f"文件 {file_id} 选择了最佳分块: {best_chunk.get('chunk_id')}, score={best_chunk.get('relevance_score')}")
        return best_chunks

    
    def _convert_chunk_to_standard_format(self, chunk_result: Dict[str, Any]) -> Dict[str, Any]:
        """将分块结果转换为标准格式"""
        # 映射文件类型到枚举值
        file_type = self._map_file_type_to_enum(chunk_result.get('file_type', ''))

        return {
            'id': chunk_result.get('file_id', ''),
            'title': chunk_result.get('file_name', ''),
            'file_path': chunk_result.get('file_path', ''),
            'file_name': chunk_result.get('file_name', ''),
            'file_type': file_type,
            'content': chunk_result.get('content', ''),
            'preview_text': self._generate_preview_text(chunk_result.get('content', '')),
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

    def _get_chunk_info(self, chunk_id: str, query: str = '') -> Optional[Dict[str, Any]]:
        """根据分块ID获取分块信息"""
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

                # 生成预览文本和高亮
                content = chunk.content or ''
                preview_text = self._generate_preview_text(content)
                highlight = self._generate_highlight(content, query) if query else content[:100] + '...' if len(content) > 100 else content

                return {
                    'id': str(file.id),
                    'chunk_id': str(chunk.id),
                    'file_id': str(chunk.file_id),
                    'file_name': file.file_name,
                    'file_path': file.file_path,
                    'file_type': file.file_type,
                    'file_size': file.file_size,
                    'created_at': file.created_at.isoformat() if file.created_at else None,
                    'modified_time': file.modified_at.isoformat() if file.modified_at else None,
                    'content': content,
                    'preview_text': preview_text,
                    'highlight': highlight,
                    'chunk_index': chunk.chunk_index,
                    'start_position': chunk.start_position,
                    'end_position': chunk.end_position,
                    'content_length': chunk.content_length,
                    # 数据源信息（插件系统）
                    'source_type': file.source_type,
                    'source_url': file.source_url
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取分块信息失败 {chunk_id}: {e}")
            return None

    def _generate_preview_text(self, content: str) -> str:
        """生成预览文本，严格限制200字符"""
        if not content:
            return ''

        # 严格限制预览文本为200字符
        if len(content) > 197:  # 197 + '...' = 200
            return content[:197] + '...'
        else:
            return content

    def _generate_highlight(self, content: str, query: str) -> str:
        """生成搜索高亮片段

        Args:
            content: 文本内容
            query: 搜索查询词

        Returns:
            str: 高亮片段
        """
        if not content or not query:
            return content[:100] + '...' if len(content) > 100 else content

        # 查找查询词首次出现的位置
        query_lower = query.lower()
        content_lower = content.lower()
        pos = content_lower.find(query_lower)

        if pos == -1:
            # 如果没找到，返回前100个字符
            return content[:100] + '...' if len(content) > 100 else content

        # 提取查询词周围的文本（前后各50字符）
        start = max(0, pos - 50)
        end = min(len(content), pos + len(query) + 50)

        highlight = content[start:end]

        # 如果不是从头开始，添加省略号
        if start > 0:
            highlight = '...' + highlight

        # 如果不是到结尾，添加省略号
        if end < len(content):
            highlight = highlight + '...'

        return highlight

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

    def _format_compatible_response(
        self,
        results: List[Dict[str, Any]],
        query: str,
        response_time: float,
        search_type: SearchType,
        glossary_info: Optional[Any] = None,
        queries_used: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """格式化兼容响应（与现有API完全一致）

        Args:
            results: 搜索结果列表
            query: 原始查询词
            response_time: 响应时间
            search_type: 搜索类型
            glossary_info: 术语扩展信息（可选）
            queries_used: 实际使用的查询词列表（可选）
        """
        formatted_results = []
        for result in results:
            # 映射文件类型到枚举值
            file_type = self._map_file_type_to_enum(result.get('file_type', ''))

            formatted_result = {
                'file_id': result.get('id', ''),
                'file_name': result.get('file_name', ''),
                'file_path': result.get('file_path', ''),
                'file_type': file_type,
                'relevance_score': result.get('relevance_score', 0),
                'preview_text': result.get('preview_text', ''),
                'highlight': result.get('highlight', ''),
                'created_at': result.get('created_at') if result.get('created_at') else None,
                'modified_at': result.get('modified_time') if result.get('modified_time') else None,
                'file_size': result.get('file_size', 0),
                'match_type': result.get('match_type', 'unknown'),
                # 数据源信息（插件系统）
                'source_type': result.get('source_type'),
                'source_url': result.get('source_url')
            }
            formatted_results.append(formatted_result)

        response_data = {
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

        # 添加术语扩展信息
        if glossary_info:
            response_data['data']['glossary_expansion'] = {
                'matched_terms': [
                    {
                        'id': term.id,
                        'term': term.term,
                        'synonyms': term.synonyms,
                        'collection_id': term.collection_id,
                        'collection_name': term.collection_name
                    }
                    for term in glossary_info.matched_terms
                ],
                'expanded_queries': glossary_info.expanded_queries,
                'used_collections': glossary_info.used_collections,
                'queries_used': queries_used or [query]  # 实际使用的查询词
            }

        return response_data

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
            self.chunk_faiss_index is not None or
            self.chunk_whoosh_index is not None
        )

    def get_index_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        info = {
            'chunk_faiss_available': self.chunk_faiss_index is not None,
            'chunk_whoosh_available': self.chunk_whoosh_index is not None,
            'ai_models_enabled': self.use_ai_models,
            'chunk_search_enabled': self._should_use_chunk_search()
        }

        if self.chunk_faiss_index:
            info['chunk_faiss_doc_count'] = self.chunk_faiss_index.ntotal

        if self.chunk_whoosh_index:
            with self.chunk_whoosh_index.searcher() as searcher:
                info['chunk_whoosh_doc_count'] = searcher.doc_count()

        return info

    async def vector_search(
        self,
        query_vector: Any,
        limit: int = 20,
        threshold: float = 0.7,
        search_type: str = "image_vector"
    ) -> Dict[str, Any]:
        """执行向量搜索（用于图像搜索）

        Args:
            query_vector: 查询向量（图像特征向量）
            limit: 返回结果数量
            threshold: 相似度阈值
            search_type: 搜索类型标识

        Returns:
            Dict[str, Any]: 搜索结果
        """
        start_time = time.time()

        try:
            logger.info(f"开始向量搜索: type={search_type}")

            # 检查索引是否可用
            if self.chunk_faiss_index is None:
                logger.warning("分块Faiss索引未加载，无法进行向量搜索")
                return self._format_error_response("", SearchType.SEMANTIC, "Faiss索引未加载")

            if self.chunk_faiss_index.ntotal == 0:
                logger.warning("分块Faiss索引为空，无法进行向量搜索")
                return self._format_error_response("", SearchType.SEMANTIC, "Faiss索引为空")

            # 准备查询向量
            import numpy as np
            query_vector = np.array(query_vector, dtype=np.float32)
            logger.debug(f"查询向量形状: {query_vector.shape}")

            # 确保查询向量是二维的 (1, d)
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            else:
                query_vector = query_vector

            logger.debug(f"查询向量最终形状: {query_vector.shape}")
            logger.debug(f"Faiss索引维度: {self.chunk_faiss_index.d}")

            # 检查向量维度是否匹配
            if query_vector.shape[1] != self.chunk_faiss_index.d:
                logger.error(f"向量维度不匹���: 查询向量={query_vector.shape[1]}, 索引={self.chunk_faiss_index.d}")
                return self._format_error_response("", SearchType.SEMANTIC, f"向量维度不匹配: {query_vector.shape[1]} != {self.chunk_faiss_index.d}")

            # 执行向量搜索
            k = min(limit * 3, self.chunk_faiss_index.ntotal)  # 搜索3倍的结果用于筛选
            distances, indices = self.chunk_faiss_index.search(query_vector, k)

            # 检查返回值的形状
            if distances is None or indices is None:
                logger.error("Faiss搜索返回空值")
                return self._format_error_response("", SearchType.SEMANTIC, "Faiss搜索返回空值")

            # 处理搜索结果
            results = []
            if len(distances) > 0 and len(indices) > 0:
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx >= 0:  # 有效的索引
                        try:
                            # 获取分块信息
                            chunk_info = self.chunk_id_to_info.get(int(idx), {})
                            if not chunk_info:
                                logger.warning(f"未找到分块信息: {idx}")
                                continue

                            # 计算相似度分数（将距离转换为相似度）
                            similarity = float(1.0 / (1.0 + distance))

                            # 应用阈值过滤
                            if similarity < threshold:
                                continue

                            # 构建结果项
                            result_item = {
                                'file_id': chunk_info.get('file_id', 0),
                                'file_name': chunk_info.get('file_name', ''),
                                'file_path': chunk_info.get('file_path', ''),
                                'file_type': chunk_info.get('file_type', ''),
                                'chunk_id': chunk_info.get('chunk_id', 0),
                                'chunk_index': chunk_info.get('chunk_index', 0),
                                'chunk_text': chunk_info.get('chunk_text', ''),
                                'relevance_score': similarity,
                                'preview_text': chunk_info.get('chunk_text', '')[:200] + '...' if len(chunk_info.get('chunk_text', '')) > 200 else chunk_info.get('chunk_text', ''),
                                'highlight': '',  # 向量搜索没有高亮
                                'created_at': chunk_info.get('created_at', ''),
                                'modified_at': chunk_info.get('modified_at', ''),
                                'file_size': chunk_info.get('file_size', 0),
                                'match_type': search_type,
                                'distance': float(distance)
                            }
                            results.append(result_item)

                            # 限制结果数量
                            if len(results) >= limit:
                                break

                        except Exception as e:
                            logger.warning(f"处理搜索结果时出错 (idx={idx}): {str(e)}")
                            continue

            # 按相似度排序
            results.sort(key=lambda x: x['relevance_score'], reverse=True)

            # 计算响应时间
            response_time = time.time() - start_time

            # 更新统计信息
            self._update_search_stats(response_time, True)

            logger.info(f"向量搜索完成: 找到{len(results)}个结果, 耗时={response_time:.3f}秒")

            # 返回兼容格式的结果
            return self._format_compatible_response(results, "", response_time, SearchType.SEMANTIC)

        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return self._format_error_response("", SearchType.SEMANTIC, str(e))

    def _merge_expansion_search_results(self, all_results: List[List[Dict]]) -> List[Dict]:
        """合并多个查询词的搜索结果

        合并策略：
        1. 按file_id分组
        2. 同一file_id取最高relevance_score
        3. 按聚合后的score排序

        Args:
            all_results: 多个查询词的搜索结果列表

        Returns:
            List[Dict]: 合并去重后的结果
        """
        # 按file_id分组，保留最高分
        file_scores = {}
        file_data = {}

        for results in all_results:
            for item in results:
                file_id = item.get('file_id') or item.get('id')
                score = item.get('relevance_score', 0)

                if file_id and (file_id not in file_scores or score > file_scores[file_id]):
                    file_scores[file_id] = score
                    file_data[file_id] = item

        # 按score排序
        merged = list(file_data.values())
        merged.sort(key=lambda x: x['relevance_score'], reverse=True)

        logger.info(f"术语扩展结果合并: 原始结果数={sum(len(r) for r in all_results)}, 合并后={len(merged)}")
        return merged

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
        chunk_faiss_path = os.getenv('FAISS_INDEX_PATH', '../data/indexes/faiss') + '/document_index_chunks.faiss'
        chunk_whoosh_path = os.getenv('WHOOSH_INDEX_PATH', '../data/indexes/whoosh')

        logger.info(f"初始化分块搜索服务:")
        logger.info(f"  - Faiss索引路径: {chunk_faiss_path}")
        logger.info(f"  - Whoosh索引路径: {chunk_whoosh_path}")

        _chunk_search_service = ChunkSearchService(
            chunk_faiss_index_path=chunk_faiss_path,
            chunk_whoosh_index_path=chunk_whoosh_path,
            use_ai_models=True
        )

    return _chunk_search_service


def configure_glossary_expansion(
    enable: bool = False,
    collection_ids: Optional[List[int]] = None,
    max_expansion_terms: int = 3
):
    """配置术语扩展功能

    Args:
        enable: 是否启用术语扩展
        collection_ids: 使用的术语库ID列表，None表示全部
        max_expansion_terms: 术语扩展最大词数（包含原词）
    """
    global _chunk_search_service
    if _chunk_search_service is not None:
        _chunk_search_service.enable_glossary_expansion = enable
        _chunk_search_service.glossary_collection_ids = collection_ids
        _chunk_search_service.max_expansion_terms = max(1, min(max_expansion_terms, 20))
        logger.info(f"术语扩展配置已更新: enable={enable}, collection_ids={collection_ids}, max_terms={_chunk_search_service.max_expansion_terms}")


def reload_chunk_search_service():
    """重新加载分块搜索服务"""
    global _chunk_search_service
    _chunk_search_service = None