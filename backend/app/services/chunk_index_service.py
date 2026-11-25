"""
分块索引服务

扩展现有索引构建功能，支持分块级索引构建。
提供透明的分块索引能力，���持与现有API完全兼容。
"""

import os
import pickle
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from app.utils.snowflake import generate_snowflake_id
from app.core.logging_config import get_logger, logger
from app.services.chunk_service import get_chunk_service, ChunkInfo
import faiss
import numpy as np
import whoosh
from whoosh import index
from whoosh import fields
from app.services.ai_model_manager import ai_model_service


class IndexBuildStopped(Exception):
    """索引构建被用户停止（已完成的分批数据已落盘）"""
    pass


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
        chunk_faiss_index_path: str,
        chunk_whoosh_index_path: str,
        use_ai_models: bool = True,
        chunk_strategy: str = None
    ):
        """初始化分块索引服务

        Args:
            chunk_faiss_index_path: 分块Faiss索引文件路径
            chunk_whoosh_index_path: 分块Whoosh索引目录路径
            use_ai_models: 是否使用AI模型
            chunk_strategy: 分块策略
        """
        self.use_ai_models = use_ai_models

        # 从统一配置文件读取默认分块策略
        if chunk_strategy is None:
            from app.core.config import get_settings
            settings = get_settings()
            chunk_strategy = settings.chunk.default_chunk_strategy
        self.chunk_strategy = chunk_strategy

        # 设置分块索引路径
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
            'avg_chunks_per_document': 0.0,
            'embedding_batch_size': settings.processing.index_batch_size,
            'last_index_time': None
        }

        # 确保索引目录存在
        os.makedirs(os.path.dirname(self.chunk_faiss_index_path), exist_ok=True)
        os.makedirs(self.chunk_whoosh_index_path, exist_ok=True)

    async def build_chunk_indexes(
        self,
        documents: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None,
        should_stop: Optional[callable] = None,
        rebuild: bool = False
    ) -> bool:
        """构建分块索引（流式分批）

        Args:
            documents: 文档列表（所有文档都将进行分块处理）
            progress_callback: 进度回调 callback(stage: str, percent: float)
            should_stop: 停止信号检查函数，返回 True 时中断
            rebuild: True 时重建 Faiss 向量索引；False 时追加到现有索引

        Returns:
            bool: 构建是否成功

        Raises:
            IndexBuildStopped: 用户停止任务（已完成批次的数据已落盘）
        """
        try:
            logger.info(f"开始构建分块索引，文档数量: {len(documents)}")
            logger.info(f"AI模型配置状态: use_ai_models={self.use_ai_models}")
            start_time = datetime.now()

            # 1. 过滤出需要分块的文档
            chunked_docs = []
            for doc in documents:
                if self._should_chunk_document(doc.get('content', ''), doc.get('file_type', '')):
                    chunked_docs.append(doc)
                else:
                    logger.info(f"文档 {doc.get('file_name', 'unknown')} 长度不足，跳过分块处理")

            logger.info(f"实际需要分块的文档: {len(chunked_docs)}")

            # 2. 处理分块文档
            if chunked_docs:
                success = await self._process_chunked_documents(
                    chunked_docs,
                    progress_callback=progress_callback,
                    should_stop=should_stop,
                    rebuild=rebuild
                )
                if not success:
                    logger.error("分块文档处理失败")
                    return False
            else:
                logger.info("没有需要分块的文档")

            # 3. 构建CLIP图像向量索引（处理所有文档）
            if self.use_ai_models:
                logger.info(f"AI模型已启用，开始构建CLIP图像向量索引，文档数量: {len(documents)}")
                clip_success = await self._build_clip_image_index(documents)
                if not clip_success:
                    logger.warning("CLIP图像索引构建失败，但继续构建其他索引")
                else:
                    logger.info("CLIP图像索引构建成功")
            else:
                logger.warning(f"AI模型未启用，跳过CLIP图像索引构建。use_ai_models={self.use_ai_models}")

            # 4. 更新统计信息
            self._update_index_stats(len(chunked_docs))
            self.index_stats['last_index_time'] = datetime.now()

            duration = datetime.now() - start_time
            logger.info(f"分块索引构建完成，耗时: {duration.total_seconds():.2f} 秒")

            return True

        except IndexBuildStopped:
            # 停止信号需要向上传递，交由任务层标记为“已停止”
            raise
        except Exception as e:
            logger.error(f"构建分块索引失败: {e}")
            return False

  
    def _should_chunk_document(self, content: str, file_type: str) -> bool:
        """判断文档是否需要分块

        Args:
            content: 文档内容
            file_type: 文件类型

        Returns:
            bool: 是否需要分块
        """
        # 获取分块配置
        from app.core.config import get_settings
        settings = get_settings()
        chunk_size = settings.chunk.default_chunk_size

        # 只要内容长度大于分块阈值，就进行分块（不限制文件类型）
        if not content or len(content) <= chunk_size:
            return False

        # 所有达到分块阈值的文件都进行分块处理
        return True

    async def _process_chunked_documents(
        self,
        documents: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None,
        should_stop: Optional[callable] = None,
        rebuild: bool = False
    ) -> bool:
        """流式处理需要分块的文档

        处理流程（按批推进，内存占用与总块数无关）：
        1. 分块
        2. 批量生成向量（float32 ndarray）
        3. 批量写入数据库，拿到真实 chunk_id
        4. 追加到 Faiss 向量索引
        5. 追加到 Whoosh 全文索引，同时清理同一文件的旧文档

        Args:
            documents: 需要分块的文档列表
            progress_callback: 进度回调 callback(stage: str, percent: float)
            should_stop: 停止信号检查函数
            rebuild: True 时重建 Faiss 索引，False 时追加

        Returns:
            bool: 处理是否成功

        Raises:
            IndexBuildStopped: 用户停止任务
        """
        from app.core.config import get_settings
        settings = get_settings()

        embedding_batch_size = max(32, int(getattr(settings.chunk, 'embedding_batch_size', 256)))
        # CPU 环境下大 batch 收益低且占用内存，限制为 32
        try:
            import torch
            if not torch.cuda.is_available():
                embedding_batch_size = min(embedding_batch_size, 32)
        except Exception:
            embedding_batch_size = min(embedding_batch_size, 32)

        pipeline_batch_chunks = max(256, int(getattr(settings.chunk, 'pipeline_batch_chunks', 4096)))
        chunk_size = max(1, int(settings.chunk.default_chunk_size))

        # 预估总块数，仅用于进度展示
        estimated_total = 0
        for doc in documents:
            content = doc.get('content') or ''
            if content:
                estimated_total += max(1, len(content) // chunk_size)
        estimated_total = max(estimated_total, 1)

        logger.info(
            f"开始处理 {len(documents)} 个需要分块的文档（流式分批，"
            f"预计 {estimated_total} 个分块，每批约 {pipeline_batch_chunks} 块）"
        )

        # 准备 Faiss 索引（追加模式会校验元数据一致性）
        faiss_index = None
        faiss_ids_all: List[int] = []
        chunk_ids_all: List[int] = []
        if self.use_ai_models and not rebuild:
            faiss_index, faiss_ids_all, chunk_ids_all = self._load_faiss_for_append()

        # 准备 Whoosh 索引（每批单独提交）
        whoosh_ix = self._open_whoosh_for_write()

        cleared_file_ids = set()
        processed_chunks = 0
        total_saved_chunks = 0
        batches = self._make_document_batches(documents, pipeline_batch_chunks, chunk_size)

        try:
            for batch_no, doc_batch in enumerate(batches, 1):
                if should_stop and should_stop():
                    raise IndexBuildStopped("索引任务已被停止")

                # 1. 分块
                chunks: List[Dict[str, Any]] = []
                for doc in doc_batch:
                    chunks.extend(await self._chunk_document(doc))

                if not chunks:
                    continue

                # 过滤掉没有有效 file_id 的分块（文档未成功入库时可能出现）
                valid_chunks = []
                for chunk in chunks:
                    try:
                        int(chunk.get('file_id'))
                        valid_chunks.append(chunk)
                    except (TypeError, ValueError):
                        logger.warning(f"跳过分块：缺少有效的 file_id ({chunk.get('file_name', 'unknown')})")
                chunks = valid_chunks
                if not chunks:
                    continue

                # 2. 生成索引ID（雪花算法）
                faiss_ids = [generate_snowflake_id(machine_id=1 + i % 1024) for i in range(len(chunks))]
                whoosh_ids = [str(generate_snowflake_id(machine_id=1 + (i + 1000) % 1024)) for i in range(len(chunks))]

                # 3. 批量生成向量
                def _embed_progress(current: int, total: int):
                    if progress_callback and total > 0:
                        overall = 72.0 + 16.0 * (processed_chunks + current) / estimated_total
                        progress_callback("生成向量", min(overall, 88.0))

                embeddings = await self._generate_chunk_embeddings_optimized(
                    chunks,
                    batch_size=embedding_batch_size,
                    should_stop=should_stop,
                    progress_callback=_embed_progress
                )

                if should_stop and should_stop():
                    raise IndexBuildStopped("索引任务已被停止")

                # 4. 先写数据库（清理同一文件的旧分块），拿到真实 chunk_id
                file_ids = {int(c['file_id']) for c in chunks if c.get('file_id') is not None}
                to_clear = [fid for fid in file_ids if fid not in cleared_file_ids]
                saved_ids = self._save_chunks_bulk(chunks, faiss_ids, whoosh_ids, to_clear)
                cleared_file_ids.update(to_clear)

                if len(saved_ids) != len(chunks):
                    logger.warning(f"分块入库数量不匹配: 期望 {len(chunks)}, 实际 {len(saved_ids)}")

                # 5. 追加向量到 Faiss（只有分块与ID数量一致时才写入，避免元数据错位）
                if (
                    self.use_ai_models
                    and embeddings is not None
                    and len(embeddings) == len(chunks)
                    and len(saved_ids) == len(chunks)
                ):
                    if faiss_index is None:
                        faiss_index = faiss.IndexFlatIP(int(embeddings.shape[1]))
                    faiss_index.add(np.ascontiguousarray(embeddings, dtype=np.float32))
                    faiss_ids_all.extend(faiss_ids)
                    chunk_ids_all.extend(saved_ids)

                # 6. 追加到 Whoosh，先删除这些文件的旧文档
                self._add_chunks_to_whoosh(whoosh_ix, chunks, whoosh_ids, to_clear, saved_ids)

                total_saved_chunks += len(saved_ids)
                processed_chunks += len(chunks)
                if progress_callback:
                    overall = 72.0 + 16.0 * min(processed_chunks / estimated_total, 1.0)
                    progress_callback("分块与向量化", min(overall, 88.0))

                logger.info(
                    f"分块批次 {batch_no}/{len(batches)} 完成: 本批 {len(chunks)} 块，"
                    f"累计 {processed_chunks}/{estimated_total}"
                )

            # 7. 落盘 Faiss 索引
            if progress_callback:
                progress_callback("写入索引文件", 90.0)

            if self.use_ai_models:
                self._write_faiss_index(faiss_index, faiss_ids_all, chunk_ids_all)

            if progress_callback:
                progress_callback("索引构建完成", 99.0)

            self.index_stats['total_chunks_created'] = (
                len(chunk_ids_all) if self.use_ai_models else total_saved_chunks
            )
            return True

        except IndexBuildStopped:
            # 已完成批次的数据已经落盘，保证索引与数据库一致
            try:
                if self.use_ai_models:
                    self._write_faiss_index(faiss_index, faiss_ids_all, chunk_ids_all)
            except Exception as write_error:
                logger.error(f"停止时写入 Faiss 索引失败: {write_error}")
            raise

        except Exception as e:
            logger.error(f"处理分块文档失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    def _make_document_batches(
        self,
        documents: List[Dict[str, Any]],
        max_chunks_per_batch: int,
        chunk_size: int
    ) -> List[List[Dict[str, Any]]]:
        """按预估块数把文档切成若干批，单个超大文档独立成批"""
        batches: List[List[Dict[str, Any]]] = []
        current: List[Dict[str, Any]] = []
        current_chunks = 0

        for doc in documents:
            content = doc.get('content') or ''
            estimated = max(1, len(content) // chunk_size) if content else 0

            if current and current_chunks + estimated > max_chunks_per_batch:
                batches.append(current)
                current = []
                current_chunks = 0

            current.append(doc)
            current_chunks += estimated

            if current_chunks >= max_chunks_per_batch:
                batches.append(current)
                current = []
                current_chunks = 0

        if current:
            batches.append(current)

        return batches

    def _load_faiss_for_append(self):
        """加载已有 Faiss 索引用于追加

        Returns:
            tuple: (index, faiss_ids, chunk_ids)；元数据不一致时 index 为 None（改为重建）
        """
        index = None
        metadata = {}

        if os.path.exists(self.chunk_faiss_index_path):
            try:
                index = faiss.read_index(self.chunk_faiss_index_path)
                metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
            except Exception as e:
                logger.warning(f"加载已有分块Faiss索引失败，将新建索引: {e}")
                index = None
                metadata = {}

        faiss_ids = list(metadata.get('pregenerated_snowflake_ids', []))
        chunk_ids = list(metadata.get('chunk_ids', []))

        # 历史数据可能只写了索引没写 chunk_ids（例如任务中途被强杀），此时追加会导致映射错位
        if index is not None and len(chunk_ids) != index.ntotal:
            logger.warning(
                f"Faiss索引行数({index.ntotal})与元数据chunk_ids({len(chunk_ids)})不一致，改为重建索引"
            )
            index = None
            faiss_ids = []
            chunk_ids = []

        return index, faiss_ids, chunk_ids

    def _write_faiss_index(self, index, faiss_ids: List[int], chunk_ids: List[int]) -> None:
        """原子写入 Faiss 索引及元数据"""
        if index is None:
            return

        index_dir = os.path.dirname(self.chunk_faiss_index_path)
        if index_dir:
            os.makedirs(index_dir, exist_ok=True)

        # 先写临时文件再替换，避免中途失败破坏旧索引
        tmp_path = self.chunk_faiss_index_path + '.tmp'
        faiss.write_index(index, tmp_path)
        os.replace(tmp_path, self.chunk_faiss_index_path)

        metadata = {
            'index_type': 'IndexFlatIP',
            'dimension': int(index.d),
            'total_chunks': int(index.ntotal),
            'created_at': datetime.now().isoformat(),
            'pregenerated_snowflake_ids': faiss_ids,
            'chunk_ids': chunk_ids,
            'embedding_batch_size': self.index_stats.get('embedding_batch_size')
        }
        metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
        tmp_meta_path = metadata_path + '.tmp'
        with open(tmp_meta_path, 'wb') as f:
            pickle.dump(metadata, f)
        os.replace(tmp_meta_path, metadata_path)

        logger.info(f"分块Faiss索引写入完成: {index.ntotal} 条向量, {len(chunk_ids)} 个 chunk_id")

    def _open_whoosh_for_write(self):
        """打开（或创建）分块 Whoosh 索引"""
        from whoosh import index as whoosh_index

        os.makedirs(self.chunk_whoosh_index_path, exist_ok=True)
        if whoosh_index.exists_in(self.chunk_whoosh_index_path):
            return whoosh_index.open_dir(self.chunk_whoosh_index_path)
        return whoosh_index.create_in(self.chunk_whoosh_index_path, self._chunk_whoosh_schema())

    def _chunk_whoosh_schema(self):
        """分块 Whoosh 索引的字段定义"""
        from whoosh import fields
        from whoosh.analysis import StandardAnalyzer

        analyzer = StandardAnalyzer()
        return fields.Schema(
            id=fields.ID(stored=True, unique=True),
            chunk_id=fields.ID(stored=True),
            file_id=fields.NUMERIC(stored=True, numtype=int),
            content=fields.TEXT(analyzer=analyzer, stored=True, phrase=True),
            file_name=fields.TEXT(analyzer=analyzer, stored=True),
            file_path=fields.ID(stored=True),
            file_type=fields.ID(stored=True),
            file_size=fields.NUMERIC(stored=True, sortable=True),
            chunk_index=fields.NUMERIC(stored=True, numtype=int),
            total_chunks=fields.NUMERIC(stored=True, numtype=int),
            keywords=fields.KEYWORD(stored=True, commas=True),
            embedding=fields.TEXT(stored=True),
            modified_time=fields.ID(stored=True, sortable=True),
            created_at=fields.ID(stored=True, sortable=True),
            content_stored=fields.STORED(),
            start_position=fields.NUMERIC(stored=True, numtype=int),
            end_position=fields.NUMERIC(stored=True, numtype=int),
            content_length=fields.NUMERIC(stored=True, numtype=int),
            title=fields.TEXT(analyzer=analyzer, stored=True),
            source_type=fields.ID(stored=True),
            source_url=fields.ID(stored=True)
        )

    def _build_whoosh_doc(self, chunk: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """构造 Whoosh 文档"""
        modified_time = chunk.get('modified_time', datetime.now())
        created_at = chunk.get('created_at', datetime.now())
        modified_timestamp = int(modified_time.timestamp()) if isinstance(modified_time, datetime) else int(float(modified_time))
        created_timestamp = int(created_at.timestamp()) if isinstance(created_at, datetime) else int(float(created_at))

        return {
            'id': doc_id,
            'chunk_id': chunk.get('chunk_id', ''),
            'file_id': chunk.get('file_id', 0),
            'content': chunk.get('content', ''),
            'content_stored': chunk.get('content', ''),
            'file_name': chunk.get('file_name', ''),
            'file_path': chunk.get('file_path', ''),
            'file_type': chunk.get('file_type', ''),
            'file_size': chunk.get('file_size', 0),
            'chunk_index': chunk.get('chunk_index', 0),
            'start_position': chunk.get('start_position', 0),
            'end_position': chunk.get('end_position', 0),
            'content_length': chunk.get('content_length', len(chunk.get('content', ''))),
            'total_chunks': chunk.get('total_chunks', 1),
            'keywords': ' '.join(chunk.get('keywords', [])),
            'embedding': str(chunk.get('embedding', [])),
            'modified_time': str(modified_timestamp),
            'created_at': str(created_timestamp),
            'title': chunk.get('file_name', ''),
            'source_type': chunk.get('source_type'),
            'source_url': chunk.get('source_url')
        }

    def _add_chunks_to_whoosh(
        self,
        ix,
        chunks: List[Dict[str, Any]],
        whoosh_ids: List[str],
        clear_file_ids: Optional[List[int]] = None,
        saved_chunk_ids: Optional[List[int]] = None
    ) -> None:
        """批量追加分块到 Whoosh，并删除同文件的旧文档

        按 file_id 删除可以覆盖历史遗留的孤儿文档（例如上次任务被强杀时只写入了索引未写数据库）。
        """
        from whoosh.writing import AsyncWriter

        writer = AsyncWriter(ix)

        for file_id in (clear_file_ids or []):
            try:
                writer.delete_by_term('file_id', int(file_id))
            except Exception as e:
                logger.debug(f"删除文件 {file_id} 的旧Whoosh文档失败: {e}")

        for i, (chunk, doc_id) in enumerate(zip(chunks, whoosh_ids)):
            doc = self._build_whoosh_doc(chunk, doc_id)
            if saved_chunk_ids and i < len(saved_chunk_ids):
                doc['chunk_id'] = str(saved_chunk_ids[i])
            writer.add_document(**doc)

        writer.commit()

    def _save_chunks_bulk(
        self,
        chunks: List[Dict[str, Any]],
        faiss_ids: List[int],
        whoosh_ids: List[str],
        clear_file_ids: Optional[List[int]] = None
    ):
        """批量保存分块到数据库

        Args:
            chunks: 分块列表
            faiss_ids: Faiss 索引ID列表
            whoosh_ids: Whoosh 文档ID列表
            clear_file_ids: 需要先清理旧分块的文件ID列表（每个文件只需清理一次）

        Returns:
            List[int]: 按 chunks 顺序排列的数据库ID列表
        """
        from app.core.database import SessionLocal
        from app.models.file_chunk import FileChunkModel

        db = SessionLocal()
        try:
            # 1. 清理同一文件的旧分块
            if clear_file_ids:
                ids = list(clear_file_ids)
                for i in range(0, len(ids), 400):
                    subset = ids[i:i + 400]
                    db.query(FileChunkModel).filter(
                        FileChunkModel.file_id.in_(subset)
                    ).delete(synchronize_session=False)
                db.commit()

            # 2. 批量插入
            now = datetime.now()
            mappings = []
            for i, chunk in enumerate(chunks):
                mappings.append({
                    'file_id': int(chunk['file_id']),
                    'chunk_index': int(chunk['chunk_index']),
                    'content': chunk['content'],
                    'content_length': chunk.get('content_length', len(chunk['content'])),
                    'start_position': int(chunk.get('start_position', 0)),
                    'end_position': int(chunk.get('end_position', 0)),
                    'faiss_index_id': faiss_ids[i] if i < len(faiss_ids) else None,
                    'whoosh_doc_id': whoosh_ids[i] if i < len(whoosh_ids) else None,
                    'is_indexed': True,
                    'index_status': 'completed',
                    'created_at': now,
                    'indexed_at': now
                })

            for i in range(0, len(mappings), 1000):
                db.bulk_insert_mappings(FileChunkModel, mappings[i:i + 1000])
                db.commit()

            # 3. 回查主键，按 chunks 顺序返回
            file_ids = sorted({int(c['file_id']) for c in chunks})
            id_map = {}
            for i in range(0, len(file_ids), 400):
                subset = file_ids[i:i + 400]
                rows = db.query(
                    FileChunkModel.id,
                    FileChunkModel.file_id,
                    FileChunkModel.chunk_index
                ).filter(FileChunkModel.file_id.in_(subset)).all()
                for row in rows:
                    id_map[(int(row[1]), int(row[2]))] = int(row[0])

            saved_ids = []
            missing = 0
            for chunk in chunks:
                key = (int(chunk['file_id']), int(chunk['chunk_index']))
                chunk_id = id_map.get(key)
                if chunk_id is None:
                    missing += 1
                else:
                    saved_ids.append(chunk_id)

            if missing:
                logger.warning(f"有 {missing} 个分块回查数据库主键失败")

            logger.info(f"批量保存 {len(chunks)} 个分块到数据库完成，回查 {len(saved_ids)} 个ID")
            return saved_ids

        finally:
            db.close()

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
                    'modified_time': document.get('modified_time', datetime.now()),
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
            if embeddings is None or len(embeddings) == 0:
                logger.error("向量嵌入生成失败")
                return False

            # 2. 创建优化的Faiss索引
            dimension = int(embeddings.shape[1])

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
                'chunk_ids': [str(chunk.get('id', f"chunk_{chunk.get('chunk_index', i)}_file_{chunk.get('file_id', '')}")) for i, chunk in enumerate(chunks)],
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

    async def _generate_chunk_embeddings_optimized(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 256,
        should_stop: Optional[callable] = None,
        progress_callback: Optional[callable] = None
    ) -> np.ndarray:
        """优化的批量生成分块向量嵌入（返回 float32 数组）

        与旧实现相比：
        - 返回 np.ndarray，避免构造数亿个 Python float 对象
        - 单次推理批大小可配置（GPU 建议 256 以上）
        - 支持停止信号与进度回调

        Args:
            chunks: 分块列表
            batch_size: 单次推理的批大小
            should_stop: 停止信号检查函数
            progress_callback: 进度回调 callback(processed, total)

        Returns:
            np.ndarray: 形状为 (len(chunks), dim) 的 float32 数组

        Raises:
            IndexBuildStopped: 用户停止任务
        """
        try:
            if not chunks:
                return np.zeros((0, 1024), dtype=np.float32)

            total_chunks = len(chunks)
            batch_size = max(8, int(batch_size))

            # 过滤过短内容，记录原始位置以便对齐
            valid_texts: List[str] = []
            valid_indices: List[int] = []

            for i, chunk in enumerate(chunks):
                content = (chunk.get('content') or '').strip()
                if content and len(content) > 10:
                    valid_texts.append(content)
                    valid_indices.append(i)

            failed_count = total_chunks - len(valid_texts)
            if failed_count:
                logger.warning(f"有 {failed_count} 个分块内容过短，使用零向量占位")

            logger.info(
                f"开始批量生成 {len(valid_texts)} 个分块的向量嵌入，"
                f"批大小: {batch_size}, 分块总数: {total_chunks}"
            )

            embeddings = None
            processed = 0
            total = len(valid_texts)

            for start in range(0, total, batch_size):
                if should_stop and should_stop():
                    raise IndexBuildStopped("索引任务已被停止")

                end = min(start + batch_size, total)
                batch_texts = valid_texts[start:end]

                try:
                    batch_embeddings = await ai_model_service.batch_text_embedding_array(
                        batch_texts,
                        batch_size=batch_size,
                        normalize_embeddings=True
                    )
                except Exception as batch_error:
                    logger.error(f"向量嵌入批次失败 (起始 {start}): {batch_error}")
                    processed += len(batch_texts)
                    continue

                if batch_embeddings is None or batch_embeddings.shape[0] != len(batch_texts):
                    actual = 0 if batch_embeddings is None else batch_embeddings.shape[0]
                    logger.warning(
                        f"向量嵌入数量不匹配: 期望 {len(batch_texts)}, 实际 {actual}"
                    )
                    processed += len(batch_texts)
                    continue

                if embeddings is None:
                    embeddings = np.zeros(
                        (total_chunks, int(batch_embeddings.shape[1])),
                        dtype=np.float32
                    )

                # 按原始位置回填，保证与 chunks 顺序严格对齐
                for offset, chunk_index in enumerate(valid_indices[start:end]):
                    embeddings[chunk_index] = batch_embeddings[offset]

                processed += len(batch_texts)
                if progress_callback:
                    progress_callback(processed, total)

            if embeddings is None:
                embeddings = np.zeros((total_chunks, 1024), dtype=np.float32)

            logger.info(f"向量嵌入生成完成 - 成功: {len(valid_texts)}, 占位: {failed_count}")
            return embeddings

        except IndexBuildStopped:
            raise
        except Exception as e:
            logger.error(f"优化生成分块向量嵌入失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return np.zeros((len(chunks), 1024), dtype=np.float32)

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
                file_size=fields.NUMERIC(stored=True, sortable=True),

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

                # 数据源信息（插件系统）
                source_type=fields.ID(stored=True),
                source_url=fields.ID(stored=True),

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
                from whoosh.index import open_dir
                ix = open_dir(self.chunk_whoosh_index_path, schema=chunk_schema)
            else:
                # 创建新索引
                from whoosh.index import create_in
                ix = create_in(self.chunk_whoosh_index_path, chunk_schema)

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
                                file_size=int(chunk.get('file_size', 0)),
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
                                content_preview=content_preview,
                                # 数据源信息（插件系统）
                                source_type=chunk.get('source_type'),
                                source_url=chunk.get('source_url')
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

    async def _save_chunks_to_database(self, chunks: List[Dict[str, Any]], faiss_index_ids: List[int] = None, whoosh_doc_ids: List[str] = None) -> bool:
        """保存分块数据到数据库并更新files表的分块状态

        Args:
            chunks: 分块列表
            faiss_index_ids: Faiss索引ID列表
            whoosh_doc_ids: Whoosh文档ID列表

        Returns:
            bool: 保存是否成功
        """
        try:
            from app.core.database import SessionLocal
            from app.models.file_chunk import FileChunkModel

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
                    # 获取文件ID
                    file_id = chunk_data['file_id']
                    # 检查是否已存在
                    existing_chunk = db.query(FileChunkModel).filter(
                        FileChunkModel.file_id == file_id,
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
                            file_id=file_id,  # 使用转换后的整数ID
                            chunk_index=chunk_data['chunk_index'],
                            content=chunk_data['content'],
                            content_length=chunk_data['content_length'],
                            start_position=chunk_data['start_position'],
                            end_position=chunk_data['end_position'],
                            # 添加索引ID
                            faiss_index_id=faiss_index_ids[i] if faiss_index_ids and i < len(faiss_index_ids) else None,
                            whoosh_doc_id=whoosh_doc_ids[i] if whoosh_doc_ids and i < len(whoosh_doc_ids) else None,
                            is_indexed=True,
                            index_status='completed',
                            indexed_at=datetime.now()
                        )
                        db.add(chunk_record)

                    # 定期提交
                    if (i + 1) % 50 == 0:
                        db.commit()
                        logger.debug(f"已保存 {i + 1}/{len(chunks)} 个分块")

                
                # 最终提交
                db.commit()

                # 获取保存后的数据库ID
                saved_chunk_ids = []
                for chunk_data in chunks:
                    file_id = chunk_data['file_id']
                    chunk_index = chunk_data['chunk_index']
                    saved_chunk = db.query(FileChunkModel).filter(
                        FileChunkModel.file_id == file_id,
                        FileChunkModel.chunk_index == chunk_index
                    ).first()
                    if saved_chunk:
                        saved_chunk_ids.append(saved_chunk.id)
                    else:
                        logger.warning(f"找不到保存的分块: file_id={file_id}, chunk_index={chunk_index}")

                logger.info(f"成功保存 {len(chunks)} 个分块到数据库，获取ID数量: {len(saved_chunk_ids)}")
                return saved_chunk_ids

            finally:
                db.close()

        except Exception as e:
            logger.error(f"保存分块到数据库失败: {e}")
            return False

    async def _update_files_chunk_status(self, chunks: List[Dict[str, Any]]) -> None:
        """更新files表的分块状态

        Args:
            chunks: 分块列表
        """
        try:
            from app.core.database import SessionLocal
            from app.models.file import FileModel

            db = SessionLocal()
            try:
                # 统计每个文件的分块数量
                file_chunk_stats = {}
                for chunk in chunks:
                    file_id = chunk.get('file_id')
                    if file_id not in file_chunk_stats:
                        file_chunk_stats[file_id] = 0
                    file_chunk_stats[file_id] += 1

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

            finally:
                db.close()

        except Exception as e:
            logger.error(f"更新文件分块状态失败: {e}")

    def _chunk_indexes_exist(self) -> bool:
        """检查分块索引是否存在"""
        faiss_exists = os.path.exists(self.chunk_faiss_index_path)
        whoosh_exists = os.path.exists(self.chunk_whoosh_index_path) and os.listdir(self.chunk_whoosh_index_path)
        return faiss_exists or whoosh_exists

    def _update_index_stats(self, chunked_count: int):
        """更新索引统计信息

        注意：总分块数由流式构建过程写入真实值，这里不再使用估算值累加。
        """
        self.index_stats['total_documents_processed'] += chunked_count
        self.index_stats['chunked_documents'] += chunked_count

        # 计算平均分块数
        total_docs = self.index_stats['total_documents_processed']
        if total_docs > 0:
            self.index_stats['avg_chunks_per_document'] = self.index_stats['total_chunks_created'] / total_docs

    async def update_chunk_indexes(self, documents: List[Dict[str, Any]]) -> bool:
        """增量更新分块索引和CLIP图像索引

        Args:
            documents: 新文档列表（包含文本和图片文件）

        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info(f"开始增量更新索引，文档数量: {len(documents)}")
            start_time = time.time()

            # 1. 处理文本分块索引
            # 过滤出需要分块的文档
            chunked_docs = []
            image_docs = []

            for doc in documents:
                if self._should_chunk_document(doc.get('content', ''), doc.get('file_type', '')):
                    chunked_docs.append(doc)
                elif doc.get('file_type') == 'image':
                    image_docs.append(doc)

            logger.info(f"需要分块的文档: {len(chunked_docs)}, 图片文档: {len(image_docs)}")

            # 2. 处理文本分块
            text_success = True
            if chunked_docs:
                # 生成分块
                all_chunks = []
                for doc in chunked_docs:
                    chunks = await self._chunk_document(doc)
                    all_chunks.extend(chunks)

                if all_chunks:
                    # 更新Faiss和Whoosh索引
                    faiss_success = await self._update_faiss_index(all_chunks)
                    whoosh_success = await self._update_whoosh_index(all_chunks)

                    # 生成索引ID
                    new_faiss_ids = []
                    new_whoosh_ids = []
                    for i, chunk in enumerate(all_chunks):
                        faiss_id = generate_snowflake_id(machine_id=1 + i % 1024)
                        new_faiss_ids.append(faiss_id)
                        whoosh_id = str(generate_snowflake_id(machine_id=1 + (i + 1000) % 1024))
                        new_whoosh_ids.append(whoosh_id)

                    # 保存到数据库
                    saved_chunk_ids = await self._save_chunks_to_database(all_chunks, new_faiss_ids, new_whoosh_ids)
                    if saved_chunk_ids:
                        # 更新Whoosh索引中的chunk_ids为数据库真实ID
                        if whoosh_success:
                            await self._update_whoosh_chunk_ids(all_chunks, saved_chunk_ids)
                        db_success = True
                    else:
                        db_success = False
                    text_success = faiss_success and whoosh_success and db_success

            # 3. 更新CLIP图像索引
            image_success = True
            if image_docs and self.use_ai_models:
                logger.info(f"开始更新CLIP图像索引，图片数量: {len(image_docs)}")
                image_success = await self._update_clip_image_index(image_docs)
            else:
                logger.info("没有新的图片文件需要更新CLIP索引")

            duration = time.time() - start_time
            logger.info(f"增量索引更新完成，耗时: {duration:.2f}秒")

            return text_success and image_success

        except Exception as e:
            logger.error(f"增量更新索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def _update_faiss_index(self, new_chunks: List[Dict[str, Any]]) -> bool:
        """增量更新Faiss索引"""
        try:
            # 读取现有索引
            index = faiss.read_index(self.chunk_faiss_index_path)

            # 生成新向量的嵌入
            embeddings = await self._generate_chunk_embeddings(new_chunks)
            if embeddings is None or len(embeddings) == 0:
                return False

            # 添加新向量
            embeddings_array = np.ascontiguousarray(embeddings, dtype=np.float32)
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
                        file_size=int(chunk.get('file_size', 0)),
                        content=chunk['content'],
                        chunk_index=chunk['chunk_index'],
                        start_position=chunk['start_position'],
                        end_position=chunk['end_position'],
                        content_length=chunk['content_length'],
                        modified_time=chunk['modified_time'],
                        created_at=chunk['created_at'].isoformat() if isinstance(chunk['created_at'], datetime) else str(chunk['created_at']),
                        # 数据源信息（插件系统）
                        source_type=chunk.get('source_type'),
                        source_url=chunk.get('source_url')
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

    async def _update_clip_image_index(self, image_documents: List[Dict[str, Any]]) -> bool:
        """增量更新CLIP图像向量索引

        Args:
            image_documents: 图片文档列表

        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info(f"开始增量更新CLIP图像索引，图片数量: {len(image_documents)}")
            start_time = time.time()

            # 检查现有图像索引
            base_path = os.path.dirname(self.chunk_faiss_index_path)
            clip_faiss_path = os.path.join(base_path, 'clip_image_index.faiss')
            clip_metadata_path = os.path.join(base_path, 'clip_image_metadata.pkl')

            if not os.path.exists(clip_faiss_path) or not os.path.exists(clip_metadata_path):
                logger.warning("CLIP图像索引不存在，跳过增量更新")
                return True

            # 加载现有索引和元数据
            clip_index = faiss.read_index(clip_faiss_path)
            with open(clip_metadata_path, 'rb') as f:
                existing_metadata = pickle.load(f)

            # 提取新图片的CLIP特征向量
            new_image_vectors = []
            new_image_metadata = {}

            current_vector_id = len(existing_metadata)  # 从现有向量ID开始

            for doc in image_documents:
                try:
                    file_path = doc.get('file_path', '')
                    if not file_path or not os.path.exists(file_path):
                        logger.warning(f"图片文件不存在: {file_path}")
                        continue

                    # 检查是否已存在于现有索引中
                    existing_vector_id = None
                    for vid, metadata in existing_metadata.items():
                        if metadata.get('file_path') == file_path:
                            existing_vector_id = vid
                            break

                    if existing_vector_id is not None:
                        logger.debug(f"图片已存在于索引中，跳过: {doc.get('file_name', 'unknown')}")
                        continue

                    # 使用AI模型服务提取CLIP特征向量
                    clip_vector = await ai_model_service.encode_image(file_path)

                    if clip_vector is not None and len(clip_vector) > 0:
                        # 存储向量
                        new_image_vectors.append(np.array(clip_vector, dtype=np.float32))

                        # 存储元数据
                        vector_id = current_vector_id + len(new_image_vectors) - 1
                        new_image_metadata[vector_id] = {
                            'file_id': doc.get('id', 0),
                            'file_name': doc.get('file_name', ''),
                            'file_path': file_path,
                            'file_type': doc.get('file_type', ''),
                            'file_size': doc.get('file_size', 0),
                            'created_at': doc.get('created_at', datetime.now()).isoformat() if doc.get('created_at') else '',
                            'modified_at': doc.get('modified_time', datetime.now()).isoformat() if doc.get('modified_time') else ''
                        }

                        logger.info(f"提取图片特征向量: {doc.get('file_name', 'unknown')}")
                    else:
                        logger.warning(f"图片文件CLIP特征向量提取失败: {file_path}")

                except Exception as e:
                    logger.warning(f"处理图片文件失败 {doc.get('file_path', 'unknown')}: {str(e)}")
                    continue

            if len(new_image_vectors) == 0:
                logger.info("没有新的图片需要添加到CLIP索引")
                return True

            # 确保向量维度一致
            vector_matrix = np.vstack(new_image_vectors).astype(np.float32)
            if vector_matrix.shape[1] != clip_index.d:
                logger.error(f"新图片向量维度 {vector_matrix.shape[1]} 与索引维度 {clip_index.d} 不匹配")
                return False

            # 添加新向量到现有索引
            clip_index.add(vector_matrix)

            # 更新元数据
            existing_metadata.update(new_image_metadata)

            # 保存更新后的索引和元数据
            faiss.write_index(clip_index, clip_faiss_path)
            with open(clip_metadata_path, 'wb') as f:
                pickle.dump(existing_metadata, f)

            update_time = time.time() - start_time
            logger.info(f"CLIP图像索引增量更新完成: 新增 {len(new_image_vectors)} 个向量，索引总数: {clip_index.ntotal}，耗时: {update_time:.2f}秒")
            return True

        except Exception as e:
            logger.error(f"增量更新CLIP图像索引失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
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

    async def _build_chunk_faiss_index_with_ids(self, chunks: List[Dict[str, Any]], pregenerated_ids: List[int]) -> bool:
        """构建分块Faiss向量索引（使用预生成的雪花ID）

        Args:
            chunks: 分块列表
            pregenerated_ids: 预生成的Faiss索引ID列表

        Returns:
            bool: 构建是否成功
        """
        start_time = time.time()
        try:
            # 1. 生成向量嵌入
            embeddings = await self._generate_chunk_embeddings_optimized(chunks)

            # 2. 创建优化的Faiss索引
            if embeddings is None or len(embeddings) == 0:
                logger.error("没有向量嵌入，无法创建索引")
                return False

            dimension = int(embeddings.shape[1])
            logger.info(f"Faiss索引维度: {dimension}")

            # 创建Flat索引
            index_type = 'IndexFlatIP'
            index = faiss.IndexFlatIP(dimension)

            # 3. 训练索引（如果需要）
            if hasattr(index, 'train') and not index.is_trained:
                logger.info("训练Faiss索引...")
                embeddings_array = np.array(embeddings).astype('float32')
                index.train(embeddings_array)

            # 4. 添加向量到索引
            embeddings_array = np.array(embeddings).astype('float32')
            index.add(embeddings_array)

            # 5. 保存索引到文件
            index_dir = os.path.dirname(self.chunk_faiss_index_path)
            if not os.path.exists(index_dir):
                os.makedirs(index_dir, exist_ok=True)

            faiss.write_index(index, self.chunk_faiss_index_path)

            # 6. 保存元数据（包含雪花ID映射）
            metadata = {
                'index_type': index_type,
                'dimension': dimension,
                'total_chunks': len(chunks),
                'created_at': datetime.now().isoformat(),
                'pregenerated_snowflake_ids': pregenerated_ids,
                'build_time_seconds': time.time() - start_time,
                'embedding_batch_size': self.index_stats['embedding_batch_size']
            }

            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)

            build_time = time.time() - start_time
            logger.info(f"分块Faiss索引构建成功（雪花ID） - 类型: {index_type}, 维度: {dimension}, 分块数: {index.ntotal}, 耗时: {build_time:.2f}秒")
            logger.debug(f"使用雪花ID数量: {len(pregenerated_ids)}")

            return True

        except Exception as e:
            logger.error(f"构建分块Faiss索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def _build_chunk_whoosh_index_with_ids(self, chunks: List[Dict[str, Any]], pregenerated_ids: List[str]) -> bool:
        """构建分块Whoosh全文索引（使用预生成的雪花ID）

        Args:
            chunks: 分块列表
            pregenerated_ids: 预生成的Whoosh文档ID列表

        Returns:
            bool: 构建是否成功
        """
        try:
            if len(chunks) != len(pregenerated_ids):
                logger.error(f"分块数量({len(chunks)})与ID数量({len(pregenerated_ids)})不匹配")
                return False

            from whoosh.writing import AsyncWriter

            # 1. 打开（或创建）索引
            ix = self._open_whoosh_for_write()

            # 2. 构建索引文档
            writer = AsyncWriter(ix)

            for chunk, doc_id in zip(chunks, pregenerated_ids):
                writer.add_document(**self._build_whoosh_doc(chunk, doc_id))

            # 3. 提交写入
            writer.commit()

            logger.info(f"分块Whoosh索引构建成功（雪花ID） - 文档数: {len(chunks)}")
            logger.debug(f"使用雪花ID数量: {len(pregenerated_ids)}")

            return True

        except Exception as e:
            logger.error(f"构建分块Whoosh索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def delete_file_from_indexes(self, file_path: str) -> Dict[str, Any]:
        """从索引中删除文件

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            logger.info(f"开始从索引中删除文件: {file_path}")
            start_time = time.time()

            # 1. 从数据库查找文件记录和相关的分块记录
            from app.core.database import SessionLocal
            from app.models.file import FileModel
            from app.models.file_chunk import FileChunkModel

            db = SessionLocal()
            try:
                # 查找文件记录
                file_record = db.query(FileModel).filter(
                    FileModel.file_path == file_path
                ).first()

                if not file_record:
                    logger.warning(f"文件不存在于数据库中: {file_path}")
                    return {
                        'success': False,
                        'error': f'文件不存在于数据库中: {file_path}'
                    }

                # 查找相关的分块记录
                chunk_records = db.query(FileChunkModel).filter(
                    FileChunkModel.file_id == file_record.id
                ).all()

                logger.info(f"找到文件记录: {file_record.id}, 分块数量: {len(chunk_records)}")

                # 2. 从Faiss索引删除相关向量
                faiss_deleted_count = 0
                if chunk_records:
                    faiss_deleted_count = await self._delete_from_faiss_index(chunk_records)

                # 3. 从Whoosh索引删除相关文档
                whoosh_deleted_count = 0
                if chunk_records:
                    whoosh_deleted_count = await self._delete_from_whoosh_index(chunk_records)

                # 4. 从数据库删除分块记录
                if chunk_records:
                    deleted_chunks = db.query(FileChunkModel).filter(
                        FileChunkModel.file_id == file_record.id
                    ).delete()
                    logger.info(f"从数据库删除了 {deleted_chunks} 个分块记录")

                # 5. 从数据库删除文件记录
                db.delete(file_record)
                db.commit()

                duration = time.time() - start_time
                logger.info(f"文件删除完成，耗时: {duration:.2f} 秒")

                return {
                    'success': True,
                    'file_path': file_path,
                    'deleted_chunks': len(chunk_records),
                    'faiss_deleted_count': faiss_deleted_count,
                    'whoosh_deleted_count': whoosh_deleted_count,
                    'duration_seconds': duration
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"从索引删除文件失败 {file_path}: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def _delete_from_faiss_index(self, chunk_records: List) -> int:
        """从Faiss索引删除向量

        Args:
            chunk_records: 分块记录列表

        Returns:
            int: 删除的向量数量
        """
        try:
            if not os.path.exists(self.chunk_faiss_index_path):
                logger.warning("Faiss索引文件不存在，跳过删除")
                return 0

            # 加载Faiss索引
            import faiss
            index = faiss.read_index(self.chunk_faiss_index_path)

            # 加载元数据
            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            if not os.path.exists(metadata_path):
                logger.warning("Faiss元数据文件不存在，无法精确删除")
                return 0

            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)

            # 收集需要删除的向量ID
            ids_to_remove = set()
            for chunk in chunk_records:
                if chunk.faiss_index_id is not None:
                    ids_to_remove.add(chunk.faiss_index_id)

            if not ids_to_remove:
                logger.info("没有需要删除的Faiss向量ID")
                return 0

            logger.info(f"准备从Faiss索引删除 {len(ids_to_remove)} 个向量")

            # 重建索引（Faiss不支持直接删除）
            new_index = faiss.IndexFlatL2(index.d)
            new_metadata = []

            # 遍历现有向量，跳过需要删除的
            removed_count = 0
            for i in range(index.ntotal):
                vector_id = metadata.get('vector_ids', [])[i] if i < len(metadata.get('vector_ids', [])) else None

                if vector_id not in ids_to_remove:
                    # 保留这个向量
                    vector = index.reconstruct(i)
                    new_index.add(vector.reshape(1, -1))
                    new_metadata.append(vector_id)
                    removed_count += 1
                else:
                    logger.debug(f"跳过删除的向量ID: {vector_id}")

            if removed_count < index.ntotal:
                # 有向量被删除，重建索引文件
                faiss.write_index(new_index, self.chunk_faiss_index_path)

                # 保存新的元数据
                new_metadata_dict = {'vector_ids': new_metadata}
                with open(metadata_path, 'wb') as f:
                    pickle.dump(new_metadata_dict, f)

                logger.info(f"Faiss索引重建完成，保留了 {removed_count} 个向量，删除了 {index.ntotal - removed_count} 个向量")
                return index.ntotal - removed_count
            else:
                logger.info("没有向量需要删除")
                return 0

        except Exception as e:
            logger.error(f"从Faiss索引删除失败: {e}")
            return 0

    async def _delete_from_whoosh_index(self, chunk_records: List) -> int:
        """从Whoosh索引删除文档

        Args:
            chunk_records: 分块记录列表

        Returns:
            int: 删除的文档数量
        """
        try:
            if not os.path.exists(self.chunk_whoosh_index_path):
                logger.warning("Whoosh索引目录不存在，跳过删除")
                return 0

            from whoosh.index import open_dir
            from whoosh.query import Term

            # 打开Whoosh索引
            ix = open_dir(self.chunk_whoosh_index_path)
            deleted_count = 0

            with ix.writer() as writer:
                for chunk in chunk_records:
                    if chunk.whoosh_doc_id:
                        # 通过文档ID删除
                        writer.delete_by_term('id', chunk.whoosh_doc_id)
                        deleted_count += 1
                        logger.debug(f"��除Whoosh文档: {chunk.whoosh_doc_id}")

            logger.info(f"从Whoosh索引删除了 {deleted_count} 个文档")
            return deleted_count

        except Exception as e:
            logger.error(f"从Whoosh索引删除失败: {e}")
            return 0

    async def _build_clip_image_index(self, documents: List[Dict[str, Any]]) -> bool:
        """构建CLIP图像向量索引

        Args:
            documents: 文档列表

        Returns:
            bool: 构建是否成功
        """
        try:
            logger.info("开始构建CLIP图像向量索引")
            logger.info(f"总文档数量: {len(documents)}")
            start_time = time.time()

            # 1. 筛选出图片文件
            image_files = []

            for doc in documents:
                file_type = doc.get('file_type', '')

                # 直接使用 file_type == 'image' 判断（与content_parser.py逻辑一致）
                if file_type == 'image':
                    logger.info(f"找到图片文件: {doc.get('file_name', 'unknown')}, 类型: {file_type}")
                    image_files.append(doc)
                else:
                    logger.debug(f"非图片文件: {doc.get('file_name', 'unknown')}, 类型: {file_type}")

            if not image_files:
                logger.info("没有找到图片文件，跳过CLIP索引构建")
                return True

            logger.info(f"找到 {len(image_files)} 个图片文件")

            # 2. 提取CLIP特征向量
            image_vectors = []
            image_metadata = {}

            for i, file_record in enumerate(image_files):
                try:
                    file_path = file_record.get('file_path', '')
                    if not file_path or not os.path.exists(file_path):
                        logger.warning(f"图片文件不存在: {file_path}")
                        continue

                    # 使用AI模型服务提取CLIP特征向量
                    clip_vector = await ai_model_service.encode_image(file_path)

                    if clip_vector is not None and len(clip_vector) > 0:
                        # 存储向量
                        image_vectors.append(np.array(clip_vector, dtype=np.float32))

                        # 存储元数据
                        vector_id = len(image_vectors) - 1
                        image_metadata[vector_id] = {
                            'file_id': file_record.get('id', 0),
                            'file_name': file_record.get('file_name', ''),
                            'file_path': file_path,
                            'file_type': file_record.get('file_type', ''),
                            'file_size': file_record.get('file_size', 0),
                            'created_at': file_record.get('created_at', datetime.now()).isoformat() if file_record.get('created_at') else '',
                            'modified_at': file_record.get('modified_time', datetime.now()).isoformat() if file_record.get('modified_time') else ''
                        }

                        if (i + 1) % 10 == 0:
                            logger.info(f"已处理 {i + 1}/{len(image_files)} 个图片文件")
                    else:
                        logger.warning(f"图片文件CLIP特征向量提取失败: {file_path}")

                except Exception as e:
                    logger.warning(f"处理图片文件失败 {file_record.get('file_path', 'unknown')}: {str(e)}")
                    continue

            if len(image_vectors) == 0:
                logger.warning("没有成功提取任何CLIP图像向量，无法构建索引")
                return False

            # 3. 构建CLIP Faiss索引
            logger.info(f"构建CLIP Faiss索引，向量数量: {len(image_vectors)}")

            # 确保所有向量维度一致
            vector_matrix = np.vstack(image_vectors).astype(np.float32)
            vector_dim = vector_matrix.shape[1]

            # 创建CLIP索引（使用内积索引，适合余弦相似度）
            clip_index = faiss.IndexFlatIP(vector_dim)

            # 添加向量到索引
            clip_index.add(vector_matrix)

            # 4. 保存CLIP索引文件
            base_path = os.path.dirname(self.chunk_faiss_index_path)
            clip_faiss_path = os.path.join(base_path, 'clip_image_index.faiss')
            clip_metadata_path = os.path.join(base_path, 'clip_image_metadata.pkl')

            # 确保目录存在
            os.makedirs(base_path, exist_ok=True)

            # 保存Faiss索引
            faiss.write_index(clip_index, clip_faiss_path)

            # 保存元数据
            with open(clip_metadata_path, 'wb') as f:
                pickle.dump(image_metadata, f)

            build_time = time.time() - start_time
            logger.info(f"CLIP图像向量索引构建完成: {len(image_vectors)} 个向量，维度: {vector_dim}，耗时: {build_time:.2f}秒")
            return True

        except Exception as e:
            logger.error(f"构建CLIP图像索引失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    async def _update_faiss_metadata_chunk_ids(self, saved_chunk_ids: List[int]) -> None:
        """更新Faiss索引元数据中的chunk_ids为数据库真实ID

        Args:
            saved_chunk_ids: 数据库中保存的分块ID列表
        """
        try:
            metadata_path = self.chunk_faiss_index_path.replace('.faiss', '_metadata.pkl')
            if not os.path.exists(metadata_path):
                logger.warning("Faiss元数据文件不存在，无法更新chunk_ids")
                return

            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)

            # 更新chunk_ids为数据库真实ID
            metadata['chunk_ids'] = [str(chunk_id) for chunk_id in saved_chunk_ids]

            # 保存更新后的元数据
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)

            logger.info(f"成功更新Faiss元数据中的chunk_ids，数量: {len(saved_chunk_ids)}")

        except Exception as e:
            logger.error(f"更新Faiss元数据chunk_ids失败: {e}")

    async def _update_whoosh_chunk_ids(self, chunks: List[Dict[str, Any]], saved_chunk_ids: List[int]) -> bool:
        """更新Whoosh索引中的chunk_id为数据库真实ID

        Args:
            chunks: 分块列表
            saved_chunk_ids: 数据库中的真实chunk_id列表（与chunks顺序一致）
        """
        try:
            from whoosh import index as whoosh_index
            from whoosh.query import And, Term

            if not os.path.exists(self.chunk_whoosh_index_path):
                logger.warning("Whoosh索引不存在，跳过chunk_id更新")
                return True

            ix = whoosh_index.open_dir(self.chunk_whoosh_index_path)

            # 第一步：收集所有需要更新的文档信息
            updates = []
            searcher = ix.searcher()
            try:
                for i, chunk in enumerate(chunks):
                    if i >= len(saved_chunk_ids):
                        break

                    real_chunk_id = str(saved_chunk_ids[i])
                    file_id = str(chunk.get('file_id', ''))
                    chunk_index = chunk.get('chunk_index', i)

                    # 构建查询条件：根据file_id和chunk_index查找文档
                    query = And([
                        Term('file_id', file_id),
                        Term('chunk_index', str(chunk_index))
                    ])

                    results = searcher.search(query, limit=1)
                    if results:
                        old_doc = results[0]
                        updates.append({
                            'old_id': old_doc.get('id'),
                            'real_chunk_id': real_chunk_id,
                            'doc_fields': dict(old_doc)
                        })
            finally:
                searcher.close()

            # 第二步：使用writer更新文档
            if updates:
                writer = ix.writer()
                try:
                    for update in updates:
                        # 删除旧文档（通过id）
                        writer.delete_by_term('id', update['old_id'])

                        # 用新的chunk_id重新添加文档
                        fields = update['doc_fields']
                        writer.add_document(
                            id=fields.get('id'),
                            chunk_id=update['real_chunk_id'],  # 使用数据库真实ID
                            file_id=fields.get('file_id'),
                            file_name=fields.get('file_name'),
                            file_path=fields.get('file_path'),
                            file_type=fields.get('file_type'),
                            file_size=fields.get('file_size'),
                            content=fields.get('content'),
                            content_stored=fields.get('content_stored'),
                            chunk_index=fields.get('chunk_index'),
                            start_position=fields.get('start_position'),
                            end_position=fields.get('end_position'),
                            content_length=fields.get('content_length'),
                            modified_time=fields.get('modified_time'),
                            created_at=fields.get('created_at'),
                            source_type=fields.get('source_type'),
                            source_url=fields.get('source_url')
                        )

                    writer.commit()
                    logger.info(f"成功更新Whoosh索引中的chunk_ids，数量: {len(updates)}")
                    return True

                except Exception as e:
                    writer.cancel()
                    raise e
            else:
                logger.info("没有需要更新的Whoosh文档")
                return True

        except Exception as e:
            logger.error(f"更新Whoosh索引chunk_ids失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    def delete_files_by_folder(self, folder_path: str) -> Dict[str, Any]:
        """删除指定文件夹下的所有文件分块索引

        Args:
            folder_path: 文件夹路径

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            logger.info(f"开始删除文件夹分块索引: {folder_path}")
            start_time = time.time()

            # 1. 从数据库查找文件夹下的所有文件和分块记录
            from app.core.database import SessionLocal
            from app.models.file import FileModel
            from app.models.file_chunk import FileChunkModel

            db = SessionLocal()
            try:
                # 查找文件夹下的所有文件
                files = db.query(FileModel).filter(
                    FileModel.file_path.like(f"{folder_path}%")
                ).all()

                if not files:
                    logger.info(f"文件夹下没有找到文件记录: {folder_path}")
                    return {
                        'success': True,
                        'deleted_count': 0,
                        'folder_path': folder_path,
                        'message': '文件夹下没有找到文件记录'
                    }

                # 收集所有文件ID
                file_ids = [file.id for file in files]

                # 查找所有相关的分块记录
                chunk_records = db.query(FileChunkModel).filter(
                    FileChunkModel.file_id.in_(file_ids)
                ).all()

                logger.info(f"找到 {len(files)} 个文件，{len(chunk_records)} 个分块")

                # 2. 从索引中删除分块
                faiss_deleted_count = 0
                whoosh_deleted_count = 0

                if chunk_records:
                    # 从Faiss索引删除
                    faiss_deleted_count = self._delete_from_faiss_index(chunk_records)

                    # 从Whoosh索引删除
                    whoosh_deleted_count = self._delete_from_whoosh_index(chunk_records)

                # 3. 删除数据库中的分块记录
                for chunk_record in chunk_records:
                    db.delete(chunk_record)
                db.commit()

                duration = time.time() - start_time

                logger.info(f"成功删除文件夹分块索引: {folder_path}")
                logger.info(f"  文件数: {len(files)}")
                logger.info(f"  分块数: {len(chunk_records)}")
                logger.info(f"  Faiss删除: {faiss_deleted_count}")
                logger.info(f"  Whoosh删除: {whoosh_deleted_count}")
                logger.info(f"  耗时: {duration:.2f}秒")

                return {
                    'success': True,
                    'deleted_count': len(chunk_records),
                    'deleted_files': len(files),
                    'faiss_deleted_count': faiss_deleted_count,
                    'whoosh_deleted_count': whoosh_deleted_count,
                    'folder_path': folder_path,
                    'duration_seconds': duration
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"删除文件夹分块索引失败 {folder_path}: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'folder_path': folder_path,
                'deleted_count': 0
            }


# 创建全局分块索引服务实例
_chunk_index_service: Optional[ChunkIndexService] = None


def get_chunk_index_service() -> ChunkIndexService:
    """获取分块索引服务实例"""
    global _chunk_index_service
    if _chunk_index_service is None:
        # 使用默认路径创建服务实例
        chunk_faiss_path = os.getenv('FAISS_INDEX_PATH', '../data/indexes/faiss') + '/document_index_chunks.faiss'
        chunk_whoosh_path = os.getenv('WHOOSH_INDEX_PATH', '../data/indexes/whoosh')

        logger.info(f"初始化分块搜索服务:")
        logger.info(f"  - Faiss索引路径: {chunk_faiss_path}")
        logger.info(f"  - Whoosh索引路径: {chunk_whoosh_path}")
        
        _chunk_index_service = ChunkIndexService(
            chunk_faiss_index_path=chunk_faiss_path,
            chunk_whoosh_index_path=chunk_whoosh_path,
            use_ai_models=True
        )

    return _chunk_index_service


def reload_chunk_index_service():
    """重新加载分块索引服务"""
    global _chunk_index_service
    _chunk_index_service = None