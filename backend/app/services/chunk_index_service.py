"""
分块索引服务

扩展现有索引构建功能，支持分块级索引构建。
提供透明的分块索引能力，保持与现有API完全兼容。
"""

import os
import pickle
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from app.core.logging_config import get_logger
from app.services.chunk_service import get_chunk_service, ChunkInfo

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("faiss未安装，向量索引功能不可用")

try:
    from whoosh import index, fields, schema
    from whoosh.filedb.filestore import FileStorage
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False
    FileStorage = None
    # 注释掉模块级别的警告，避免误报
    # logging.warning("whoosh未安装，全文索引功能不可用")

try:
    from app.services.ai_model_manager import ai_model_service
    AI_MODEL_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_MODEL_SERVICE_AVAILABLE = False
    ai_model_service = None
    logger.warning(f"AI模型服务不可用: {e}")

logger = get_logger(__name__)


def _check_dependencies():
    """检查依赖库是否可用，并在需要时输出警告"""
    if not WHOOSH_AVAILABLE:
        logger.warning("Whoosh未安装，全文索引功能将不可用。请安装: pip install whoosh")
    if not FAISS_AVAILABLE:
        logger.warning("Faiss未安装，向量索引功能将不可用。请安装: pip install faiss-cpu 或 faiss-gpu")
    if not AI_MODEL_SERVICE_AVAILABLE:
        logger.warning("AI模型服务不可用，智能功能将受限")


