"""
Vector index implementation using Faiss for efficient similarity search.

This module provides a high-level interface for managing vector indices,
including indexing, searching, and CRUD operations for embeddings.
"""

import os
import json
import logging
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("Faiss not installed. Vector search functionality will be limited.")

from core.config import settings

logger = logging.getLogger(__name__)


class VectorIndex:
    """
    Faiss-based vector index for efficient similarity search.

    Supports IndexIVFFlat for large-scale vector search with configurable
    clustering and search parameters.
    """

    def __init__(
        self,
        dimension: int = 768,  # BGE embedding dimension
        nlist: int = 100,  # Number of IVF clusters
        nprobe: int = 10,  # Number of clusters to search
        index_path: Optional[str] = None,
        id_mapping_path: Optional[str] = None
    ):
        """
        Initialize vector index.

        Args:
            dimension: Vector dimension (768 for BGE embeddings)
            nlist: Number of IVF clusters for IndexIVFFlat
            nprobe: Number of clusters to search during query
            index_path: Path to save/load index file
            id_mapping_path: Path to save/load ID mapping file
        """
        if not FAISS_AVAILABLE:
            raise ImportError("Faiss is required for vector search functionality")

        self.dimension = dimension
        self.nlist = nlist
        self.nprobe = nprobe

        # File paths
        self.index_path = index_path or settings.VECTOR_INDEX_PATH
        self.id_mapping_path = id_mapping_path or (
            str(Path(self.index_path).parent / "vector_id_mapping.json")
        )

        # Internal state
        self.index = None
        self.id_mapping: Dict[int, Any] = {}  # Maps vector_id -> metadata
        self.reverse_id_mapping: Dict[Any, int] = {}  # Maps metadata -> vector_id
        self.next_id = 0
        self.is_trained = False

        # Create directories if they don't exist
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.id_mapping_path).parent.mkdir(parents=True, exist_ok=True)

        # Try to load existing index
        self._load_index()

    def _create_index(self) -> None:
        """Create a new IVFFlat index."""
        try:
            # Create a quantizer for the index
            quantizer = faiss.IndexFlatL2(self.dimension)

            # Create IVF index
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist)

            logger.info(f"Created new IVFFlat index with {self.nlist} clusters")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise

    def _train_index(self, vectors: np.ndarray) -> None:
        """
        Train the IVF index with training vectors.

        Args:
            vectors: Training vectors of shape (n_vectors, dimension)
        """
        if len(vectors) < self.nlist:
            logger.warning(
                f"Insufficient training vectors ({len(vectors)}) for {self.nlist} clusters. "
                "Using smaller number of clusters."
            )
            self.nlist = max(1, len(vectors) // 10)
            self._create_index()

        try:
            # Ensure vectors are float32 and properly shaped
            vectors = vectors.astype(np.float32)
            if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
                raise ValueError(f"Training vectors must be shape (n, {self.dimension})")

            # Train the index
            self.index.train(vectors)
            self.is_trained = True
            logger.info(f"Successfully trained index with {len(vectors)} vectors")
        except Exception as e:
            logger.error(f"Error training index: {e}")
            raise

    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: Optional[List[Any]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        Add vectors to the index.

        Args:
            vectors: Vectors to add, shape (n_vectors, dimension)
            ids: Optional list of IDs for the vectors. If None, auto-generated IDs are used.
            metadata: Optional metadata for each vector

        Returns:
            List of vector IDs in the index
        """
        if self.index is None:
            self._create_index()

        # Prepare vectors
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vectors must have dimension {self.dimension}")

        n_vectors = len(vectors)

        # Train index if not trained yet and we have enough vectors
        if not self.is_trained and n_vectors >= self.nlist:
            logger.info("Training index before adding vectors...")
            self._train_index(vectors)

        # Prepare IDs
        if ids is None:
            vector_ids = list(range(self.next_id, self.next_id + n_vectors))
            self.next_id += n_vectors
        else:
            vector_ids = ids

        if len(vector_ids) != n_vectors:
            raise ValueError("Number of IDs must match number of vectors")

        # Add to index (handle untrained index case)
        if not self.is_trained:
            # If index is not trained, temporarily use flat index
            logger.warning("Index not trained, using flat index for initial vectors")
            temp_index = faiss.IndexFlatL2(self.dimension)
            temp_index.add_with_ids(vectors, np.array(vector_ids, dtype=np.int64))

            # If we now have enough vectors, train the main index and migrate
            if self.index.ntotal + n_vectors >= self.nlist:
                all_vectors = np.vstack([self._extract_all_vectors(), vectors]) if self.index.ntotal > 0 else vectors
                self._train_index(all_vectors)

                # Re-add all vectors to the trained index
                if self.index.ntotal > 0:
                    existing_ids = self._get_existing_ids()
                    self.index.reset()
                    self.index.add_with_ids(self._extract_all_vectors(), np.array(existing_ids, dtype=np.int64))

                self.index.add_with_ids(vectors, np.array(vector_ids, dtype=np.int64))
        else:
            # Add vectors to trained index
            self.index.add_with_ids(vectors, np.array(vector_ids, dtype=np.int64))

        # Update ID mappings
        if metadata:
            for i, vector_id in enumerate(vector_ids):
                meta = metadata[i] if i < len(metadata) else {}
                self.id_mapping[vector_id] = meta

                # Create reverse mapping for common metadata fields
                if 'file_id' in meta:
                    self.reverse_id_mapping[f"file_{meta['file_id']}"] = vector_id
                if 'content_id' in meta:
                    self.reverse_id_mapping[f"content_{meta['content_id']}"] = vector_id

        logger.info(f"Added {n_vectors} vectors to index. Total: {self.index.ntotal}")
        return vector_ids

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        nprobe: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector, shape (dimension,)
            k: Number of results to return
            nprobe: Number of clusters to search (overrides default)

        Returns:
            Tuple of (distances, vector_ids, metadata_list)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty")
            return np.array([]), np.array([], dtype=np.int64), []

        # Prepare query vector
        query_vector = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector must have dimension {self.dimension}")

        # Set nprobe for search
        if nprobe is not None:
            original_nprobe = self.index.nprobe
            self.index.nprobe = min(nprobe, self.nlist)
        else:
            original_nprobe = None

        try:
            # Perform search
            distances, indices = self.index.search(query_vector, k)

            # Extract metadata
            metadata_list = []
            for idx in indices[0]:
                if idx != -1 and idx in self.id_mapping:
                    metadata_list.append(self.id_mapping[idx])
                else:
                    metadata_list.append({})

            return distances[0], indices[0], metadata_list

        finally:
            # Restore original nprobe
            if original_nprobe is not None:
                self.index.nprobe = original_nprobe

    def get_vector_count(self) -> int:
        """Get the number of vectors in the index."""
        return self.index.ntotal if self.index else 0

    def is_empty(self) -> bool:
        """Check if the index is empty."""
        return self.index is None or self.index.ntotal == 0

    def delete_vectors(self, vector_ids: List[int]) -> bool:
        """
        Delete vectors from the index.

        Note: Faiss doesn't support direct deletion. This method removes
        vectors from the ID mapping and marks them as deleted.
        """
        try:
            deleted_count = 0
            for vector_id in vector_ids:
                if vector_id in self.id_mapping:
                    # Remove from mappings
                    metadata = self.id_mapping[vector_id]
                    del self.id_mapping[vector_id]

                    # Remove reverse mappings
                    for key, value in list(self.reverse_id_mapping.items()):
                        if value == vector_id:
                            del self.reverse_id_mapping[key]

                    deleted_count += 1

            logger.info(f"Marked {deleted_count} vectors as deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False

    def save_index(self) -> bool:
        """Save the index and ID mappings to disk."""
        try:
            if self.index is not None:
                # Save index
                faiss.write_index(self.index, self.index_path)

                # Save ID mappings
                mapping_data = {
                    'id_mapping': self.id_mapping,
                    'reverse_id_mapping': self.reverse_id_mapping,
                    'next_id': self.next_id,
                    'is_trained': self.is_trained,
                    'nlist': self.nlist,
                    'dimension': self.dimension
                }

                with open(self.id_mapping_path, 'w') as f:
                    json.dump(mapping_data, f, indent=2)

                logger.info(f"Saved index with {self.index.ntotal} vectors")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False

    def _load_index(self) -> bool:
        """Load the index and ID mappings from disk."""
        try:
            # Load index
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded index with {self.index.ntotal} vectors")

                # Load ID mappings
                if os.path.exists(self.id_mapping_path):
                    with open(self.id_mapping_path, 'r') as f:
                        mapping_data = json.load(f)

                    self.id_mapping = mapping_data.get('id_mapping', {})
                    self.reverse_id_mapping = mapping_data.get('reverse_id_mapping', {})
                    self.next_id = mapping_data.get('next_id', 0)
                    self.is_trained = mapping_data.get('is_trained', False)
                    self.nlist = mapping_data.get('nlist', self.nlist)
                    self.dimension = mapping_data.get('dimension', self.dimension)

                    logger.info(f"Loaded {len(self.id_mapping)} ID mappings")

                return True
            return False
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def _extract_all_vectors(self) -> np.ndarray:
        """Extract all vectors from the index (used for re-indexing)."""
        # This is a placeholder - actual implementation would depend on needs
        logger.warning("Vector extraction not fully implemented")
        return np.array([]).reshape(0, self.dimension)

    def _get_existing_ids(self) -> List[int]:
        """Get all existing vector IDs in the index."""
        return list(self.id_mapping.keys())

    def get_metadata_by_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """Get metadata for a vector ID."""
        return self.id_mapping.get(vector_id)

    def get_id_by_metadata(self, file_id: Optional[int] = None, content_id: Optional[str] = None) -> Optional[int]:
        """Get vector ID by metadata."""
        if file_id:
            return self.reverse_id_mapping.get(f"file_{file_id}")
        if content_id:
            return self.reverse_id_mapping.get(f"content_{content_id}")
        return None

    def rebuild_index(
        self,
        vectors: np.ndarray,
        ids: Optional[List[Any]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
        force_retrain: bool = False
    ) -> bool:
        """
        Completely rebuild the index.

        Args:
            vectors: All vectors to include in the new index
            ids: Optional list of IDs for the vectors
            metadata: Optional metadata for each vector
            force_retrain: Force retraining even if index was trained before

        Returns:
            True if rebuild was successful
        """
        try:
            logger.info("Rebuilding vector index...")

            # Reset index
            self.index = None
            self.is_trained = False
            self.id_mapping.clear()
            self.reverse_id_mapping.clear()
            self.next_id = 0

            # Create new index and add all vectors
            self._create_index()
            if vectors:
                self.add_vectors(vectors, ids, metadata)

            logger.info("Vector index rebuilt successfully")
            return True
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        return {
            "total_vectors": self.get_vector_count(),
            "is_trained": self.is_trained,
            "dimension": self.dimension,
            "nlist": self.nlist,
            "id_mappings": len(self.id_mapping),
            "index_path": self.index_path,
            "mapping_path": self.id_mapping_path
        }


# Global vector index instance
vector_index = VectorIndex()