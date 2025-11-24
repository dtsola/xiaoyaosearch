"""
文件索引服务

整合文件扫描、元数据提取、内容解析和索引构建功能的主要服务类。
"""

import os
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# 导入自定义服务
from .file_scanner import FileScanner, FileInfo
from .metadata_extractor import MetadataExtractor
from .content_parser import ContentParser, ParsedContent
from .index_builder import IndexBuilder

logger = logging.getLogger(__name__)


class FileIndexService:
    """文件索引服务

    核心功能：
    - 统一的索引管理接口
    - 索引任务调度和监控
    - 增量索引更新
    - 错误处理和恢复机制
    - 性能优化（内存管理、批处理）
    """

    def __init__(
        self,
        data_root: str,
        faiss_index_path: Optional[str] = None,
        whoosh_index_path: Optional[str] = None,
        use_chinese_analyzer: bool = True,
        scanner_config: Optional[Dict[str, Any]] = None,
        parser_config: Optional[Dict[str, Any]] = None
    ):
        """初始化文件索引服务

        Args:
            data_root: 数据根目录
            faiss_index_path: Faiss索引文件路径
            whoosh_index_path: Whoosh索引目录路径
            use_chinese_analyzer: 是否使用中文分析器
            scanner_config: 文件扫描器配置
            parser_config: 内容解析器配置
        """
        self.data_root = Path(data_root)
        self.data_root.mkdir(parents=True, exist_ok=True)

        # 设置索引路径
        if not faiss_index_path:
            faiss_index_path = str(self.data_root / "indexes" / "faiss" / "document_index.faiss")
        if not whoosh_index_path:
            whoosh_index_path = str(self.data_root / "indexes" / "whoosh")

        # 初始化子服务
        self.scanner = FileScanner(**(scanner_config or {}))
        self.metadata_extractor = MetadataExtractor()
        self.content_parser = ContentParser(**(parser_config or {}))
        self.index_builder = IndexBuilder(
            faiss_index_path=faiss_index_path,
            whoosh_index_path=whoosh_index_path,
            use_chinese_analyzer=use_chinese_analyzer
        )

        # 索引状态
        self.index_status = {
            'is_building': False,
            'last_index_time': None,
            'total_files_indexed': 0,
            'failed_files': 0,
            'indexing_progress': 0.0
        }

        # 内存中缓存已索引文件信息（用于变更检测）
        self._indexed_files_cache: Dict[str, FileInfo] = {}

    def build_full_index(
        self,
        scan_paths: List[str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """构建完整索引

        Args:
            scan_paths: 要扫描的路径列表
            progress_callback: 进度回调函数

        Returns:
            Dict[str, Any]: 构建结果
        """
        if self.index_status['is_building']:
            return {
                'success': False,
                'error': '索引正在构建中，请等待完成后再试'
            }

        self.index_status['is_building'] = True
        self.index_status['indexing_progress'] = 0.0

        try:
            logger.info(f"开始构建完整索引，扫描路径: {scan_paths}")
            start_time = datetime.now()

            # 1. 扫描所有文件
            all_files = []
            for path in scan_paths:
                files = self.scanner.scan_directory(
                    path,
                    recursive=True,
                    include_hidden=False,
                    progress_callback=lambda current, total: self._update_progress(
                        current, total, progress_callback, stage="扫描文件"
                    )
                )
                all_files.extend(files)

            if not all_files:
                return {
                    'success': False,
                    'error': '没有找到支持的文件'
                }

            # 2. 处理文件并构建文档
            documents = []
            failed_count = 0

            for i, file_info in enumerate(all_files):
                try:
                    doc = self._process_file_to_document(file_info)
                    if doc:
                        documents.append(doc)

                    # 更新进度
                    self.index_status['indexing_progress'] = 30.0 + (i / len(all_files)) * 50.0
                    if progress_callback:
                        progress_callback(f"处理文件: {file_info.name}",
                                         self.index_status['indexing_progress'])

                except Exception as e:
                    logger.error(f"处理文件失败 {file_info.path}: {e}")
                    failed_count += 1

            if not documents:
                return {
                    'success': False,
                    'error': '没有成功处理的文档'
                }

            # 3. 构建索引
            self.index_status['indexing_progress'] = 80.0
            if progress_callback:
                progress_callback("构建索引", 80.0)

            index_success = self.index_builder.build_indexes(documents)

            # 4. 更新缓存和状态
            if index_success:
                self._update_indexed_files_cache(all_files)
                self.index_status.update({
                    'last_index_time': datetime.now(),
                    'total_files_indexed': len(documents),
                    'failed_files': failed_count,
                    'indexing_progress': 100.0
                })

            duration = datetime.now() - start_time
            logger.info(f"完整索引构建完成，耗时: {duration.total_seconds():.2f} 秒")

            return {
                'success': index_success,
                'total_files_found': len(all_files),
                'documents_indexed': len(documents),
                'failed_files': failed_count,
                'duration_seconds': duration.total_seconds(),
                'index_stats': self.index_builder.get_index_stats()
            }

        except Exception as e:
            logger.error(f"构建完整索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.index_status['is_building'] = False

    def update_incremental_index(
        self,
        scan_paths: List[str]
    ) -> Dict[str, Any]:
        """增量更新索引

        Args:
            scan_paths: 要扫描的路径列表

        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            logger.info(f"开始增量更新索引，扫描路径: {scan_paths}")
            start_time = datetime.now()

            # 1. 检查索引是否存在
            if not self.index_builder.index_exists():
                logger.info("索引不存在，执行完整索引构建")
                return self.build_full_index(scan_paths)

            # 2. 扫描文件变更
            all_changes = []
            all_deletions = []

            for path in scan_paths:
                changed_files, deleted_files, _ = self.scanner.scan_changes(
                    path,
                    self._indexed_files_cache,
                    recursive=True,
                    include_hidden=False
                )
                all_changes.extend(changed_files)
                all_deletions.extend(deleted_files)

            if not all_changes and not all_deletions:
                return {
                    'success': True,
                    'message': '没有文件变更',
                    'changed_files': 0,
                    'deleted_files': 0
                }

            # 3. 处理变更的文件
            new_documents = []
            for file_info in all_changes:
                try:
                    doc = self._process_file_to_document(file_info)
                    if doc:
                        new_documents.append(doc)
                except Exception as e:
                    logger.error(f"处理变更文件失败 {file_info.path}: {e}")

            # 4. 从索引中删除已删除的文件
            if all_deletions:
                deleted_ids = [str(Path(f).stat().st_ino) for f in all_deletions]
                self.index_builder.delete_from_indexes(deleted_ids)

            # 5. 添加新文档到索引
            if new_documents:
                self.index_builder.update_indexes(new_documents)

            # 6. 更新缓存
            # 从缓存中移除已删除的文件
            for deleted_path in all_deletions:
                self._indexed_files_cache.pop(deleted_path, None)

            # 更新缓存中的变更文件
            for file_info in all_changes:
                self._indexed_files_cache[file_info.path] = file_info

            duration = datetime.now() - start_time
            logger.info(f"增量索引更新完成，耗时: {duration.total_seconds():.2f} 秒")

            return {
                'success': True,
                'changed_files': len(all_changes),
                'deleted_files': len(all_deletions),
                'new_documents': len(new_documents),
                'duration_seconds': duration.total_seconds(),
                'index_stats': self.index_builder.get_index_stats()
            }

        except Exception as e:
            logger.error(f"增量更新索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _process_file_to_document(self, file_info: FileInfo) -> Optional[Dict[str, Any]]:
        """将文件信息处理为索引文档

        Args:
            file_info: 文件信息

        Returns:
            Optional[Dict[str, Any]]: 文档数据
        """
        try:
            # 1. 提取元数据
            metadata = self.metadata_extractor.extract_metadata(file_info.path)
            if 'error' in metadata:
                logger.warning(f"提取元数据失败 {file_info.path}: {metadata['error']}")

            # 2. 解析内容
            parsed_content = self.content_parser.parse_content(file_info.path)
            if hasattr(parsed_content, 'error') and parsed_content.error:
                logger.warning(f"解析内容失败 {file_info.path}: {parsed_content.error}")

            # 3. 构建文档
            doc_id = self._generate_document_id(file_info)

            document = {
                'id': doc_id,
                'title': parsed_content.title or file_info.name,
                'content': parsed_content.text,
                'file_path': file_info.path,
                'file_name': file_info.name,
                'file_extension': file_info.extension,
                'file_type': metadata.get('file_type', 'unknown'),
                'file_size': file_info.size,
                'mime_type': file_info.mime_type,
                'created_time': file_info.created_time,
                'modified_time': file_info.modified_time,
                'language': parsed_content.language,
                'encoding': parsed_content.encoding,
                'content_hash': file_info.content_hash,
                'tags': self._extract_tags(metadata),
                'metadata': {
                    'extraction_confidence': parsed_content.confidence,
                    'content_length': len(parsed_content.text),
                    **metadata
                }
            }

            return document

        except Exception as e:
            logger.error(f"处理文件到文档失败 {file_info.path}: {e}")
            return None

    def _generate_document_id(self, file_info: FileInfo) -> str:
        """生成文档ID"""
        # 使用文件路径和修改时间生成唯一ID
        base_id = f"{file_info.path}_{file_info.modified_time.timestamp()}"
        import hashlib
        return hashlib.md5(base_id.encode('utf-8')).hexdigest()

    def _extract_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """从元数据中提取标签"""
        tags = []

        # 从文件类型提取标签
        file_type = metadata.get('file_type', '')
        if file_type:
            tags.append(file_type)

        # 从MIME类型提取标签
        mime_type = metadata.get('mime_type', '')
        if mime_type:
            main_type = mime_type.split('/')[0]
            if main_type and main_type not in tags:
                tags.append(main_type)

        # 从文档属性提取标签
        if metadata.get('keywords'):
            keywords = metadata['keywords'].split(',')
            tags.extend([kw.strip() for kw in keywords if kw.strip()])

        # 从其他字段提取标签
        for field in ['category', 'author']:
            if metadata.get(field):
                tags.append(str(metadata[field]))

        return list(set(tags))  # 去重

    def _update_indexed_files_cache(self, files: List[FileInfo]):
        """更新已索引文件缓存"""
        self._indexed_files_cache.clear()
        for file_info in files:
            self._indexed_files_cache[file_info.path] = file_info

    def _update_progress(self, current: int, total: int, callback: Optional[callable], stage: str = ""):
        """更新进度"""
        if total > 0:
            progress = (current / total) * 30.0  # 扫描阶段占30%
            self.index_status['indexing_progress'] = progress
            if callback:
                callback(f"{stage}: {current}/{total}", progress)

    def get_index_status(self) -> Dict[str, Any]:
        """获取索引状态"""
        status = self.index_status.copy()
        status.update(self.index_builder.get_index_stats())
        return status

    def search_files(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """搜索文件

        注意：这是一个简化的搜索实现，实际应该使用专门的搜索服务

        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            offset: 结果偏移量
            filters: 过滤条件

        Returns:
            Dict[str, Any]: 搜索结果
        """
        try:
            # 这里应该调用专门的搜索服务
            # 目前返回一个模拟结果
            return {
                'success': True,
                'query': query,
                'total_found': 0,
                'results': [],
                'limit': limit,
                'offset': offset,
                'message': '搜索功能需要专门的搜索服务实现'
            }
        except Exception as e:
            logger.error(f"搜索文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file_from_index(self, file_path: str) -> Dict[str, Any]:
        """从索引中删除文件

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 生成文档ID
            doc_id = self._generate_document_id_from_path(file_path)

            # 从索引中删除
            success = self.index_builder.delete_from_indexes([doc_id])

            # 从缓存中删除
            self._indexed_files_cache.pop(file_path, None)

            return {
                'success': success,
                'message': f"文件 {file_path} 已从索引中删除"
            }
        except Exception as e:
            logger.error(f"从索引中删除文件失败 {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_document_id_from_path(self, file_path: str) -> str:
        """从文件路径生成文档ID"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                base_id = f"{file_path}_{stat.st_mtime}"
            else:
                base_id = file_path
            import hashlib
            return hashlib.md5(base_id.encode('utf-8')).hexdigest()
        except Exception:
            import hashlib
            return hashlib.md5(file_path.encode('utf-8')).hexdigest()

    def backup_indexes(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """备份索引

        Args:
            backup_name: 备份名称，如果为None则使用时间戳

        Returns:
            Dict[str, Any]: 备份结果
        """
        try:
            if not backup_name:
                backup_name = f"index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            backup_dir = self.data_root / "backups" / backup_name
            success = self.index_builder.backup_indexes(str(backup_dir))

            return {
                'success': success,
                'backup_path': str(backup_dir),
                'backup_name': backup_name
            }
        except Exception as e:
            logger.error(f"备份索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取支持的文件格式"""
        return {
            'scanner_formats': self.scanner.DEFAULT_SUPPORTED_EXTENSIONS,
            'parser_formats': self.content_parser.get_supported_formats(),
            'extractor_formats': self.metadata_extractor.get_supported_formats()
        }

    def cleanup(self):
        """清理资源"""
        try:
            # 清理缓存
            self._indexed_files_cache.clear()

            # 这里可以添加其他清理逻辑
            logger.info("文件索引服务资源清理完成")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建测试目录和文件
    test_data_dir = Path("./test_data")
    test_data_dir.mkdir(exist_ok=True)

    # 创建测试文件
    test_file = test_data_dir / "test_document.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("这是一个测试文档。\n包含中文内容用于测试索引功能。\nThis is English content.")

    # 创建文件索引服务
    service = FileIndexService(
        data_root="./test_data/index_data",
        use_chinese_analyzer=True
    )

    # 构建完整索引
    result = service.build_full_index(
        scan_paths=["./test_data"],
        progress_callback=lambda message, progress: print(f"进度: {message} - {progress:.1f}%")
    )

    print(f"索引构建结果: {result}")

    # 获取索引状态
    status = service.get_index_status()
    print(f"索引状态: {status}")

    # 获取支持的格式
    formats = service.get_supported_formats()
    print(f"支持的格式: {formats}")