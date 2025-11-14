"""
Full-text Search Manager - High-level interface for full-text search operations.

This module provides a convenient interface for managing full-text search
operations including indexing, searching, and result formatting.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from whoosh.query import Every, Term

from .fulltext_index import FullTextIndex

logger = logging.getLogger(__name__)


class FullTextSearchManager:
    """
    High-level manager for full-text search operations.

    Integrates Whoosh indexing with database models and provides
    convenient methods for common search operations.
    """

    def __init__(
        self,
        index_dir: Optional[str] = None
    ):
        """
        Initialize full-text search manager.

        Args:
            index_dir: Directory to store the index
        """
        self.fulltext_index = FullTextIndex(index_dir=index_dir)

    def index_file_content(
        self,
        file_id: int,
        content: str,
        title: Optional[str] = None,
        filename: str = "",
        file_path: str = "",
        extension: str = "",
        content_type: str = "text",
        file_size: int = 0,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        language: str = "zh"
    ) -> bool:
        """
        Index file content for full-text search.

        Args:
            file_id: File ID
            content: File content to index
            title: Optional title (defaults to filename)
            filename: Filename
            file_path: Full file path
            extension: File extension
            content_type: Content type
            file_size: File size in bytes
            created_at: Creation timestamp
            modified_at: Modification timestamp
            tags: File tags
            language: Content language

        Returns:
            True if successful
        """
        try:
            # Use filename as title if not provided
            if not title:
                title = Path(filename).stem

            # Use current time if timestamps not provided
            now = datetime.utcnow()
            created_at = created_at or now
            modified_at = modified_at or now

            # Add to index
            return self.fulltext_index.add_document(
                doc_id=file_id,
                title=title,
                content=content,
                filename=filename,
                file_path=file_path,
                extension=extension,
                content_type=content_type,
                file_size=file_size,
                created_at=created_at,
                modified_at=modified_at,
                tags=tags,
                language=language,
                file_id=file_id
            )

        except Exception as e:
            logger.error(f"Error indexing file {file_id}: {e}")
            return False

    def index_content_chunks(
        self,
        file_id: int,
        chunks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Index content chunks for large files.

        Args:
            file_id: File ID
            chunks: List of content chunks with 'content' and optionally 'title' keys
            metadata: File metadata

        Returns:
            Number of successfully indexed chunks
        """
        try:
            if metadata is None:
                metadata = {}

            successful = 0

            for i, chunk in enumerate(chunks):
                chunk_data = {
                    'id': f"{file_id}_chunk_{i}",
                    'title': chunk.get('title', f"Chunk {i+1}"),
                    'content': chunk['content'],
                    'filename': metadata.get('filename', ''),
                    'file_path': metadata.get('file_path', ''),
                    'extension': metadata.get('extension', ''),
                    'content_type': metadata.get('content_type', 'text'),
                    'file_size': metadata.get('file_size', 0),
                    'created_at': metadata.get('created_at', datetime.utcnow()),
                    'modified_at': metadata.get('modified_at', datetime.utcnow()),
                    'tags': metadata.get('tags', []),
                    'language': metadata.get('language', 'zh'),
                    'chunk_index': i,
                    'file_id': file_id,
                    'search_boost': 1.0
                }

                if self.fulltext_index.add_document(**chunk_data):
                    successful += 1

            logger.info(f"Indexed {successful} out of {len(chunks)} chunks for file {file_id}")
            return successful

        except Exception as e:
            logger.error(f"Error indexing chunks for file {file_id}: {e}")
            return 0

    def search_files(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        content_type: Optional[str] = None,
        extension: Optional[List[str]] = None,
        file_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        language: str = "zh",
        use_bm25: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search files using full-text search.

        Args:
            query: Search query
            limit: Maximum number of results
            offset: Number of results to skip
            content_type: Filter by content type
            extension: Filter by file extensions
            file_path: Filter by file path (partial match)
            tags: Filter by tags
            language: Search language
            use_bm25: Use BM25 relevance scoring

        Returns:
            List of search results
        """
        try:
            # Build filters
            filters = {}
            if content_type:
                filters['content_type'] = content_type
            if extension:
                filters['extension'] = extension
            if language:
                filters['language'] = language

            # Boost fields for better relevance
            boost_fields = {
                'title': 1.5,    # Title is more important
                'filename': 1.3, # Filename also important
                'content': 1.0   # Content base weight
            }

            # Search
            results = self.fulltext_index.search(
                query_str=query,
                fields=['title', 'content', 'filename'],
                limit=limit,
                offset=offset,
                filters=filters,
                boost_fields=boost_fields,
                use_bm25=use_bm25
            )

            # Apply additional filters if needed
            if file_path:
                filtered_results = []
                for result in results:
                    if file_path.lower() in result['file_path'].lower():
                        filtered_results.append(result)
                results = filtered_results

            if tags:
                filtered_results = []
                for result in results:
                    result_tags = set(result['tags'])
                    filter_tags = set(tags)
                    if filter_tags.issubset(result_tags):
                        filtered_results.append(result)
                results = filtered_results

            return results

        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []

    def search_within_file(
        self,
        file_id: int,
        query: str,
        limit: int = 10,
        language: str = "zh"
    ) -> List[Dict[str, Any]]:
        """
        Search within a specific file.

        Args:
            file_id: File ID to search within
            query: Search query
            limit: Maximum number of results
            language: Search language

        Returns:
            List of search results (chunks)
        """
        try:
            results = self.fulltext_index.search(
                query_str=query,
                fields=['title', 'content'],
                limit=limit,
                filters={'file_id': file_id},
                use_bm25=True
            )

            # Sort by chunk_index if available
            results.sort(key=lambda x: (x.get('chunk_index', 0), x['rank']))

            return results

        except Exception as e:
            logger.error(f"Error searching within file {file_id}: {e}")
            return []

    def get_file_chunks(
        self,
        file_id: int,
        language: str = "zh"
    ) -> List[Dict[str, Any]]:
        """
        Get all indexed chunks for a file.

        Args:
            file_id: File ID
            language: Search language

        Returns:
            List of indexed chunks
        """
        try:
            # Search for all content in the file
            results = self.fulltext_index.search(
                query_str="*",
                fields=['content'],
                limit=1000,
                filters={'file_id': file_id},
                use_bm25=False
            )

            # Sort by chunk_index
            results.sort(key=lambda x: x.get('chunk_index', 0))

            return results

        except Exception as e:
            logger.error(f"Error getting chunks for file {file_id}: {e}")
            return []

    def delete_file_from_index(self, file_id: int) -> bool:
        """
        Delete a file and all its chunks from the index.

        Args:
            file_id: File ID to delete

        Returns:
            True if successful
        """
        try:
            # Delete all documents with this file_id
            return self.fulltext_index.delete_documents_by_field('file_id', file_id)

        except Exception as e:
            logger.error(f"Error deleting file {file_id} from index: {e}")
            return False

    def update_file_access_count(self, file_id: int, increment: int = 1) -> bool:
        """
        Update file access count for relevance scoring.

        Args:
            file_id: File ID
            increment: Amount to increment

        Returns:
            True if successful
        """
        try:
            # Get current chunks for the file
            chunks = self.get_file_chunks(file_id)

            # Update each chunk
            for chunk in chunks:
                doc_id = chunk['doc_id']
                current_count = chunk.get('access_count', 0)
                new_count = current_count + increment

                self.fulltext_index.update_document(
                    doc_id=doc_id,
                    access_count=new_count
                )

            logger.debug(f"Updated access count for {len(chunks)} chunks of file {file_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating access count for file {file_id}: {e}")
            return False

    def suggest_search_terms(
        self,
        prefix: str,
        field: str = 'content',
        limit: int = 10
    ) -> List[str]:
        """
        Get search term suggestions for autocomplete.

        Args:
            prefix: Partial term
            field: Field to search in
            limit: Maximum suggestions

        Returns:
            List of suggested terms
        """
        try:
            return self.fulltext_index.suggest_terms(prefix, field, limit)

        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []

    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive search statistics.

        Returns:
            Statistics dictionary
        """
        try:
            stats = self.fulltext_index.get_index_stats()

            # Add additional manager-specific statistics
            with self.fulltext_index.index.searcher() as searcher:
                # Count documents by type
                type_counts = {}
                extension_counts = {}
                language_counts = {}

                try:
                    # This is a simplified approach
                    # In practice, you might want to use facets or more efficient counting
                    all_docs_query = Every() if Every is not None else Term("id", "*")
                    results = searcher.search(all_docs_query, limit=10000)

                    for hit in results:
                        content_type = hit.get('content_type', 'unknown')
                        extension = hit.get('extension', 'unknown')
                        language = hit.get('language', 'unknown')

                        type_counts[content_type] = type_counts.get(content_type, 0) + 1
                        extension_counts[extension] = extension_counts.get(extension, 0) + 1
                        language_counts[language] = language_counts.get(language, 0) + 1

                    stats['content_type_distribution'] = type_counts
                    stats['extension_distribution'] = extension_counts
                    stats['language_distribution'] = language_counts

                except Exception as e:
                    logger.error(f"Error collecting detailed statistics: {e}")

            return stats

        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {'error': str(e)}

    def optimize_index(self) -> bool:
        """
        Optimize the search index for better performance.

        Returns:
            True if successful
        """
        try:
            logger.info("Optimizing full-text search index...")
            return self.fulltext_index.optimize_index()

        except Exception as e:
            logger.error(f"Error optimizing index: {e}")
            return False

    def rebuild_index_from_metadata(
        self,
        files_metadata: List[Dict[str, Any]]
    ) -> bool:
        """
        Rebuild the entire index from file metadata.

        Args:
            files_metadata: List of file metadata with content

        Returns:
            True if successful
        """
        try:
            logger.info(f"Rebuilding full-text index from {len(files_metadata)} files...")

            # Prepare documents for indexing
            documents = []
            for file_meta in files_metadata:
                doc = {
                    'id': file_meta['id'],
                    'title': file_meta.get('title', Path(file_meta.get('filename', '')).stem),
                    'content': file_meta.get('content_text', ''),
                    'filename': file_meta.get('filename', ''),
                    'file_path': file_meta.get('path', ''),
                    'extension': file_meta.get('extension', ''),
                    'content_type': file_meta.get('content_type', 'text'),
                    'file_size': file_meta.get('size', 0),
                    'created_at': file_meta.get('created_at', datetime.utcnow()),
                    'modified_at': file_meta.get('modified_at', datetime.utcnow()),
                    'tags': file_meta.get('tags', []),
                    'language': file_meta.get('language', 'zh'),
                    'file_id': file_meta['id'],
                    'search_boost': 1.0,
                    'access_count': file_meta.get('access_count', 0)
                }
                documents.append(doc)

            # Rebuild index
            return self.fulltext_index.rebuild_index(documents)

        except Exception as e:
            logger.error(f"Error rebuilding index from metadata: {e}")
            return False

    def save_index(self) -> bool:
        """Save the index to disk."""
        try:
            # Whoosh automatically saves, but we can optimize
            return self.optimize_index()
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False


# Global full-text search manager instance
fulltext_search_manager = FullTextSearchManager()