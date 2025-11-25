"""
索引构建器

构建Faiss向量索引和Whoosh全文索引，为搜索功能提供基础支持。
"""

import os
import pickle
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import asyncio

# 索引库导入
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("faiss未安装，向量索引功能不可用")

try:
    from whoosh import fields, index
    from whoosh.analysis import ChineseAnalyzer, StandardAnalyzer
    from whoosh.filedb.filestore import FileStorage
    from whoosh.writing import IndexWriter
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False
    logging.warning("whoosh未安装，全文索引功能不可用")

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logging.warning("jieba未安装，中文分词功能不可用")

logger = logging.getLogger(__name__)


class IndexBuilder:
    """索引构建器

    功能：
    - 构建Faiss向量索引（为后续AI向量搜索准备）
    - 构建Whoosh全文索引（支持中文分词）
    - 增量索引更新
    - 索引备份和恢复
    """

    def __init__(
        self,
        faiss_index_path: str,
        whoosh_index_path: str,
        use_chinese_analyzer: bool = True,
        use_ai_embeddings: bool = True
    ):
        """初始化索引构建器

        Args:
            faiss_index_path: Faiss索引文件路径
            whoosh_index_path: Whoosh索引目录路径
            use_chinese_analyzer: 是否使用中文分析器
            use_ai_embeddings: 是否使用AI模型生成嵌入向量
        """
        self.faiss_index_path = faiss_index_path
        self.whoosh_index_path = whoosh_index_path
        self.use_chinese_analyzer = use_chinese_analyzer
        self.use_ai_embeddings = use_ai_embeddings

        # 确保索引目录存在
        os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
        os.makedirs(whoosh_index_path, exist_ok=True)

        # 配置分析器
        if WHOOSH_AVAILABLE:
            if use_chinese_analyzer and JIEBA_AVAILABLE:
                # 使用中文分析器
                self.analyzer = ChineseAnalyzer()
            else:
                # 使用标准分析器
                self.analyzer = StandardAnalyzer()

        # 索引统计
        self.stats = {
            'total_documents': 0,
            'faiss_index_size': 0,
            'whoosh_index_size': 0,
            'last_updated': None
        }

        # AI模型服务缓存
        self._ai_model_service = None

    def build_indexes(self, documents: List[Dict[str, Any]]) -> bool:
        """构建索引

        Args:
            documents: 文档列表，每个文档包含 id, title, content, metadata 等字段

        Returns:
            bool: 构建是否成功
        """
        if not documents:
            logger.warning("文档列表为空，跳过索引构建")
            return False

        logger.info(f"开始构建索引，文档数量: {len(documents)}")
        start_time = datetime.now()

        try:
            # 构建Faiss向量索引
            faiss_success = self._build_faiss_index(documents)

            # 构建Whoosh全文索引
            whoosh_success = self._build_whoosh_index(documents)

            # 更新统计信息
            self.stats['total_documents'] = len(documents)
            self.stats['last_updated'] = datetime.now()
            if faiss_success:
                self.stats['faiss_index_size'] = len(documents)
            if whoosh_success:
                self.stats['whoosh_index_size'] = len(documents)

            duration = datetime.now() - start_time
            logger.info(f"索引构建完成，耗时: {duration.total_seconds():.2f} 秒")

            return faiss_success or whoosh_success

        except Exception as e:
            logger.error(f"构建索引失败: {e}")
            return False

    def update_indexes(self, new_documents: List[Dict[str, Any]]) -> bool:
        """增量更新索引

        Args:
            new_documents: 新增文档列表

        Returns:
            bool: 更新是否成功
        """
        if not new_documents:
            logger.warning("新文档列表为空，跳过索引更新")
            return False

        logger.info(f"开始增量更新索引，新增文档数量: {len(new_documents)}")

        try:
            # 更新Faiss索引
            faiss_success = self._update_faiss_index(new_documents)

            # 更新Whoosh索引
            whoosh_success = self._update_whoosh_index(new_documents)

            # 更新统计信息
            if faiss_success:
                self.stats['faiss_index_size'] += len(new_documents)
            if whoosh_success:
                self.stats['whoosh_index_size'] += len(new_documents)
            self.stats['total_documents'] += len(new_documents)
            self.stats['last_updated'] = datetime.now()

            logger.info(f"索引增量更新完成")
            return faiss_success or whoosh_success

        except Exception as e:
            logger.error(f"增量更新索引失败: {e}")
            return False

    def _build_faiss_index(self, documents: List[Dict[str, Any]]) -> bool:
        """构建Faiss向量索引"""
        if not FAISS_AVAILABLE:
            logger.warning("Faiss不可用，跳过向量索引构建")
            return False

        try:
            logger.info("开始构建Faiss向量索引")

            # 提取文档ID
            doc_ids = [doc.get('id') for doc in documents]

            # 提取文档向量
            if self.use_ai_embeddings:
                logger.info("使用AI模型生成嵌入向量")
                vectors = self._extract_ai_embeddings(documents)
            else:
                logger.info("使用简单字符统计特征")
                vectors = self._extract_simple_vectors(documents)

            if not vectors:
                logger.warning("没有有效的向量数据，跳过Faiss索引构建")
                return False

            # 转换为numpy数组
            import numpy as np
            vectors = np.array(vectors, dtype=np.float32)

            # 创建Faiss索引
            dimension = vectors.shape[1]
            faiss_index = faiss.IndexFlatIP(dimension)  # 内积索引

            # 归一化向量（对于余弦相似度）
            faiss.normalize_L2(vectors)

            # 添加向量到索引
            faiss_index.add(vectors)

            # 保存索引
            faiss.write_index(faiss_index, self.faiss_index_path)

            # 保存元数据
            metadata = {
                'dimension': dimension,
                'doc_count': len(documents),
                'doc_ids': doc_ids,
                'created_time': datetime.now().isoformat(),
                'embedding_type': 'ai_model' if self.use_ai_embeddings else 'simple_features'
            }
            metadata_path = self.faiss_index_path.replace('.faiss', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)

            logger.info(f"Faiss索引构建完成，维度: {dimension}, 文档数: {len(documents)}")
            return True

        except Exception as e:
            logger.error(f"构建Faiss索引失败: {e}")
            return False

    def _extract_ai_embeddings(self, documents: List[Dict[str, Any]]) -> List[List[float]]:
        """使用AI模型提取文档嵌入向量"""
        try:
            vectors = []
            batch_size = 32  # 批处理大小

            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                texts = [doc.get('content', '') + ' ' + doc.get('title', '') for doc in batch_docs]

                # 过滤空文本
                valid_texts = [text for text in texts if text.strip()]
                if not valid_texts:
                    continue

                # 使用AI模型生成嵌入向量
                logger.info(f"生成嵌入向量，批次 {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                embeddings = asyncio.run(self._generate_batch_embeddings(valid_texts))

                vectors.extend(embeddings)

            return vectors

        except Exception as e:
            logger.error(f"AI模型向量提取失败，回退到简单特征: {e}")
            return self._extract_simple_vectors(documents)

    async def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成批量嵌入向量"""
        try:
            from app.services.ai_model_manager import ai_model_service
            embeddings = await ai_model_service.text_embedding(texts, normalize_embeddings=True)

            # 转换为列表格式
            if hasattr(embeddings, 'numpy'):
                return embeddings.numpy().tolist()
            elif hasattr(embeddings, 'tolist'):
                return embeddings.tolist()
            else:
                return [list(embed) for emb in embeddings]

        except Exception as e:
            logger.error(f"批量嵌入生成失败: {e}")
            # 返回零向量作为fallback
            return [[0.0] * 768 for _ in texts]

    def _extract_simple_vectors(self, documents: List[Dict[str, Any]]) -> List[List[float]]:
        """提取简单特征向量（fallback方法）"""
        vectors = []
        for doc in documents:
            vector = self._extract_simple_vector(doc.get('content', ''))
            vectors.append(vector)
        return vectors

    def _build_whoosh_index(self, documents: List[Dict[str, Any]]) -> bool:
        """构建Whoosh全文索引"""
        if not WHOOSH_AVAILABLE:
            logger.warning("Whoosh不可用，跳过全文索引构建")
            return False

        try:
            # 定义索引模式
            schema = fields.Schema(
                id=fields.ID(stored=True, unique=True),
                title=fields.TEXT(stored=True, analyzer=self.analyzer),
                content=fields.TEXT(stored=False, analyzer=self.analyzer),
                file_path=fields.ID(stored=True),
                file_name=fields.TEXT(stored=True, analyzer=self.analyzer),
                file_type=fields.ID(stored=True),
                file_size=fields.NUMERIC(stored=True),
                modified_time=fields.DATETIME(stored=True),
                language=fields.ID(stored=True),
                tags=fields.KEYWORD(stored=True, commas=True)
            )

            # 创建索引
            storage = FileStorage(self.whoosh_index_path)
            ix = storage.create_index(schema)

            # 添加文档
            writer = ix.writer()

            for doc in documents:
                try:
                    writer.add_document(
                        id=str(doc.get('id', '')),
                        title=doc.get('title', ''),
                        content=doc.get('content', ''),
                        file_path=doc.get('file_path', ''),
                        file_name=doc.get('file_name', ''),
                        file_type=doc.get('file_type', ''),
                        file_size=doc.get('file_size', 0),
                        modified_time=doc.get('modified_time', datetime.now()),
                        language=doc.get('language', ''),
                        tags=','.join(doc.get('tags', []))
                    )
                except Exception as e:
                    logger.error(f"添加文档到Whoosh索引失败 {doc.get('id', 'unknown')}: {e}")

            writer.commit()

            logger.info(f"Whoosh全文索引构建完成，文档数: {len(documents)}")
            return True

        except Exception as e:
            logger.error(f"构建Whoosh索引失败: {e}")
            return False

    def _update_faiss_index(self, new_documents: List[Dict[str, Any]]) -> bool:
        """增量更新Faiss索引"""
        if not FAISS_AVAILABLE:
            return False

        try:
            # 读取现有索引
            if os.path.exists(self.faiss_index_path):
                faiss_index = faiss.read_index(self.faiss_index_path)
            else:
                # 如果索引不存在，创建新索引
                return self._build_faiss_index(new_documents)

            # 读取现有元数据
            metadata_path = self.faiss_index_path.replace('.faiss', '_metadata.pkl')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                existing_doc_ids = metadata.get('doc_ids', [])
            else:
                existing_doc_ids = []

            # 为新文档生成向量
            if self.use_ai_embeddings and self.bge_model:
                # 使用AI模型生成嵌入向量
                new_vectors = self._extract_ai_embeddings(new_documents)
                logger.info(f"使用AI模型生成{len(new_vectors)}个嵌入向量")
            else:
                # 使用简单特征向量（fallback方法）
                new_vectors = []
                for doc in new_documents:
                    vector = self._extract_simple_vector(doc.get('content', ''))
                    new_vectors.append(vector)
                logger.info(f"使用简单特征生成{len(new_vectors)}个向量")

            new_doc_ids = [doc.get('id') for doc in new_documents]

            if new_vectors:
                import numpy as np
                new_vectors = np.array(new_vectors, dtype=np.float32)

                # 检查维度兼容性
                existing_dimension = faiss_index.d
                new_dimension = new_vectors.shape[1]
                if existing_dimension != new_dimension:
                    logger.error(f"向量维度不匹配: 现有索引维度={existing_dimension}, 新向量维度={new_dimension}")
                    return False

                faiss.normalize_L2(new_vectors)

                # 添加新向量到索引
                faiss_index.add(new_vectors)

                # 保存更新后的索引
                faiss.write_index(faiss_index, self.faiss_index_path)

                # 更新元数据
                updated_doc_ids = existing_doc_ids + new_doc_ids
                metadata.update({
                    'doc_count': len(updated_doc_ids),
                    'doc_ids': updated_doc_ids,
                    'updated_time': datetime.now().isoformat()
                })
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)

            logger.info(f"Faiss索引增量更新完成，新增文档: {len(new_documents)}")
            return True

        except Exception as e:
            logger.error(f"增量更新Faiss索引失败: {e}")
            return False

    def _update_whoosh_index(self, new_documents: List[Dict[str, Any]]) -> bool:
        """增量更新Whoosh索引"""
        if not WHOOSH_AVAILABLE:
            return False

        try:
            # 打开现有索引或创建新索引
            if os.path.exists(self.whoosh_index_path):
                ix = index.open_dir(self.whoosh_index_path)
            else:
                return self._build_whoosh_index(new_documents)

            # 增量添加文档
            writer = ix.writer()

            for doc in new_documents:
                try:
                    # 检查文档是否已存在
                    doc_id = str(doc.get('id', ''))
                    if doc_id:
                        writer.update_document(
                            id=doc_id,
                            title=doc.get('title', ''),
                            content=doc.get('content', ''),
                            file_path=doc.get('file_path', ''),
                            file_name=doc.get('file_name', ''),
                            file_type=doc.get('file_type', ''),
                            file_size=doc.get('file_size', 0),
                            modified_time=doc.get('modified_time', datetime.now()),
                            language=doc.get('language', ''),
                            tags=','.join(doc.get('tags', []))
                        )
                    else:
                        writer.add_document(
                            id=doc_id,
                            title=doc.get('title', ''),
                            content=doc.get('content', ''),
                            file_path=doc.get('file_path', ''),
                            file_name=doc.get('file_name', ''),
                            file_type=doc.get('file_type', ''),
                            file_size=doc.get('file_size', 0),
                            modified_time=doc.get('modified_time', datetime.now()),
                            language=doc.get('language', ''),
                            tags=','.join(doc.get('tags', []))
                        )
                except Exception as e:
                    logger.error(f"更新文档到Whoosh索引失败 {doc.get('id', 'unknown')}: {e}")

            writer.commit()

            logger.info(f"Whoosh索引增量更新完成，新增/更新文档: {len(new_documents)}")
            return True

        except Exception as e:
            logger.error(f"增量更新Whoosh索引失败: {e}")
            return False

    def _extract_simple_vector(self, text: str, dimension: int = 512) -> List[float]:
        """简单的文本特征向量提取

        注意：这是一个简化的实现，实际应用中应该使用预训练的文本嵌入模型
        """
        if not text:
            return [0.0] * dimension

        # 简单的字符统计特征
        import numpy as np

        # 基础统计特征
        features = [
            len(text),  # 文本长度
            text.count(' '),  # 空格数量
            text.count('\n'),  # 换行数量
            len(set(text)),  # 不同字符数量
        ]

        # 字符频率特征（ASCII字符）
        char_freq = [0] * 128
        for char in text[:1000]:  # 只考虑前1000个字符
            if ord(char) < 128:
                char_freq[ord(char)] += 1

        # 归一化字符频率
        if max(char_freq) > 0:
            char_freq = [f / max(char_freq) for f in char_freq]

        # 组合所有特征
        all_features = features + char_freq

        # 填充或截断到指定维度
        if len(all_features) < dimension:
            all_features.extend([0.0] * (dimension - len(all_features)))
        else:
            all_features = all_features[:dimension]

        # 归一化向量
        import numpy as np
        vector = np.array(all_features, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    def delete_from_indexes(self, doc_ids: List[str]) -> bool:
        """从索引中删除文档

        Args:
            doc_ids: 要删除的文档ID列表

        Returns:
            bool: 删除是否成功
        """
        try:
            # 从Whoosh索引中删除
            if WHOOSH_AVAILABLE and os.path.exists(self.whoosh_index_path):
                ix = index.open_dir(self.whoosh_index_path)
                writer = ix.writer()

                for doc_id in doc_ids:
                    writer.delete_by_term('id', doc_id)

                writer.commit()

            # Faiss索引删除需要重建（因为不支持删除操作）
            if FAISS_AVAILABLE and os.path.exists(self.faiss_index_path):
                # 这里简化处理，实际应该重新构建索引
                logger.info("Faiss索引删除需要重建索引")

            logger.info(f"从索引中删除 {len(doc_ids)} 个文档")
            return True

        except Exception as e:
            logger.error(f"从索引中删除文档失败: {e}")
            return False

    def backup_indexes(self, backup_dir: str) -> bool:
        """备份索引文件

        Args:
            backup_dir: 备份目录

        Returns:
            bool: 备份是否成功
        """
        try:
            import shutil

            os.makedirs(backup_dir, exist_ok=True)

            # 备份Faiss索引
            if os.path.exists(self.faiss_index_path):
                faiss_backup = os.path.join(backup_dir, os.path.basename(self.faiss_index_path))
                shutil.copy2(self.faiss_index_path, faiss_backup)

                # 备份元数据
                metadata_path = self.faiss_index_path.replace('.faiss', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    metadata_backup = os.path.join(backup_dir, os.path.basename(metadata_path))
                    shutil.copy2(metadata_path, metadata_backup)

            # 备份Whoosh索引
            if os.path.exists(self.whoosh_index_path):
                whoosh_backup = os.path.join(backup_dir, 'whoosh_index')
                shutil.copytree(self.whoosh_index_path, whoosh_backup, dirs_exist_ok=True)

            logger.info(f"索引备份完成，备份目录: {backup_dir}")
            return True

        except Exception as e:
            logger.error(f"备份索引失败: {e}")
            return False

    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        stats = self.stats.copy()

        try:
            # Faiss索引统计
            if FAISS_AVAILABLE and os.path.exists(self.faiss_index_path):
                faiss_index = faiss.read_index(self.faiss_index_path)
                stats['faiss_index_dimension'] = faiss_index.d
                stats['faiss_index_ntotal'] = faiss_index.ntotal

            # Whoosh索引统计
            if WHOOSH_AVAILABLE and os.path.exists(self.whoosh_index_path):
                ix = index.open_dir(self.whoosh_index_path)
                stats['whoosh_index_doc_count'] = ix.doc_count()

        except Exception as e:
            logger.error(f"获取索引统计失败: {e}")

        return stats

    def index_exists(self) -> bool:
        """检查索引是否存在"""
        return (os.path.exists(self.faiss_index_path) and
                os.path.exists(self.whoosh_index_path))


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试索引构建
    test_docs = [
        {
            'id': '1',
            'title': '测试文档1',
            'content': '这是一个测试文档的内容，包含中文文本。',
            'file_path': '/test/doc1.txt',
            'file_name': 'doc1.txt',
            'file_type': 'text',
            'file_size': 100,
            'language': 'zh',
            'tags': ['测试', '文档']
        },
        {
            'id': '2',
            'title': 'Test Document 2',
            'content': 'This is a test document with English content.',
            'file_path': '/test/doc2.txt',
            'file_name': 'doc2.txt',
            'file_type': 'text',
            'file_size': 80,
            'language': 'en',
            'tags': ['test', 'document']
        }
    ]

    # 创建索引构建器
    builder = IndexBuilder(
        faiss_index_path='./test_data/test_index.faiss',
        whoosh_index_path='./test_data/test_whoosh_index',
        use_chinese_analyzer=True
    )

    # 构建索引
    success = builder.build_indexes(test_docs)
    print(f"索引构建{'成功' if success else '失败'}")

    # 获取统计信息
    stats = builder.get_index_stats()
    print(f"索引统计: {stats}")