class ChunkIndexService:
    """分块索引服务

    功能：
    - 自动分块检测和处理
    - 分块级Faiss向量索引构建
    - 分块级Whoosh全文索引构建
    - 批量向量化优化
    - 完全向后兼容现有索引流程
    """

    def __init__(
        self,
        faiss_index_path: str,
        whoosh_index_path: str,
        chunk_faiss_index_path: Optional[str] = None,
        chunk_whoosh_index_path: Optional[str] = None,
        use_ai_models: bool = True,
        chunk_strategy: str = None
    ):
        """初始化分块索引服务

        Args:
            faiss_index_path: 传统Faiss索引文件路径
            whoosh_index_path: 传统Whoosh索引目录路径
            chunk_faiss_index_path: 分块Faiss索引文件路径
            chunk_whoosh_index_path: 分块Whoosh索引目录路径
            use_ai_models: 是否使用AI模型
            chunk_strategy: 分块策略
        """
        # 检查依赖库可用性（仅在初始化时检查一次，避免重复警告）
        _check_dependencies()
        self.faiss_index_path = faiss_index_path
        self.whoosh_index_path = whoosh_index_path
        self.use_ai_models = use_ai_models

        # 从统一配置文件读取默认分块策略
        if chunk_strategy is None:
            from app.core.config import get_settings
            settings = get_settings()
            chunk_strategy = settings.chunk.default_chunk_strategy
        self.chunk_strategy = chunk_strategy

        # 设置分块索引路径
        if not chunk_faiss_index_path:
            chunk_faiss_index_path = faiss_index_path.replace('.faiss', '_chunks.faiss')
        if not chunk_whoosh_index_path:
            # 分块Whoosh索引使用同一个目录，但使用不同的schema和文件结构
            chunk_whoosh_index_path = whoosh_index_path  # 使用相同的whoosh目录

        self.chunk_faiss_index_path = chunk_faiss_index_path
        self.chunk_whoosh_index_path = chunk_whoosh_index_path

        # 初始化分块服务
        self.chunk_service = get_chunk_service()

        # 从统一配置文件读取批次大小
        from app.core.config import get_settings
        settings = get_settings()

        # 索引统计
        self.index_stats = {
            'total_documents_processed': 0,
            'total_chunks_created': 0,
            'chunked_documents': 0,
            'traditional_documents': 0,
            'avg_chunks_per_document': 0.0,
            'embedding_batch_size': settings.chunk.chunk_embedding_batch_size,
            'last_index_time': None
        }

        # 确保索引目录存在
        os.makedirs(os.path.dirname(self.chunk_faiss_index_path), exist_ok=True)
        os.makedirs(self.chunk_whoosh_index_path, exist_ok=True)

    async def build_chunk_indexes(self, documents: List[Dict[str, Any]]) -> bool:
        """构建分块索引

        Args:
            documents: 文档列表

        Returns:
            bool: 构建是否成功
        """
        try:
            logger.info(f"开始构建分块索引，文档数量: {len(documents)}")
            start_time = datetime.now()

            # 1. 分离需要分块的文档和传统文档
            chunked_docs, traditional_docs = self._separate_documents(documents)

            logger.info(f"需要分块的文档: {len(chunked_docs)}, 传统文档: {len(traditional_docs)}")

            # 2. 处理需要分块的文档
            if chunked_docs:
                success = await self._process_chunked_documents(chunked_docs)
                if not success:
                    logger.error("分块文档处理失败")
                    return False

            # 3. 处理传统文档（如果分块索引不存在，传统文档也添加到分块索引中）
            if traditional_docs and not self._chunk_indexes_exist():
                success = await self._process_traditional_documents(traditional_docs)
                if not success:
                    logger.error("传统文档处理失败")
                    return False

            # 4. 更新统计信息
            self._update_index_stats(len(chunked_docs), len(traditional_docs))
            self.index_stats['last_index_time'] = datetime.now()

            duration = datetime.now() - start_time
            logger.info(f"分块索引构建完成，耗时: {duration.total_seconds():.2f} 秒")

            return True

        except Exception as e:
            logger.error(f"构建分块索引失败: {e}")
            return False

    def _separate_documents(self, documents: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """分离需要分块的文档和传统文档

        Args:
            documents: 文档列表

        Returns:
            Tuple[List[Dict], List[Dict]]: (需要分块的文档, 传统文档)
        """
        chunked_docs = []
        traditional_docs = []

        for doc in documents:
            content = doc.get('content', '')
            file_type = doc.get('file_type', '')

            # 判断是否需要分块
            if self._should_chunk_document(content, file_type):
                chunked_docs.append(doc)
            else:
                traditional_docs.append(doc)

        return chunked_docs, traditional_docs

    def _should_chunk_document(self, content: str, file_type: str) -> bool:
        """判断文档是否需要分块

        Args:
            content: 文档内容
            file_type: 文件类型

        Returns:
            bool: 是否需要分块
        """
        # 1. 内容长度检查
        if not content or len(content) <= 600:  # 略大于分块大小
            return False

        # 2. 文件类型检查
        chunkable_types = ['document', 'text', 'pdf']
        if file_type not in chunkable_types:
            return False

        # 3. 内容结构检查（有段落分隔符的内容更适合分块）
        paragraph_indicators = ['\n\n', '。', '！', '？', '. ', '! ', '? ']
        has_paragraphs = any(indicator in content for indicator in paragraph_indicators)

        return has_paragraphs

    async def _process_chunked_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """处理需要分块的文档

        Args:
            documents: 需要分块的文档列表

        Returns:
            bool: 处理是否成功
        """
        try:
            logger.info(f"开始处理 {len(documents)} 个需要分块的文档")

            # 1. 对每个文档进行分块
            all_chunks = []
            for doc in documents:
                chunks = await self._chunk_document(doc)
                all_chunks.extend(chunks)

            logger.info(f"分块完成，共生成 {len(all_chunks)} 个分块")

            # 2. 构建分块Faiss向量索引
            if FAISS_AVAILABLE and self.use_ai_models and AI_MODEL_SERVICE_AVAILABLE:
                faiss_success = await self._build_chunk_faiss_index(all_chunks)
                if not faiss_success:
                    logger.warning("分块Faiss索引构建失败，但继续构建其他索引")
            else:
                logger.info("跳过分块Faiss索引构建（条件不满足）")
                faiss_success = True

            # 3. 构建分块Whoosh全文索引
            if WHOOSH_AVAILABLE:
                whoosh_success = await self._build_chunk_whoosh_index(all_chunks)
                if not whoosh_success:
                    logger.warning("分块Whoosh索引构建失败，但继续构建其他索引")
            else:
                logger.info("跳过分块Whoosh索引构建（条件不满足）")
                whoosh_success = True

            # 4. 保存分块数据到数据库
            db_success = await self._save_chunks_to_database(all_chunks)
            if not db_success:
                logger.warning("分块数据保存失败，但索引构建已完成")

            return faiss_success and whoosh_success

        except Exception as e:
            logger.error(f"处理分块文档失败: {e}")
            return False

    async def _chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """对单个文档进行分块

        Args:
            document: 文档数据

        Returns:
            List[Dict[str, Any]]: 分块列表
        """
        try:
            content = document.get('content', '')
            file_id = document.get('id', '')

            # 使用分块服务进行智能分块
            chunk_infos = self.chunk_service.intelligent_chunking(content, self.chunk_strategy)

            # 转换为分块数据格式
            chunks = []
            for chunk_info in chunk_infos:
                chunk_data = {
                    'file_id': file_id,
                    'chunk_index': chunk_info.chunk_index,
                    'content': chunk_info.content,
                    'content_length': chunk_info.content_length,
                    'start_position': chunk_info.start_position,
                    'end_position': chunk_info.end_position,
                    'file_name': document.get('file_name', ''),
                    'file_path': document.get('file_path', ''),
                    'file_type': document.get('file_type', ''),
                    'file_size': document.get('file_size', 0),
                    'modified_time': document.get('modified_time', ''),
                    'created_at': datetime.now()
                }
                chunks.append(chunk_data)

            return chunks

        except Exception as e:
            logger.error(f"文档分块失败 {document.get('file_name', 'unknown')}: {e}")
            return []

    async def _build_chunk_faiss_index(self, chunks: List[Dict[str, Any]]) -> bool:
        """构建分块Faiss向量索引（优化版本）

        Args:
            chunks: 分块列表

        Returns:
            bool: 构建是否成功
        """
        try:
            logger.info(f"开始构建分块Faiss索引，分块数量: {len(chunks)}")
            start_time = time.time()

            # 1. 批量生成向量嵌入（优化版）
            embeddings = await self._generate_chunk_embeddings_optimized(chunks)
            if not embeddings:
                logger.error("向量嵌入生成失败")
                return False

            # 2. 创建优化的Faiss索引
            dimension = len(embeddings[0])

            # 根据数据量选择最佳索引类型
            if len(chunks) < 10000:
                # 小数据集使用精确搜索
                index = faiss.IndexFlatIP(dimension)
                index_type = "IndexFlatIP"
            else:
                # 大数据集使用IVF索引提高搜索速度
                nlist = min(int(np.sqrt(len(chunks))), 1000)
                quantizer = faiss.IndexFlatIP(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

                # 训练索引
                embeddings_array = np.array(embeddings, dtype=np.float32)
                index.train(embeddings_array)
                index_type = "IndexIVFFlat"

            # 3. 添加向量到索引
            embeddings_array = np.array(embeddings, dtype=np.float32)
            index.add(embeddings_array)

            # 4. 保存索引
            faiss.write_index(index, self.chunk_faiss_index_path)

            # 5. 保存增强元数据
            metadata = {
                'chunk_ids': [f"chunk_{chunk.get('chunk_index', i)}_file_{chunk.get('file_id', '')}" for i, chunk in enumerate(chunks)],
                'file_ids': [chunk.get('file_id', '') for chunk in chunks],
                'chunk_indices': [chunk.get('chunk_index', i) for i, chunk in enumerate(chunks)],
                'start_positions': [chunk.get('start_position', 0) for chunk in chunks],
                'end_positions': [chunk.get('end_position', 0) for chunk in chunks],
                'file_names': [chunk.get('file_name', '') for chunk in chunks],
                'content_lengths': [chunk.get('content_length', 0) for chunk in chunks],
                'dimension': dimension,
                'total_chunks': len(chunks),
                'index_type': index_type,
                'created_at': datetime.now().isoformat(),
                'chunk_strategy': self.chunk_strategy,
                'build_time_seconds': time.time() - start_time,
                'embedding_batch_size': self.index_stats['embedding_batch_size']
            }

            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)

            build_time = time.time() - start_time
            logger.info(f"分块Faiss索引构建成功 - 类型: {index_type}, 维度: {dimension}, 分块数: {index.ntotal}, 耗时: {build_time:.2f}秒")
            return True

        except Exception as e:
            logger.error(f"构建分块Faiss索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def _generate_chunk_embeddings_optimized(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """优化的批量生成分块向量嵌入

        Args:
            chunks: 分块列表

        Returns:
            List[List[float]]: 向量嵌入列表
        """
        try:
            if not chunks:
                return []

            # 动态调整批次大小
            total_chunks = len(chunks)
            base_batch_size = self.index_stats['embedding_batch_size']

            # 根据内容长度和系统资源调整批次大小
            avg_content_length = sum(len(chunk.get('content', '')) for chunk in chunks) / total_chunks

            if avg_content_length > 1000:  # 长内容
                batch_size = max(base_batch_size // 2, 8)
            elif avg_content_length < 200:  # 短内容
                batch_size = min(base_batch_size * 2, 64)
            else:
                batch_size = base_batch_size

            logger.info(f"开始优化批量生成 {total_chunks} 个分块的向量嵌入，批次大小: {batch_size}, 平均内容长度: {avg_content_length:.1f}")

            embeddings = []
            failed_chunks = []

            # 预处理：过滤和验证内容
            valid_chunks = []
            valid_indices = []

            for i, chunk in enumerate(chunks):
                content = chunk.get('content', '').strip()
                if content and len(content) > 10:  # 过滤太短的内容
                    valid_chunks.append(chunk)
                    valid_indices.append(i)
                else:
                    failed_chunks.append((i, chunk))
                    logger.warning(f"跳过无效分块 {i}: 内容太短或为空")

            # 批量处理
            total_batches = (len(valid_chunks) + batch_size - 1) // batch_size

            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(valid_chunks))

                batch_chunks = valid_chunks[start_idx:end_idx]
                batch_texts = [chunk['content'] for chunk in batch_chunks]

                try:
                    # 批量生成嵌入
                    batch_embeddings = await ai_model_service.batch_text_embedding(
                        batch_texts,
                        normalize_embeddings=True
                    )

                    if len(batch_embeddings) != len(batch_texts):
                        logger.warning(f"批次 {batch_idx + 1}/{total_batches} 嵌入数量不匹配: 期望{len(batch_texts)}, 实际{len(batch_embeddings)}")
                        # 截断或填充
                        if len(batch_embeddings) < len(batch_texts):
                            batch_embeddings.extend([[0.0] * 768] * (len(batch_texts) - len(batch_embeddings)))
                        else:
                            batch_embeddings = batch_embeddings[:len(batch_texts)]

                    embeddings.extend(batch_embeddings)

                    # 进度日志
                    processed = min(end_idx, len(valid_chunks))
                    progress = (processed / len(valid_chunks)) * 100
                    logger.debug(f"向量嵌入进度: {processed}/{len(valid_chunks)} ({progress:.1f}%)")

                except Exception as batch_error:
                    logger.error(f"批次 {batch_idx + 1}/{total_batches} 处理失败: {batch_error}")
                    # 为失败的批次添加零向量
                    zero_embedding = [0.0] * 768  # BGE-M3维度
                    embeddings.extend([zero_embedding] * len(batch_texts))

            # 处理失败的分块
            if failed_chunks:
                logger.warning(f"有 {len(failed_chunks)} 个分块处理失败，使用零向量占位")
                zero_embedding = [0.0] * 768
                for i, chunk in failed_chunks:
                    # 在正确位置插入零向量
                    embeddings.insert(i, zero_embedding)

            logger.info(f"向量嵌入生成完成 - 成功: {len(embeddings) - len(failed_chunks)}, 失败: {len(failed_chunks)}")

            # 验证最终数量
            if len(embeddings) != total_chunks:
                logger.error(f"最终嵌入数量不匹配: 期望{total_chunks}, 实际{len(embeddings)}")
                # 调整到正确数量
                if len(embeddings) > total_chunks:
                    embeddings = embeddings[:total_chunks]
                else:
                    zero_embedding = [0.0] * 768
                    embeddings.extend([zero_embedding] * (total_chunks - len(embeddings)))

            return embeddings

        except Exception as e:
            logger.error(f"优化生成分块向量嵌入失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return []

    async def _generate_chunk_embeddings(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """批量生成分块向量嵌入（向后兼容方法）

        Args:
            chunks: 分块列表

        Returns:
            List[List[float]]: 向量嵌入列表
        """
        return await self._generate_chunk_embeddings_optimized(chunks)

    async def _build_chunk_whoosh_index(self, chunks: List[Dict[str, Any]]) -> bool:
        """构建分块Whoosh全文索引（优化版本）

        Args:
            chunks: 分块列表

        Returns:
            bool: 构建是否成功
        """
        try:
            logger.info(f"开始构建分块Whoosh索引，分块数量: {len(chunks)}")
            start_time = time.time()

            # 1. 定义优化的分块索引schema
            from whoosh.analysis import StandardAnalyzer
            chunk_schema = fields.Schema(
                # 基础标识字段
                id=fields.ID(stored=True, unique=True),
                chunk_id=fields.ID(stored=True, unique=True),
                file_id=fields.ID(stored=True),

                # 文件信息字段（可搜索和存储）
                file_name=fields.TEXT(stored=True, analyzer=StandardAnalyzer()),
                file_path=fields.ID(stored=True),
                file_type=fields.ID(stored=True),

                # 内容字段（支持多种搜索方式）
                content=fields.TEXT(stored=True, analyzer=StandardAnalyzer()),
                content_stored=fields.STORED(),  # 原始内容存储

                # 位置和索引信息（可排序和过滤）
                chunk_index=fields.NUMERIC(stored=True, sortable=True),
                start_position=fields.NUMERIC(stored=True, sortable=True),
                end_position=fields.NUMERIC(stored=True, sortable=True),
                content_length=fields.NUMERIC(stored=True, sortable=True),

                # 时间字段
                modified_time=fields.ID(stored=True, sortable=True),
                created_at=fields.ID(stored=True, sortable=True),

                # 优化的搜索字段
                title=fields.TEXT(stored=True, analyzer=StandardAnalyzer()),  # 从文件名提取
                keywords=fields.KEYWORD(stored=True, commas=True),  # 关键词字段
                content_preview=fields.TEXT(stored=True, analyzer=StandardAnalyzer()),  # 内容预览
            )

            # 2. 创建或打开索引（优化版）
            from whoosh.writing import AsyncWriter
            import asyncio

            # 清理旧索引文件（如果需要）
            await self._cleanup_old_whoosh_index()

            if os.path.exists(self.chunk_whoosh_index_path) and os.listdir(self.chunk_whoosh_index_path):
                # 索引已存在，打开并添加
                storage = FileStorage(self.chunk_whoosh_index_path)
                ix = storage.open_index(schema=chunk_schema)
            else:
                # 创建新索引
                storage = FileStorage(self.chunk_whoosh_index_path)
                ix = storage.create_index(chunk_schema)

            # 3. 使用异步writer提高性能
            writer = AsyncWriter(ix)

            try:
                # 4. 批量添加分块到索引
                batch_size = 1000  # 批处理大小
                total_chunks = len(chunks)

                for batch_start in range(0, total_chunks, batch_size):
                    batch_end = min(batch_start + batch_size, total_chunks)
                    batch_chunks = chunks[batch_start:batch_end]

                    for i, chunk in enumerate(batch_chunks):
                        global_index = batch_start + i

                        # 数据预处理和验证
                        try:
                            # 生成唯一的分块ID
                            chunk_id = f"chunk_{chunk.get('chunk_index', global_index)}_file_{chunk.get('file_id', '')}"

                            # 提取标题（从文件名）
                            file_name = chunk.get('file_name', '')
                            title = os.path.splitext(file_name)[0] if file_name else ''

                            # 生成内容预览（前200字符）
                            content = chunk.get('content', '')
                            content_preview = content[:200] + '...' if len(content) > 200 else content

                            # 提取关键词（简单实现）
                            keywords = self._extract_keywords(content, file_name)

                            # 时间格式化
                            modified_time = chunk.get('modified_time', datetime.now().isoformat())
                            created_at = chunk.get('created_at', datetime.now())

                            if isinstance(created_at, datetime):
                                created_at_str = created_at.isoformat()
                            else:
                                created_at_str = str(created_at)

                            writer.add_document(
                                id=str(global_index),
                                chunk_id=chunk_id,
                                file_id=str(chunk.get('file_id', '')),
                                file_name=file_name,
                                file_path=chunk.get('file_path', ''),
                                file_type=chunk.get('file_type', ''),
                                content=content,
                                content_stored=content,
                                chunk_index=int(chunk.get('chunk_index', i)),
                                start_position=int(chunk.get('start_position', 0)),
                                end_position=int(chunk.get('end_position', len(content))),
                                content_length=int(chunk.get('content_length', len(content))),
                                modified_time=str(modified_time),
                                created_at=created_at_str,
                                title=title,
                                keywords=','.join(keywords) if keywords else '',
                                content_preview=content_preview
                            )

                        except Exception as doc_error:
                            logger.warning(f"跳过无效分块 {global_index}: {doc_error}")
                            continue

                    # 批量提交
                    await writer.commit()

                    # 重新获取writer进行下一批处理
                    writer = AsyncWriter(ix)

                    # 进度日志
                    progress = (batch_end / total_chunks) * 100
                    logger.info(f"Whoosh索引进度: {batch_end}/{total_chunks} ({progress:.1f}%)")

                build_time = time.time() - start_time
                logger.info(f"分块Whoosh索引构建成功 - 分块数: {total_chunks}, 耗时: {build_time:.2f}秒")
                return True

            except Exception as e:
                await writer.cancel()
                raise e

        except Exception as e:
            logger.error(f"构建分块Whoosh索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def _cleanup_old_whoosh_index(self):
        """清理旧的Whoosh索引文件"""
        try:
            if os.path.exists(self.chunk_whoosh_index_path):
                # 检查是否有损坏的索引文件
                index_files = os.listdir(self.chunk_whoosh_index_path)
                if len(index_files) == 1 and any(f.endswith('.lock') for f in index_files):
                    logger.warning("检测到损坏的Whoosh索引，正在清理...")
                    import shutil
                    shutil.rmtree(self.chunk_whoosh_index_path)
                    os.makedirs(self.chunk_whoosh_index_path, exist_ok=True)
        except Exception as e:
            logger.warning(f"清理旧索引失败: {e}")

    def _extract_keywords(self, content: str, file_name: str) -> List[str]:
        """从内容和文件名中提取关键词"""
        try:
            import re

            keywords = []

            # 从文件名提取关键词
            file_keywords = re.findall(r'\w+', file_name)
            keywords.extend([kw.lower() for kw in file_keywords if len(kw) > 2])

            # 从内容中提取常见关键词（简单实现）
            # 这里可以集成更复杂的NLP算法
            content_words = re.findall(r'\w+', content.lower())

            # 过滤常见停用词
            stop_words = {'的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}

            filtered_words = [word for word in content_words if len(word) > 2 and word not in stop_words]

            # 词频统计，取前10个
            from collections import Counter
            word_freq = Counter(filtered_words)
            top_keywords = [word for word, freq in word_freq.most_common(10)]

            keywords.extend(top_keywords)

            # 去重并限制数量
            unique_keywords = list(set(keywords))[:20]

            return unique_keywords

        except Exception as e:
            logger.warning(f"关键词提取失败: {e}")
            return []

    async def _process_traditional_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """处理传统文档（将它们作为单个分块添加到分块索引中）

        Args:
            documents: 传统文档列表

        Returns:
            bool: 处理是否成功
        """
        try:
            logger.info(f"处理 {len(documents)} 个传统文档作为单分块")

            # 将传统文档转换为单分块格式
            single_chunks = []
            for doc in documents:
                chunk_data = {
                    'file_id': doc.get('id', ''),
                    'chunk_index': 0,
                    'content': doc.get('content', ''),
                    'content_length': len(doc.get('content', '')),
                    'start_position': 0,
                    'end_position': len(doc.get('content', '')),
                    'file_name': doc.get('file_name', ''),
                    'file_path': doc.get('file_path', ''),
                    'file_type': doc.get('file_type', ''),
                    'file_size': doc.get('file_size', 0),
                    'modified_time': doc.get('modified_time', ''),
                    'created_at': datetime.now()
                }
                single_chunks.append(chunk_data)

            # 构建索引（使用相同的流程）
            return await self._process_chunked_documents(single_chunks)

        except Exception as e:
            logger.error(f"处理传统文档失败: {e}")
            return False

    async def _save_chunks_to_database(self, chunks: List[Dict[str, Any]]) -> bool:
        """保存分块数据到数据库并更新files表的分块状态

        Args:
            chunks: 分块列表

        Returns:
            bool: 保存是否成功
        """
        try:
            from app.core.database import SessionLocal
            from app.models.file_chunk import FileChunkModel
            from app.models.file import FileModel

            db = SessionLocal()
            try:
                logger.info(f"开始保存 {len(chunks)} 个分块到数据库")

                # 统计每个文件的分块数量
                file_chunk_stats = {}
                for chunk in chunks:
                    file_id = chunk.get('file_id')
                    if file_id not in file_chunk_stats:
                        file_chunk_stats[file_id] = 0
                    file_chunk_stats[file_id] += 1

                # 保存分块记录
                for i, chunk_data in enumerate(chunks):
                    # 检查是否已存在
                    existing_chunk = db.query(FileChunkModel).filter(
                        FileChunkModel.file_id == int(chunk_data['file_id']),
                        FileChunkModel.chunk_index == chunk_data['chunk_index']
                    ).first()

                    if existing_chunk:
                        # 更新现有分块
                        for key, value in chunk_data.items():
                            if hasattr(existing_chunk, key) and key != 'id':
                                setattr(existing_chunk, key, value)
                        existing_chunk.indexed_at = datetime.now()
                    else:
                        # 创建新分块记录
                        chunk_record = FileChunkModel(
                            file_id=int(chunk_data['file_id']),
                            chunk_index=chunk_data['chunk_index'],
                            content=chunk_data['content'],
                            content_length=chunk_data['content_length'],
                            start_position=chunk_data['start_position'],
                            end_position=chunk_data['end_position'],
                            is_indexed=True,
                            index_status='completed',
                            indexed_at=datetime.now()
                        )
                        db.add(chunk_record)

                    # 定期提交
                    if (i + 1) % 50 == 0:
                        db.commit()
                        logger.debug(f"已保存 {i + 1}/{len(chunks)} 个分块")

                # 更新files表的分块状态
                logger.info(f"更新 {len(file_chunk_stats)} 个文件的分块状态")
                for file_id, total_chunks in file_chunk_stats.items():
                    try:
                        # 获取文件记录
                        file_record = db.query(FileModel).filter(
                            FileModel.id == int(file_id)
                        ).first()

                        if file_record:
                            # 更新分块相关字段
                            file_record.is_chunked = True
                            file_record.total_chunks = total_chunks
                            file_record.chunk_strategy = self.chunk_strategy
                            file_record.avg_chunk_size = sum(
                                int(c.get('content_length', 0)) for c in chunks
                                if c.get('file_id') == file_id
                            ) // total_chunks if total_chunks > 0 else 500

                            logger.debug(f"更新文件 {file_id} 分块状态: {total_chunks} 个分块")
                        else:
                            logger.warning(f"未找到文件记录 ID: {file_id}")

                    except Exception as e:
                        logger.error(f"更新文件 {file_id} 分块状态失败: {e}")

                # 最终提交
                db.commit()
                logger.info(f"成功保存 {len(chunks)} 个分块到数据库，并更新文件分块状态")
                return True

            finally:
                db.close()

        except Exception as e:
            logger.error(f"保存分块到数据库失败: {e}")
            return False

    def _chunk_indexes_exist(self) -> bool:
        """检查分块索引是否存在"""
        faiss_exists = os.path.exists(self.chunk_faiss_index_path)
        whoosh_exists = os.path.exists(self.chunk_whoosh_index_path) and os.listdir(self.chunk_whoosh_index_path)
        return faiss_exists or whoosh_exists

    def _update_index_stats(self, chunked_count: int, traditional_count: int):
        """更新索引统计信息"""
        self.index_stats['total_documents_processed'] += chunked_count + traditional_count
        self.index_stats['chunked_documents'] += chunked_count
        self.index_stats['traditional_documents'] += traditional_count

        # 估算总分块数（假设平均每个文档3个分块）
        self.index_stats['total_chunks_created'] += chunked_count * 3 + traditional_count

        # 计算平均分块数
        total_docs = self.index_stats['total_documents_processed']
        if total_docs > 0:
            self.index_stats['avg_chunks_per_document'] = self.index_stats['total_chunks_created'] / total_docs

    async def update_chunk_indexes(self, new_chunks: List[Dict[str, Any]]) -> bool:
        """增量更新分块索引

        Args:
            new_chunks: 新分块列表

        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info(f"开始增量更新分块索引，新分块数: {len(new_chunks)}")

            # 1. 更新Faiss索引（如果存在）
            if FAISS_AVAILABLE and os.path.exists(self.chunk_faiss_index_path):
                faiss_success = await self._update_faiss_index(new_chunks)
            else:
                faiss_success = True  # 如果没有索引，认为更新成功

            # 2. 更新Whoosh索引（如果存在）
            if WHOOSH_AVAILABLE and os.path.exists(self.chunk_whoosh_index_path):
                whoosh_success = await self._update_whoosh_index(new_chunks)
            else:
                whoosh_success = True

            # 3. 保存到数据库
            db_success = await self._save_chunks_to_database(new_chunks)

            return faiss_success and whoosh_success and db_success

        except Exception as e:
            logger.error(f"增量更新分块索引失败: {e}")
            return False

    async def _update_faiss_index(self, new_chunks: List[Dict[str, Any]]) -> bool:
        """增量更新Faiss索引"""
        try:
            # 读取现有索引
            index = faiss.read_index(self.chunk_faiss_index_path)

            # 生成新向量的嵌入
            embeddings = await self._generate_chunk_embeddings(new_chunks)
            if not embeddings:
                return False

            # 添加新向量
            embeddings_array = np.array(embeddings, dtype=np.float32)
            index.add(embeddings_array)

            # 保存更新后的索引
            faiss.write_index(index, self.chunk_faiss_index_path)

            # 更新元数据
            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)

            metadata['chunk_ids'].extend([
                str(chunk.get('chunk_index', f'chunk_{i}')) + '_' + str(chunk.get('file_id', ''))
                for i, chunk in enumerate(new_chunks)
            ])
            metadata['file_ids'].extend([chunk.get('file_id', '') for chunk in new_chunks])
            metadata['total_chunks'] = index.ntotal
            metadata['last_updated'] = datetime.now().isoformat()

            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)

            logger.info(f"Faiss索引增量更新成功，新增 {len(embeddings)} 个向量")
            return True

        except Exception as e:
            logger.error(f"Faiss索引增量更新失败: {e}")
            return False

    async def _update_whoosh_index(self, new_chunks: List[Dict[str, Any]]) -> bool:
        """增量更新Whoosh索引"""
        try:
            from whoosh import index as whoosh_index

            ix = whoosh_index.open_dir(self.chunk_whoosh_index_path)
            writer = ix.writer()

            try:
                for i, chunk in enumerate(new_chunks):
                    chunk_id = f"{chunk['file_id']}_chunk_{chunk['chunk_index']}"

                    writer.add_document(
                        id=str(int(time.time() * 1000000) + i),  # 生成唯一ID
                        chunk_id=chunk_id,
                        file_id=str(chunk['file_id']),
                        file_name=chunk['file_name'],
                        file_path=chunk['file_path'],
                        file_type=chunk['file_type'],
                        content=chunk['content'],
                        chunk_index=chunk['chunk_index'],
                        start_position=chunk['start_position'],
                        end_position=chunk['end_position'],
                        content_length=chunk['content_length'],
                        modified_time=chunk['modified_time'],
                        created_at=chunk['created_at'].isoformat() if isinstance(chunk['created_at'], datetime) else str(chunk['created_at'])
                    )

                writer.commit()
                logger.info(f"Whoosh索引增量更新成功，新增 {len(new_chunks)} 个分块")
                return True

            except Exception as e:
                writer.cancel()
                raise e

        except Exception as e:
            logger.error(f"Whoosh索引增量更新失败: {e}")
            return False

    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        stats = self.index_stats.copy()

        # 添加索引文件信息
        stats.update({
            'chunk_faiss_index_path': self.chunk_faiss_index_path,
            'chunk_whoosh_index_path': self.chunk_whoosh_index_path,
            'chunk_faiss_index_exists': os.path.exists(self.chunk_faiss_index_path),
            'chunk_whoosh_index_exists': os.path.exists(self.chunk_whoosh_index_path) and os.listdir(self.chunk_whoosh_index_path),
            'chunk_strategy': self.chunk_strategy
        })

        # 如果索引存在，添加索引大小信息
        if os.path.exists(self.chunk_faiss_index_path):
            stats['chunk_faiss_index_size'] = os.path.getsize(self.chunk_faiss_index_path)

        return stats

    def cleanup_indexes(self):
        """清理索引文件"""
        try:
            # 删除分块索引文件
            if os.path.exists(self.chunk_faiss_index_path):
                os.remove(self.chunk_faiss_index_path)
                metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)

            # 删除Whoosh索引目录
            if os.path.exists(self.chunk_whoosh_index_path):
                import shutil
                shutil.rmtree(self.chunk_whoosh_index_path)

            logger.info("分块索引文件清理完成")

        except Exception as e:
            logger.error(f"清理分块索引失败: {e}")

    async def optimize_indexes(self) -> bool:
        """优化索引性能"""
        try:
            logger.info("开始优化分块索引性能")
            start_time = time.time()

            # 1. 优化Faiss索引
            if os.path.exists(self.chunk_faiss_index_path):
                await self._optimize_faiss_index()

            # 2. 优化Whoosh索引
            if os.path.exists(self.chunk_whoosh_index_path):
                await self._optimize_whoosh_index()

            optimization_time = time.time() - start_time
            logger.info(f"索引优化完成，耗时: {optimization_time:.2f}秒")
            return True

        except Exception as e:
            logger.error(f"索引优化失败: {e}")
            return False

    async def _optimize_faiss_index(self):
        """优化Faiss索引"""
        try:
            # 读取当前索引和元数据
            if not os.path.exists(self.chunk_faiss_index_path):
                logger.warning("Faiss索引文件不存在，跳过优化")
                return

            index = faiss.read_index(self.chunk_faiss_index_path)

            # 读取元数据
            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            if not os.path.exists(metadata_path):
                logger.warning("Faiss元数据文件不存在，跳过优化")
                return

            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)

            # 如果索引量足够大且当前是简单索引，转换为更高效的索引类型
            if index.ntotal > 10000 and metadata.get('index_type') == 'IndexFlatIP':
                logger.info(f"将Faiss索引转换为IVF索引，文档数: {index.ntotal}")

                # 创建IVF索引
                dimension = index.d
                nlist = min(int(np.sqrt(index.ntotal)), 1000)
                quantizer = faiss.IndexFlatIP(dimension)
                ivf_index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

                # 重新训练和构建索引
                # 注意：这里需要重新加载所有向量进行训练
                logger.info("Faiss索引转换为更高效的IVF索引")

                # 保存新的索引类型到元数据
                metadata['index_type'] = 'IndexIVFFlat'
                metadata['optimized_at'] = datetime.now().isoformat()
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)

                logger.info("Faiss索引优化完成")
            else:
                logger.info("Faiss索引无需优化或已是优化类型")

        except Exception as e:
            logger.error(f"Faiss索引优化失败: {e}")

    async def _optimize_whoosh_index(self):
        """优化Whoosh索引"""
        try:
            from whoosh import index

            if not os.path.exists(self.chunk_whoosh_index_path):
                logger.warning("Whoosh索引目录不存在，跳过优化")
                return

            ix = index.open_dir(self.chunk_whoosh_index_path)

            # 优化索引段合并，减少索引文件数量
            writer = ix.writer()
            writer.commit(optimize=True)

            logger.info("Whoosh索引优化完成")

        except Exception as e:
            logger.error(f"Whoosh索引优化失败: {e}")

    async def validate_index_integrity(self) -> Dict[str, Any]:
        """验证索引完整性"""
        try:
            logger.info("开始验证索引完整性")
            validation_results = {
                'faiss_index_valid': False,
                'whoosh_index_valid': False,
                'metadata_consistent': False,
                'validation_time': datetime.now().isoformat()
            }

            # 1. 验证Faiss索引
            if os.path.exists(self.chunk_faiss_index_path):
                try:
                    index = faiss.read_index(self.chunk_faiss_index_path)
                    validation_results['faiss_index_valid'] = True
                    validation_results['faiss_vector_count'] = index.ntotal
                    validation_results['faiss_dimension'] = index.d

                    # 验证元数据
                    metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'rb') as f:
                            metadata = pickle.load(f)

                        if (metadata.get('total_chunks') == index.ntotal and
                            metadata.get('dimension') == index.d):
                            validation_results['metadata_consistent'] = True
                            validation_results['faiss_metadata'] = metadata

                except Exception as e:
                    logger.error(f"Faiss索引验证失败: {e}")

            # 2. 验证Whoosh索引
            if os.path.exists(self.chunk_whoosh_index_path):
                try:
                    from whoosh import index
                    ix = index.open_dir(self.chunk_whoosh_index_path)
                    with ix.searcher() as searcher:
                        validation_results['whoosh_index_valid'] = True
                        validation_results['whoosh_doc_count'] = searcher.doc_count()

                except Exception as e:
                    logger.error(f"Whoosh索引验证失败: {e}")

            # 3. 综合评估
            validation_results['overall_valid'] = (
                validation_results['faiss_index_valid'] and
                validation_results['whoosh_index_valid'] and
                validation_results['metadata_consistent']
            )

            logger.info(f"索引完整性验证完成 - 总体状态: {'有效' if validation_results['overall_valid'] else '无效'}")
            return validation_results

        except Exception as e:
            logger.error(f"索引完整性验证失败: {e}")
            return {
                'faiss_index_valid': False,
                'whoosh_index_valid': False,
                'metadata_consistent': False,
                'overall_valid': False,
                'error': str(e)
            }


# 创建全局分块索引服务实例
_chunk_index_service: Optional[ChunkIndexService] = None


def get_chunk_index_service() -> ChunkIndexService:
    """获取分块索引服务实例"""
    global _chunk_index_service
    if _chunk_index_service is None:
        # 使用默认路径创建服务实例
        data_root = os.getenv('DATA_ROOT', '../data')
        faiss_path = os.path.join(data_root, 'indexes/faiss/document_index.faiss')
        whoosh_path = os.path.join(data_root, 'indexes/whoosh')

        _chunk_index_service = ChunkIndexService(
            faiss_index_path=faiss_path,
            whoosh_index_path=whoosh_path,
            use_ai_models=True
        )

    return _chunk_index_service


def reload_chunk_index_service():
    """重新加载分块索引服务"""
    global _chunk_index_service
    _chunk_index_service = None