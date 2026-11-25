"""
文件索引服务

整合文件扫描、元数据提取、内容解析和索引构建功能的主要服务类。
"""

import os
import time
import uuid
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 导入自定义服务
from .file_scanner import FileScanner, FileInfo
from .metadata_extractor import MetadataExtractor
from .content_parser import ContentParser, ParsedContent
from .chunk_index_service import get_chunk_index_service, IndexBuildStopped
from app.core.logging_config import logger

# 导入统一配置
from app.core.config import get_settings
settings = get_settings()


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

        # 存储传统索引路径（用于兼容性，但主要使用分块索引）
        self.traditional_faiss_path = faiss_index_path
        self.traditional_whoosh_path = whoosh_index_path

        # 索引状态
        self.index_status = {
            'is_building': False,
            'last_index_time': None,
            'total_files_indexed': 0,
            'failed_files': 0,
            'indexing_progress': 0.0
        }

        # 任务停止标志
        self._should_stop = False
        self._current_task_id = None

        # 进度写入节流（避免每处理一个文件就写一次数据库）
        self._last_progress_write = 0.0

        # 内存中缓存已索引文件信息（用于变更检测）
        self._indexed_files_cache: Dict[str, FileInfo] = {}

        # 插件加载器引用（用于提取数据源元数据）
        self._plugin_loader = None

    def stop_indexing(self, task_id: Optional[int] = None) -> Dict[str, Any]:
        """停止索引构建任务

        Args:
            task_id: 任务ID，可选

        Returns:
            Dict[str, Any]: 停止结果
        """
        try:
            if self._current_task_id and task_id and self._current_task_id != task_id:
                return {
                    'success': False,
                    'error': f'任务ID不匹配，当前任务: {self._current_task_id}, 请求停止: {task_id}'
                }

            self._should_stop = True
            logger.info(f"索引停止信号已发送，任务ID: {task_id or self._current_task_id}")

            return {
                'success': True,
                'message': '索引任务停止信号已发送',
                'task_id': self._current_task_id
            }

        except Exception as e:
            logger.error(f"停止索引任务失败: {e}")
            return {
                'success': False,
                'error': f'停止索引任务失败: {str(e)}'
            }

    def reset_stop_flag(self, task_id: Optional[int] = None):
        """重置停止标志（开始新任务前调用）

        Args:
            task_id: 新任务ID
        """
        self._should_stop = False
        self._current_task_id = task_id
        logger.debug(f"停止标志已重置，新任务ID: {task_id}")

    def check_stop_signal(self) -> bool:
        """检查是否应该停止当前任务

        Returns:
            bool: 是否应该停止
        """
        if self._should_stop:
            logger.info(f"检测到停止信号，任务ID: {self._current_task_id}")
        return self._should_stop

    def set_plugin_loader(self, plugin_loader):
        """设置插件加载器引用

        Args:
            plugin_loader: 插件加载器实例
        """
        self._plugin_loader = plugin_loader
        logger.debug("插件加载器已设置到索引服务")

    async def _extract_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """提取数据源信息（调用插件）

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            dict: 数据源信息 {source_type, source_url}
        """
        source_info = {"source_type": "filesystem", "source_url": None, "source_id": None}

        if not self._plugin_loader:
            return source_info

        datasource_plugins = self._plugin_loader.get_plugins_by_type("datasource")
        for plugin_id, plugin in datasource_plugins.items():
            try:
                plugin_info = plugin.get_file_source_info(file_path, content)
                if plugin_info.get("source_type"):
                    logger.debug(f"文件 {file_path} 的数据源: {plugin_info.get('source_type')}")
                    return plugin_info
            except Exception as e:
                logger.warning(f"插件 {plugin_id} 获取源信息失败: {e}")
                continue

        return source_info

    def _should_be_chunked(self, content_length: int) -> bool:
        """判断文件是否应该被分块处理

        Args:
            content_length: 文件内容的字符长度

        Returns:
            bool: 是否应该分块
        """
        # 获取分块配置
        from app.core.config import get_settings
        settings = get_settings()
        chunk_size = settings.chunk.default_chunk_size

        # 如果内容长度大于分块大小，则进行分块
        return content_length > chunk_size

    async def load_indexed_files_cache(self):
        """从数据库加载已索引文件到缓存（启动时调用）"""
        try:
            from app.core.database import SessionLocal
            from app.models.file import FileModel

            logger.info("开始从数据库加载索引缓存...")
            start_time = datetime.now()

            db = SessionLocal()
            try:
                # 查询所有已索引的文件
                indexed_files = db.query(FileModel).filter(
                    FileModel.is_indexed == True,
                    FileModel.index_status == 'completed'
                ).all()

                loaded_count = 0
                for file_record in indexed_files:
                    try:
                        # 转换数据库记录为FileInfo对象
                        file_info = FileInfo(
                            path=file_record.file_path,
                            name=file_record.file_name,
                            extension=file_record.file_extension,
                            size=file_record.file_size,
                            created_time=file_record.created_at,
                            modified_time=file_record.modified_at,
                            mime_type=file_record.mime_type or "application/octet-stream",
                            content_hash=file_record.content_hash or ""
                        )

                        # 检查文件是否仍然存在且未被修改
                        if os.path.exists(file_record.file_path):
                            current_stat = os.stat(file_record.file_path)
                            current_modified = datetime.fromtimestamp(current_stat.st_mtime)

                            # 只有当文件未被修改时才加入缓存
                            if current_modified <= file_record.modified_at:
                                self._indexed_files_cache[file_info.path] = file_info
                                loaded_count += 1
                                logger.debug(f"✅ 加载到缓存: {file_record.file_name}")
                            else:
                                logger.debug(f"❌ 文件已修改，跳过: {file_record.file_name}")
                        else:
                            logger.debug(f"❌ 文件不存在，跳过: {file_record.file_path}")

                    except Exception as e:
                        logger.warning(f"加载文件到缓存失败 {file_record.file_path}: {e}")
                        continue

                duration = datetime.now() - start_time
                logger.info(f"索引缓存加载完成: {loaded_count}/{len(indexed_files)} 个文件，耗时 {duration.total_seconds():.2f} 秒")

                # 如果缓存的文件数量远少于数据库记录，可能需要重建索引
                if loaded_count < len(indexed_files) * 0.8:  # 少于80%
                    logger.warning(f"缓存完整性较低 ({loaded_count}/{len(indexed_files)})，建议检查索引状态")

            except Exception as e:
                logger.error(f"从数据库加载索引缓存失败: {e}")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"加载索引缓存时发生异常: {e}")

    async def build_full_index(
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
                # 检查停止信号
                if self.check_stop_signal():
                    return {
                        'success': False,
                        'error': '索引任务已被停止',
                        'stopped': True
                    }

                files = self.scanner.scan_directory(
                    path,
                    recursive=True,
                    include_hidden=False,
                    progress_callback=lambda current, total: self._update_progress(
                        current, total, progress_callback, stage="扫描文件"
                    )
                )
                all_files.extend(files)

                # 检查停止信号
                if self.check_stop_signal():
                    return {
                        'success': False,
                        'error': '索引任务已被停止',
                        'stopped': True
                    }

            if not all_files:
                return {
                    'success': False,
                    'error': '没有找到支持的文件'
                }

            # 扫描完成，设置总文件数到数据库
            self._update_job_progress(0, total_files=len(all_files), force=True)
            logger.info(f"扫描完成，设置总文件数: {self._current_task_id} - {len(all_files)} 个文件, 进度重置为0%")

            # 2. 处理文件并构建文档
            documents = []
            failed_count = 0

            for i, file_info in enumerate(all_files):
                # 检查停止信号
                if self.check_stop_signal():
                    return {
                        'success': False,
                        'error': '索引任务已被停止',
                        'stopped': True
                    }

                try:
                    doc = await self._process_file_to_document(file_info)
                    if doc:
                        documents.append(doc)

                    # 更新进度（解析阶段占 10-70%）
                    self.index_status['indexing_progress'] = 10.0 + ((i + 1) / len(all_files)) * 60.0
                    self._update_job_progress(self.index_status['indexing_progress'])

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

            # 3. 先保存文件数据到数据库（确保分块服务能找到文件记录）
            self.index_status['indexing_progress'] = 70.0
            self._update_job_progress(70.0, force=True)
            if progress_callback:
                progress_callback("保存文件到数据库", 70.0)

            logger.info(f"开始保存 {len(documents)} 个文件到数据库")
            await self._save_files_to_database(all_files, documents)
            logger.info("文件保存到数据库完成")

            # 4. 构建索引（主要使用分块索引）
            self.index_status['indexing_progress'] = 72.0
            self._update_job_progress(72.0, force=True)
            if progress_callback:
                progress_callback("构建分块索引", 72.0)

            chunk_index_success = False
            index_success = False
            index_error = None  # 用于记录详细的错误信息

            try:
                logger.info("开始构建分块索引")
                chunk_index_service = get_chunk_index_service()
                logger.info("分块索引服务获取成功")

                def _chunk_progress(stage: str, percent: float):
                    if progress_callback:
                        progress_callback(stage, percent)
                    self._update_job_progress(percent)

                chunk_index_success = await chunk_index_service.build_chunk_indexes(
                    documents,
                    progress_callback=_chunk_progress,
                    should_stop=self.check_stop_signal,
                    rebuild=True
                )
                logger.info(f"分块索引构建完成，结果: {chunk_index_success}")

                if chunk_index_success:
                    logger.info("分块索引构建成功")
                    index_success = True  # 分块索引成功代表整体成功
                    self._update_job_progress(99.0, force=True)
                else:
                    logger.warning("分块索引构建失败")
                    index_error = "分块索引构建失败：Faiss向量索引或Whoosh全文索引构建失败"

            except IndexBuildStopped:
                logger.info("分块索引构建被用户停止")
                raise
            except Exception as e:
                logger.error(f"构建分块索引失败: {e}")
                import traceback
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                chunk_index_success = False
                index_error = f"分块索引构建异常：{str(e)}"

            # 5. 更新缓存和状态
            if index_success:
                self._update_indexed_files_cache(all_files)
                self.index_status.update({
                    'last_index_time': datetime.now(),
                    'total_files_indexed': len(documents),
                    'failed_files': failed_count,
                    'indexing_progress': 100.0
                })

                # 设置真正的 100%（任务完成）
                self._update_job_progress(100.0, force=True)
                logger.debug(f"任务完成，设置进度为100%: {self._current_task_id}")

            duration = datetime.now() - start_time
            logger.info(f"完整索引构建完成，耗时: {duration.total_seconds():.2f} 秒")

            # 获取分块索引统计信息
            chunk_index_stats = {}
            if chunk_index_success:
                try:
                    chunk_index_service = get_chunk_index_service()
                    chunk_index_stats = chunk_index_service.get_index_stats()
                except Exception as e:
                    logger.warning(f"获取分块索引统计失败: {e}")

            return {
                'success': index_success,
                'total_files_found': len(all_files),
                'documents_indexed': len(documents),
                'failed_files': failed_count,
                'duration_seconds': duration.total_seconds(),
                'chunk_index_stats': chunk_index_stats,
                'chunk_index_success': chunk_index_success,
                'error': index_error  # 添加详细的错误信息
            }

        except IndexBuildStopped:
            logger.info("完整索引构建被用户停止")
            return {
                'success': False,
                'error': '索引任务已被停止',
                'stopped': True
            }
        except Exception as e:
            logger.error(f"构建完整索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.index_status['is_building'] = False

    def _build_full_index_sync(self, scan_paths: List[str]) -> Dict[str, Any]:
        """同步版本的完整索引构建

        Args:
            scan_paths: 要扫描的路径列表

        Returns:
            Dict[str, Any]: 构建结果
        """
        import asyncio

        try:
            # 创建新的事件循环来运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.build_full_index(scan_paths))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"同步构建完整索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def update_incremental_index(
        self,
        scan_paths: List[str],
        progress_callback: Optional[callable] = None
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

            # 初始进度：准备阶段
            if progress_callback:
                progress_callback(0, 100, "准备增量更新")

            chunk_index_service = get_chunk_index_service()
            if not chunk_index_service._chunk_indexes_exist():
                logger.info("索引不存在，执行完整索引构建")
                # 直接同步调用，因为build_full_index会处理异步操作
                return self._build_full_index_sync(scan_paths)

            # 1. 扫描文件变更 (10% 进度)
            if progress_callback:
                progress_callback(10, 100, "扫描文件变更")

            all_changes = []
            all_deletions = []

            # 🔍 调试：检查缓存状态
            logger.info(f"🔍 增量更新调试：当前缓存中有 {len(self._indexed_files_cache)} 个文件")
            if len(self._indexed_files_cache) == 0:
                logger.warning("⚠️ 缓存为空！这将导致全量重建！")
                # 列出缓存中的几个文件路径用于调试
                for i, (path, file_info) in enumerate(list(self._indexed_files_cache.items())[:3]):
                    logger.debug(f"缓存文件 {i+1}: {path}")
            else:
                logger.info("✅ 缓存有数据，进行增量更新")

            for path in scan_paths:
                # 检查停止信号
                if self.check_stop_signal():
                    return {
                        'success': False,
                        'error': '增量索引任务已被停止',
                        'stopped': True
                    }

                logger.info(f"🔍 扫描路径变更: {path}")
                changed_files, deleted_files, _ = self.scanner.scan_changes(
                    path,
                    self._indexed_files_cache,
                    recursive=True,
                    include_hidden=False
                )
                logger.info(f"🔍 扫描结果: 变更文件 {len(changed_files)} 个, 删除文件 {len(deleted_files)} 个")
                if changed_files:
                    for file_info in changed_files[:5]:  # 只显示前5个
                        logger.debug(f"  变更: {file_info.path}")
                all_changes.extend(changed_files)
                all_deletions.extend(deleted_files)

            if not all_changes and not all_deletions:
                # 完成进度
                if progress_callback:
                    progress_callback(100, 100, "没有文件变更")
                return {
                    'success': True,
                    'message': '没有文件变更',
                    'changed_files': 0,
                    'deleted_files': 0
                }

            total_operations = len(all_changes) + len(all_deletions)
            completed_operations = 0

            # 2. 处理变更的文件 (30-70% 进度)
            if progress_callback:
                progress_callback(30, 100, f"处理 {len(all_changes)} 个变更文件")

            new_documents = []
            for i, file_info in enumerate(all_changes):
                # 检查停止信号
                if self.check_stop_signal():
                    return {
                        'success': False,
                        'error': '增量索引任务已被停止',
                        'stopped': True
                    }

                try:
                    doc = await self._process_file_to_document(file_info)
                    if doc:
                        new_documents.append(doc)

                    # 更新处理进度
                    completed_operations += 1
                    if progress_callback and total_operations > 0:
                        progress_pct = 30 + int((completed_operations / total_operations) * 40)
                        progress_callback(progress_pct, 100, f"处理变更文件 {i+1}/{len(all_changes)}")

                except Exception as e:
                    logger.error(f"处理变更文件失败 {file_info.path}: {e}")
                    completed_operations += 1

            # 3. 保存变更文件到数据库（确保获得正确的整数ID）(70% 进度)
            if new_documents:
                if progress_callback:
                    progress_callback(70, 100, f"保存 {len(new_documents)} 个文件到数据库")
                logger.info(f"开始保存 {len(new_documents)} 个变更文件到数据库")
                await self._save_files_to_database(all_changes, new_documents)
                logger.info("变更文件保存到数据库完成")

            # 4. 从索引中删除已删除的文件 (70-90% 进度)
            deleted_count = 0
            if all_deletions:
                if progress_callback:
                    progress_callback(70, 100, f"删除 {len(all_deletions)} 个已删除文件的索引")
                logger.info(f"开始删除 {len(all_deletions)} 个已删除文件的索引")

                for i, deleted_file_path in enumerate(all_deletions):
                    try:
                        # 使用分块索引服务删除文件
                        delete_result = await chunk_index_service.delete_file_from_indexes(deleted_file_path)
                        if delete_result.get('success', False):
                            deleted_count += delete_result.get('deleted_chunks', 0)
                            logger.info(f"成功删除文件索引: {deleted_file_path}")
                        else:
                            logger.error(f"删除文件索引失败: {deleted_file_path}, 错误: {delete_result.get('error')}")
                    except Exception as e:
                        logger.error(f"删除文件索引异常: {deleted_file_path}, 错误: {e}")

                    # 更新删除进度
                    completed_operations += 1
                    if progress_callback and len(all_deletions) > 0:
                        progress_pct = 70 + int((i+1) / len(all_deletions) * 20)
                        progress_callback(progress_pct, 100, f"删除文件索引 {i+1}/{len(all_deletions)}")

                logger.info(f"文件索引删除完成，总共删除了 {deleted_count} 个分块")

            # 5. 添加新文档到索引 (90-95% 进度)
            if new_documents:
                if progress_callback:
                    progress_callback(90, 100, f"构建 {len(new_documents)} 个文档的分块索引")

                def _chunk_progress(stage: str, percent: float):
                    if progress_callback:
                        progress_callback(int(percent), 100, stage)
                    self._update_job_progress(percent)

                chunk_index_success = await chunk_index_service.build_chunk_indexes(
                    new_documents,
                    progress_callback=_chunk_progress,
                    should_stop=self.check_stop_signal,
                    rebuild=False
                )
                if not chunk_index_success:
                    logger.warning("增量更新中构建分块索引失败，但继续处理")

            # 6. 更新缓存 (95-100% 进度)
            if progress_callback:
                progress_callback(95, 100, "更新文件缓存")

            # 从缓存中移除已删除的文件
            for deleted_path in all_deletions:
                self._indexed_files_cache.pop(deleted_path, None)

            # 更新缓存中的变更文件
            for file_info in all_changes:
                self._indexed_files_cache[file_info.path] = file_info

            # 完成进度
            if progress_callback:
                progress_callback(100, 100, "增量索引更新完成")

            duration = datetime.now() - start_time
            logger.info(f"增量索引更新完成，耗时: {duration.total_seconds():.2f} 秒")

            return {
                'success': True,
                'changed_files': len(all_changes),
                'deleted_files': len(all_deletions),
                'new_documents': len(new_documents),
                'duration_seconds': duration.total_seconds(),
                'index_stats': chunk_index_service.get_index_stats()
            }

        except IndexBuildStopped:
            logger.info("增量索引更新被用户停止")
            return {
                'success': False,
                'error': '增量索引任务已被停止',
                'stopped': True
            }
        except Exception as e:
            logger.error(f"增量更新索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _save_files_to_database(self, all_files: List[FileInfo], documents: List[Dict[str, Any]]):
        """保存文件数据到数据库

        Args:
            all_files: 扫描到的所有文件列表
            documents: 处理成功的文档列表
        """
        try:
            from app.core.database import SessionLocal
            from app.models.file import FileModel
            from app.models.file_content import FileContentModel
            import hashlib

            db = SessionLocal()
            try:
                logger.info(f"开始保存 {len(documents)} 个文件到数据库")

                for i, (file_info, document) in enumerate(zip(all_files, documents)):
                    try:
                        # 计算文件内容哈希
                        content_hash = self._calculate_file_hash(file_info.path)

                        # 使用统一配置获取文件类型
                        try:
                            file_type = settings.default.get_file_type(file_info.extension)
                        except ValueError:
                            # 如果扩展名不支持，尝试从mime_type推断
                            file_type = 'unknown'
                            if file_info.mime_type:
                                if 'image' in file_info.mime_type:
                                    file_type = 'image'
                                elif 'video' in file_info.mime_type:
                                    file_type = 'video'
                                elif 'audio' in file_info.mime_type:
                                    file_type = 'audio'
                                elif 'application/pdf' in file_info.mime_type or 'application/' in file_info.mime_type or 'text' in file_info.mime_type:
                                    file_type = 'document'

                        # 跳过不支持的文件类型
                        if file_type == 'unknown':
                            logger.warning(f"跳过不支持的文件类型: {file_info.path} (扩展名: {file_info.extension}, MIME类型: {file_info.mime_type})")
                            continue

                        # 提取数据源信息（调用插件）
                        content_text = document.get('content', '')
                        source_info = await self._extract_source_info(file_info.path, content_text)

                        # 创建或更新文件记录
                        file_record = FileModel(
                            file_path=file_info.path,
                            file_name=file_info.name,
                            file_extension=file_info.extension,
                            file_type=file_type,
                            file_size=file_info.size,
                            created_at=file_info.created_time,
                            modified_at=file_info.modified_time,
                            indexed_at=datetime.now(),
                            content_hash=content_hash,
                            is_indexed=True,
                            is_content_parsed=True,
                            index_status='completed',
                            mime_type=file_info.mime_type,
                            title=document.get('title', ''),
                            author=document.get('author', ''),
                            keywords=document.get('keywords', ''),
                            content_length=len(document.get('content', '')),
                            word_count=len(document.get('content', '').split()),
                            parse_confidence=1.0,  # 简化处理
                            index_quality_score=1.0,
                            needs_reindex=False,
                            # v2.0分块字段（初始值，将在分块处理后更新）
                            is_chunked=self._should_be_chunked(len(document.get('content', ''))),
                            total_chunks=1,
                            chunk_strategy='500+50',
                            avg_chunk_size=500,
                            # 数据源信息（插件提供）
                            source_type=source_info.get("source_type", "filesystem"),
                            source_url=source_info.get("source_url")
                        )

                        # 合并处理：如果文件已存在则更新，否则创建
                        existing_file = db.query(FileModel).filter(
                            FileModel.file_path == file_info.path
                        ).first()

                        if existing_file:
                            # 更新现有记录
                            for key, value in file_record.__dict__.items():
                                if key != 'id' and not key.startswith('_'):
                                    setattr(existing_file, key, value)
                            db_file = existing_file
                        else:
                            # 创建新记录
                            db.add(file_record)
                            db.flush()  # 获取ID
                            db_file = file_record

                        # 更新文档中的id为数据库整数ID，供分块服务使用
                        document['id'] = db_file.id

                        # 创建文件内容记录（即使内容为空也创建，用于跟踪处理状态）
                        content_text = document.get('content', '')
                        has_error = 'error' in document.get('metadata', {})
                        error_message = document.get('metadata', {}).get('error', '') if has_error else ''

                        content_record = FileContentModel(
                            file_id=db_file.id,
                            title=document.get('title', ''),
                            content=content_text,
                            content_length=len(content_text),
                            word_count=len(content_text.split()) if content_text.strip() else 0,
                            language=document.get('language', 'unknown'),
                            confidence=document.get('confidence', 1.0),
                            is_parsed=not has_error,
                            has_error=has_error,
                            error_message=error_message,
                            parsed_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        # 检查是否已存在内容记录
                        existing_content = db.query(FileContentModel).filter(
                            FileContentModel.file_id == db_file.id
                        ).first()

                        if existing_content:
                            # 更新现有记录
                            for key, value in content_record.__dict__.items():
                                if key != 'id' and not key.startswith('_'):
                                    setattr(existing_content, key, value)
                        else:
                            db.add(content_record)

                        # 定期提交以避免内存占用过大
                        if (i + 1) % 10 == 0:
                            db.commit()
                            logger.debug(f"已保存 {i + 1}/{len(documents)} 个文件")

                    except Exception as e:
                        logger.error(f"保存文件到数据库失败 {file_info.path}: {e}")
                        continue

                # 最终提交
                db.commit()
                logger.info(f"成功保存 {len(documents)} 个文件到数据库")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"保存文件数据到数据库失败: {e}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件内容的SHA256哈希值"""
        try:
            import hashlib
            hash_sha256 = hashlib.sha256()

            # 对于大文件，读取前1MB来计算哈希（提高性能）
            with open(file_path, "rb") as f:
                # 读取前1MB
                chunk = f.read(1024 * 1024)
                if chunk:
                    hash_sha256.update(chunk)
                else:
                    # 空文件
                    hash_sha256.update(b'')

            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    async def _process_file_to_document(self, file_info: FileInfo) -> Optional[Dict[str, Any]]:
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

            # 2. 解析内容（支持异步）
            parsed_content = await self.content_parser.parse_content(file_info.path)
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

    def _update_job_progress(self, percent: float, total_files: Optional[int] = None, force: bool = False):
        """按当前任务ID更新索引进度（节流写入数据库）

        Args:
            percent: 总体进度百分比（0-100）
            total_files: 需要同步更新的总文件数
            force: 忽略节流，立即写入
        """
        job_id = self._current_task_id
        if not job_id:
            return

        now = time.time()
        if not force and self._last_progress_write and (now - self._last_progress_write) < 2.0:
            return
        self._last_progress_write = now

        try:
            from app.core.database import SessionLocal
            from app.models.index_job import IndexJobModel

            db = SessionLocal()
            try:
                job = db.query(IndexJobModel).filter(IndexJobModel.id == job_id).first()
                if not job:
                    return
                if total_files is not None and total_files > 0:
                    job.total_files = total_files
                total = job.total_files or 0
                if total > 0:
                    job.processed_files = max(0, min(total, int(total * percent / 100.0)))
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"更新任务进度失败: {e}")

    def _update_progress(self, current: int, total: int, callback: Optional[callable], stage: str = ""):
        """更新扫描阶段进度（扫描阶段占 0-10%）"""
        if total > 0:
            progress = (current / total) * 10.0
            self.index_status['indexing_progress'] = progress

            self._update_job_progress(
                progress,
                total_files=total if stage == "扫描文件" else None
            )

            if callback:
                callback(f"{stage}: {current}/{total}", progress)

    def get_index_status(self) -> Dict[str, Any]:
        """获取索引状态"""
        status = self.index_status.copy()

        # 从数据库获取准确的统计信息，而不是使用内存缓存
        try:
            from app.core.database import get_db
            from app.models.file import FileModel
            from app.schemas.enums import JobStatus
            from app.utils.enum_helpers import get_enum_value

            # 创建数据库会话
            from sqlalchemy.orm import sessionmaker
            from app.core.database import engine
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            with SessionLocal() as db:
                # 从数据库获取准确的文件统计
                total_files_indexed = db.query(FileModel).filter(FileModel.is_indexed == True).count()
                failed_files = db.query(FileModel).filter(FileModel.index_status == get_enum_value(JobStatus.FAILED)).count()

                # 更新状态中的文件数为数据库中的准确数据
                status['total_files_indexed'] = total_files_indexed
                status['failed_files'] = failed_files

                logger.info(f"从数据库获取文件统计: 已索引={total_files_indexed}, 失败={failed_files}, 缓存={len(self._indexed_files_cache)}")

        except Exception as e:
            logger.warning(f"从数据库获取文件统计失败: {e}")

        # 添加分块索引统计
        try:
            chunk_index_service = get_chunk_index_service()
            chunk_stats = chunk_index_service.get_index_stats()
            status.update({
                'chunk_faiss_index_exists': chunk_stats.get('chunk_faiss_index_exists', False),
                'chunk_whoosh_index_exists': chunk_stats.get('chunk_whoosh_index_exists', []),
                'total_chunks_created': chunk_stats.get('total_chunks_created', 0),
                'chunk_faiss_index_size': chunk_stats.get('chunk_faiss_index_size', 0)
            })
        except Exception as e:
            logger.warning(f"获取分块索引统计失败: {e}")

        # 计算索引文件大小
        index_size_bytes = 0
        try:
            # 计算传统索引文件大小
            import os
            from pathlib import Path

            # Faiss 索引文件大小
            if self.traditional_faiss_path and Path(self.traditional_faiss_path).exists():
                for file_path in Path(self.traditional_faiss_path).rglob('*'):
                    if file_path.is_file():
                        index_size_bytes += file_path.stat().st_size

            # Whoosh 索引文件大小
            if self.traditional_whoosh_path and Path(self.traditional_whoosh_path).exists():
                for file_path in Path(self.traditional_whoosh_path).rglob('*'):
                    if file_path.is_file():
                        index_size_bytes += file_path.stat().st_size

            # 添加分块索引大小
            if 'chunk_faiss_index_size' in status:
                index_size_bytes += status['chunk_faiss_index_size']

        except Exception as e:
            logger.warning(f"计算索引文件大小失败: {e}")

        # 添加索引大小到状态中
        status['index_size_bytes'] = index_size_bytes

        # 添加缓存状态信息
        status.update({
            'cached_files_count': len(self._indexed_files_cache)
        })

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

    async def delete_file_from_index(self, file_path: str) -> Dict[str, Any]:
        """从索引中删除文件

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 生成文档ID
            doc_id = self._generate_document_id_from_path(file_path)

            chunk_index_service = get_chunk_index_service()
            delete_result = await chunk_index_service.delete_file_from_indexes(file_path)
            success = delete_result.get('success', False)

            # 从缓存中删除
            self._indexed_files_cache.pop(file_path, None)

            if not success:
                logger.error(f"删除文件失败: {delete_result.get('error', '未知错误')}")
                return {
                    'success': False,
                    'error': delete_result.get('error', '删除文件失败'),
                    'file_path': file_path
                }

            logger.info(f"分块索引服务删除文件成功: {delete_result.get('deleted_chunks', 0)} 个分块")

            return {
                'success': True,
                'file_path': file_path,
                'deleted_chunks': delete_result.get('deleted_chunks', 0),
                'faiss_deleted_count': delete_result.get('faiss_deleted_count', 0),
                'whoosh_deleted_count': delete_result.get('whoosh_deleted_count', 0),
                'duration_seconds': delete_result.get('duration_seconds', 0),
                'message': '文件删除完成'
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
            # 注意：分块索引服务暂不提供备份功能，这里仅记录日志
            logger.info(f"需要备份索引到: {backup_dir}")
            success = True

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

    def clear_index(self) -> Dict[str, Any]:
        """清空所有索引文件

        删除 Faiss 索引文件和 Whoosh 索引目录，用于全量重建索引前清空

        Returns:
            Dict[str, Any]: 清空结果
        """
        try:
            import glob
            import shutil

            logger.info("开始清空索引文件")

            # 1. 删除所有 Faiss 索引文件
            faiss_dir = os.path.dirname(self.traditional_faiss_path)
            if os.path.exists(faiss_dir):
                faiss_files = glob.glob(os.path.join(faiss_dir, "*.index"))
                deleted_faiss = 0
                for faiss_file in faiss_files:
                    try:
                        os.remove(faiss_file)
                        deleted_faiss += 1
                        logger.info(f"已删除 Faiss 索引: {faiss_file}")
                    except Exception as e:
                        logger.warning(f"删除 Faiss 索引失败: {faiss_file}, {e}")
            else:
                deleted_faiss = 0

            # 2. 删除 Whoosh 索引目录
            deleted_whoosh = False
            if os.path.exists(self.traditional_whoosh_path):
                try:
                    shutil.rmtree(self.traditional_whoosh_path)
                    deleted_whoosh = True
                    logger.info(f"已删除 Whoosh 索引: {self.traditional_whoosh_path}")
                except Exception as e:
                    logger.warning(f"删除 Whoosh 索引失败: {e}")
                # 重新创建目录
                try:
                    os.makedirs(self.traditional_whoosh_path, exist_ok=True)
                except Exception as e:
                    logger.warning(f"重新创建 Whoosh 索引目录失败: {e}")

            # 3. 调用分块索引服务的清理方法
            deleted_chunk = 0
            try:
                from app.services.chunk_index_service import get_chunk_index_service
                chunk_service = get_chunk_index_service()
                chunk_service.cleanup_indexes()
                deleted_chunk = 1  # 分块索引清理没有详细计数，标记为已执行
                logger.info("分块索引清理完成")
            except Exception as e:
                logger.warning(f"分块索引清理失败: {e}")

            # 4. 重置内存状态
            self._indexed_files_cache.clear()
            logger.info("已清空索引缓存")

            logger.info(f"索引清空完成: Faiss={deleted_faiss}, Whoosh={deleted_whoosh}, 分块={deleted_chunk}")

            return {
                'success': True,
                'deleted_faiss_count': deleted_faiss,
                'deleted_whoosh': deleted_whoosh,
                'deleted_chunk': deleted_chunk,
                'message': '索引文件已清空'
            }

        except Exception as e:
            logger.error(f"清空索引失败: {e}")
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


# 全局文件索引服务实例（单例模式）
_file_index_service: Optional[FileIndexService] = None


def get_file_index_service() -> FileIndexService:
    """获取文件索引服务实例（单例模式）

    Returns:
        FileIndexService: 文件索引服务实例
    """
    global _file_index_service
    if _file_index_service is None:
        from app.core.config import get_settings
        settings = get_settings()

        faiss_path, whoosh_path = settings.get_index_paths()
        _file_index_service = FileIndexService(
            data_root=settings.index.data_root,
            faiss_index_path=faiss_path,
            whoosh_index_path=whoosh_path,
            use_chinese_analyzer=settings.index.use_chinese_analyzer,
            scanner_config={
                'max_workers': settings.index.scanner_max_workers,
                'max_file_size': settings.index.max_file_size,
                'supported_extensions': set(settings.index.supported_extensions)
            },
            parser_config={
                'max_content_length': settings.index.max_content_length
            }
        )

        logger.info("文件索引服务实例已创建")
    return _file_index_service
