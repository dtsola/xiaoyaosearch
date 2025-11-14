"""
Vector Search Manager - High-level interface for vector search operations.

This module provides a convenient interface for managing vector search
operations including indexing, searching, and metadata management.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from .vector_index import VectorIndex
from .vector_operations import VectorOperations

logger = logging.getLogger(__name__)


class VectorSearchManager:
    """
    High-level manager for vector search operations.

    Integrates vector indexing, search operations, and metadata management
    into a single convenient interface.
    """

    def __init__(
        self,
        dimension: int = 768,
        nlist: int = 100,
        nprobe: int = 10,
        index_path: Optional[str] = None
    ):
        """
        Initialize vector search manager.

        Args:
            dimension: Vector dimension (768 for BGE embeddings)
            nlist: Number of IVF clusters
            nprobe: Number of clusters to search
            index_path: Path to save/load index
        """
        self.vector_index = VectorIndex(
            dimension=dimension,
            nlist=nlist,
            nprobe=nprobe,
            index_path=index_path
        )
        self.dimension = dimension

    def add_file_vector(
        self,
        file_id: int,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Add a vector for a file.

        Args:
            file_id: File ID
            vector: Vector embedding
            metadata: Additional metadata

        Returns:
            Vector ID or None if failed
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}

            metadata.update({
                'file_id': file_id,
                'type': 'file',
                'content_id': f"file_{file_id}"
            })

            # Normalize vector for better search performance
            vector = VectorOperations.normalize_vector(vector)

            # Add to index
            vector_ids = self.vector_index.add_vectors(
                vectors=np.array([vector]),
                ids=None,
                metadata=[metadata]
            )

            if vector_ids:
                logger.info(f"Added vector for file {file_id} with vector ID {vector_ids[0]}")
                return vector_ids[0]
            return None

        except Exception as e:
            logger.error(f"Error adding vector for file {file_id}: {e}")
            return None

    def add_content_vector(
        self,
        content_id: str,
        vector: np.ndarray,
        file_id: Optional[int] = None,
        chunk_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Add a vector for content chunk.

        Args:
            content_id: Unique content identifier
            vector: Vector embedding
            file_id: Optional parent file ID
            chunk_index: Optional chunk index
            metadata: Additional metadata

        Returns:
            Vector ID or None if failed
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}

            metadata.update({
                'content_id': content_id,
                'file_id': file_id,
                'chunk_index': chunk_index,
                'type': 'content',
                'content_ref': f"content_{content_id}"
            })

            # Normalize vector
            vector = VectorOperations.normalize_vector(vector)

            # Add to index
            vector_ids = self.vector_index.add_vectors(
                vectors=np.array([vector]),
                ids=None,
                metadata=[metadata]
            )

            if vector_ids:
                logger.info(f"Added vector for content {content_id} with vector ID {vector_ids[0]}")
                return vector_ids[0]
            return None

        except Exception as e:
            logger.error(f"Error adding vector for content {content_id}: {e}")
            return None

    def add_batch_vectors(
        self,
        vectors_data: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add multiple vectors in batch.

        Args:
            vectors_data: List of dictionaries with 'vector' and 'metadata' keys

        Returns:
            List of vector IDs
        """
        try:
            if not vectors_data:
                return []

            # Prepare vectors and metadata
            vectors = []
            metadata_list = []

            for item in vectors_data:
                vector = item['vector']
                metadata = item.get('metadata', {})

                # Normalize vector
                vector = VectorOperations.normalize_vector(vector)
                vectors.append(vector)
                metadata_list.append(metadata)

            # Add to index
            vectors_array = np.array(vectors)
            vector_ids = self.vector_index.add_vectors(
                vectors=vectors_array,
                ids=None,
                metadata=metadata_list
            )

            logger.info(f"Added batch of {len(vectors)} vectors")
            return vector_ids

        except Exception as e:
            logger.error(f"Error adding batch vectors: {e}")
            return []

    def search_similar(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        content_type: Optional[str] = None,
        file_id: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors with optional filtering.

        Args:
            query_vector: Query vector
            k: Number of results to return
            content_type: Filter by content type ('file', 'content')
            file_id: Filter by file ID
            min_similarity: Minimum similarity threshold

        Returns:
            List of search results with metadata
        """
        try:
            # Normalize query vector
            query_vector = VectorOperations.normalize_vector(query_vector)

            # Perform search
            distances, indices, metadata_list = self.vector_index.search(
                query_vector=query_vector,
                k=k
            )

            results = []
            for i, (distance, idx, metadata) in enumerate(zip(distances, indices, metadata_list)):
                if idx == -1:
                    continue  # Invalid index

                # Apply filters
                if content_type and metadata.get('type') != content_type:
                    continue

                if file_id and metadata.get('file_id') != file_id:
                    continue

                # Convert distance to similarity (assuming L2 distance)
                similarity = 1.0 / (1.0 + distance)

                if min_similarity and similarity < min_similarity:
                    continue

                result = {
                    'vector_id': int(idx),
                    'similarity': float(similarity),
                    'distance': float(distance),
                    'metadata': metadata,
                    'rank': i + 1
                }

                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            return []

    def search_by_file(
        self,
        file_id: int,
        query_vector: np.ndarray,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content within a specific file.

        Args:
            file_id: File ID to search within
            query_vector: Query vector
            k: Number of results

        Returns:
            List of search results
        """
        return self.search_similar(
            query_vector=query_vector,
            k=k,
            content_type='content',
            file_id=file_id
        )

    def get_file_vectors(
        self,
        file_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all vectors associated with a file.

        Args:
            file_id: File ID

        Returns:
            List of vector information
        """
        try:
            # This is a simplified implementation
            # In practice, you might want to maintain additional indices
            results = []
            for vector_id, metadata in self.vector_index.id_mapping.items():
                if metadata.get('file_id') == file_id:
                    results.append({
                        'vector_id': vector_id,
                        'metadata': metadata
                    })

            return results

        except Exception as e:
            logger.error(f"Error getting vectors for file {file_id}: {e}")
            return []

    def delete_file_vectors(self, file_id: int) -> bool:
        """
        Delete all vectors associated with a file.

        Args:
            file_id: File ID

        Returns:
            True if successful
        """
        try:
            # Find all vector IDs associated with the file
            vector_ids = []
            for vector_id, metadata in self.vector_index.id_mapping.items():
                if metadata.get('file_id') == file_id:
                    vector_ids.append(vector_id)

            # Delete vectors
            if vector_ids:
                success = self.vector_index.delete_vectors(vector_ids)
                if success:
                    logger.info(f"Deleted {len(vector_ids)} vectors for file {file_id}")
                return success

            return True  # No vectors to delete

        except Exception as e:
            logger.error(f"Error deleting vectors for file {file_id}: {e}")
            return False

    def delete_content_vector(self, content_id: str) -> bool:
        """
        Delete a specific content vector.

        Args:
            content_id: Content ID

        Returns:
            True if successful
        """
        try:
            vector_id = self.vector_index.get_id_by_metadata(content_id=content_id)
            if vector_id:
                success = self.vector_index.delete_vectors([vector_id])
                if success:
                    logger.info(f"Deleted vector for content {content_id}")
                return success
            return True  # Vector doesn't exist

        except Exception as e:
            logger.error(f"Error deleting vector for content {content_id}: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the vector index.

        Returns:
            Statistics dictionary
        """
        try:
            base_stats = self.vector_index.get_index_stats()

            # Additional statistics
            file_vectors = 0
            content_vectors = 0
            unique_files = set()

            for metadata in self.vector_index.id_mapping.values():
                if metadata.get('type') == 'file':
                    file_vectors += 1
                    unique_files.add(metadata.get('file_id'))
                elif metadata.get('type') == 'content':
                    content_vectors += 1
                    file_id = metadata.get('file_id')
                    if file_id:
                        unique_files.add(file_id)

            base_stats.update({
                'file_vectors': file_vectors,
                'content_vectors': content_vectors,
                'unique_files': len(unique_files),
                'average_vectors_per_file': (
                    content_vectors / len(unique_files) if unique_files else 0
                )
            })

            return base_stats

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def rebuild_index(
        self,
        force_retrain: bool = False
    ) -> bool:
        """
        Rebuild the entire vector index.

        Args:
            force_retrain: Force retraining even if index was trained before

        Returns:
            True if successful
        """
        try:
            logger.info("Rebuilding vector index...")

            # Get all existing data
            if self.vector_index.id_mapping:
                # In a real implementation, you would extract all vectors
                # This is a simplified version that saves current state
                self.save_index()

            logger.info("Vector index rebuild completed")
            return True

        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False

    def save_index(self) -> bool:
        """Save the vector index to disk."""
        return self.vector_index.save_index()

    def optimize_index(self) -> bool:
        """
        Optimize the vector index for better performance.

        Returns:
            True if successful
        """
        try:
            # This would implement index optimization strategies
            # For example, adjusting nprobe based on index size
            total_vectors = self.vector_index.get_vector_count()

            if total_vectors > 10000:
                # Increase nprobe for larger indices
                new_nprobe = min(50, max(10, total_vectors // 1000))
                self.vector_index.nprobe = new_nprobe
                logger.info(f"Optimized index with nprobe={new_nprobe}")

            return True

        except Exception as e:
            logger.error(f"Error optimizing index: {e}")
            return False


# Global vector search manager instance
vector_search_manager = VectorSearchManager()