"""
Vector operations utilities for preprocessing and managing embeddings.

This module provides utility functions for common vector operations
including normalization, distance calculations, and batch processing.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorOperations:
    """Utility class for common vector operations."""

    @staticmethod
    def normalize_vector(vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector to unit length (L2 normalization).

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    @staticmethod
    def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
        """
        Normalize a batch of vectors to unit length.

        Args:
            vectors: Input vectors, shape (n_vectors, dimension)

        Returns:
            Normalized vectors
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms

    @staticmethod
    def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            Cosine similarity score (-1 to 1)
        """
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def euclidean_distance(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            Euclidean distance
        """
        return np.linalg.norm(vector1 - vector2)

    @staticmethod
    def cosine_distance(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate cosine distance between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            Cosine distance (0 to 2)
        """
        similarity = VectorOperations.cosine_similarity(vector1, vector2)
        return 1.0 - similarity

    @staticmethod
    def batch_cosine_similarity(query_vector: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query vector and a batch of vectors.

        Args:
            query_vector: Query vector
            vectors: Batch of vectors, shape (n_vectors, dimension)

        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        query_norm = VectorOperations.normalize_vector(query_vector)
        vectors_norm = VectorOperations.normalize_vectors(vectors)

        # Calculate dot products
        similarities = np.dot(vectors_norm, query_norm)
        return similarities

    @staticmethod
    def validate_vector_dimensions(vectors: np.ndarray, expected_dim: int) -> bool:
        """
        Validate that vectors have the expected dimensions.

        Args:
            vectors: Vectors to validate
            expected_dim: Expected dimension

        Returns:
            True if dimensions are valid
        """
        if vectors.ndim == 1:
            return len(vectors) == expected_dim
        elif vectors.ndim == 2:
            return vectors.shape[1] == expected_dim
        else:
            return False

    @staticmethod
    def prepare_vectors(vectors: List[np.ndarray]) -> np.ndarray:
        """
        Prepare a list of vectors into a batch array.

        Args:
            vectors: List of vectors

        Returns:
            Batched vectors as numpy array
        """
        if not vectors:
            return np.array([]).reshape(0, 0)

        # Ensure all vectors have the same dimension
        expected_dim = len(vectors[0])
        for i, vec in enumerate(vectors):
            if len(vec) != expected_dim:
                raise ValueError(f"Vector {i} has dimension {len(vec)}, expected {expected_dim}")

        return np.array(vectors, dtype=np.float32)

    @staticmethod
    def chunk_vectors(vectors: np.ndarray, chunk_size: int) -> List[np.ndarray]:
        """
        Split a large batch of vectors into smaller chunks.

        Args:
            vectors: Input vectors
            chunk_size: Size of each chunk

        Returns:
            List of vector chunks
        """
        if len(vectors) <= chunk_size:
            return [vectors]

        chunks = []
        for i in range(0, len(vectors), chunk_size):
            chunk = vectors[i:i + chunk_size]
            chunks.append(chunk)

        return chunks

    @staticmethod
    def compute_vector_statistics(vectors: np.ndarray) -> Dict[str, Any]:
        """
        Compute statistics about a batch of vectors.

        Args:
            vectors: Input vectors

        Returns:
            Dictionary with vector statistics
        """
        if len(vectors) == 0:
            return {
                "count": 0,
                "dimension": 0,
                "mean_norm": 0.0,
                "std_norm": 0.0,
                "mean": None,
                "std": None
            }

        # Compute norms
        norms = np.linalg.norm(vectors, axis=1)

        stats = {
            "count": len(vectors),
            "dimension": vectors.shape[1],
            "mean_norm": float(np.mean(norms)),
            "std_norm": float(np.std(norms)),
            "min_norm": float(np.min(norms)),
            "max_norm": float(np.max(norms)),
            "mean": vectors.mean(axis=0).tolist(),
            "std": vectors.std(axis=0).tolist()
        }

        return stats

    @staticmethod
    def filter_vectors_by_threshold(
        vectors: np.ndarray,
        threshold: float,
        metric: str = "norm"
    ) -> np.ndarray:
        """
        Filter vectors based on a threshold metric.

        Args:
            vectors: Input vectors
            threshold: Threshold value
            metric: Metric to filter by ("norm", "mean", "variance")

        Returns:
            Filtered vectors
        """
        if len(vectors) == 0:
            return vectors

        if metric == "norm":
            norms = np.linalg.norm(vectors, axis=1)
            mask = norms >= threshold
        elif metric == "mean":
            means = np.mean(vectors, axis=1)
            mask = np.abs(means) >= threshold
        elif metric == "variance":
            variances = np.var(vectors, axis=1)
            mask = variances >= threshold
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        return vectors[mask]

    @staticmethod
    def reduce_dimensionality_pca(
        vectors: np.ndarray,
        target_dim: int,
        fit_vectors: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, Any]:
        """
        Reduce vector dimensionality using PCA.

        Args:
            vectors: Vectors to reduce
            target_dim: Target dimension
            fit_vectors: Vectors to fit PCA on (if different from vectors)

        Returns:
            Tuple of (reduced_vectors, pca_transformer)
        """
        try:
            from sklearn.decomposition import PCA

            # Create PCA transformer
            pca = PCA(n_components=target_dim)

            # Fit PCA
            if fit_vectors is not None:
                pca.fit(fit_vectors)
            else:
                pca.fit(vectors)

            # Transform vectors
            reduced_vectors = pca.transform(vectors)

            return reduced_vectors, pca
        except ImportError:
            logger.warning("sklearn not available for PCA dimensionality reduction")
            return vectors, None
        except Exception as e:
            logger.error(f"Error in PCA dimensionality reduction: {e}")
            return vectors, None

    @staticmethod
    def save_vectors(vectors: np.ndarray, file_path: str, ids: Optional[List[Any]] = None) -> bool:
        """
        Save vectors to a file.

        Args:
            vectors: Vectors to save
            file_path: Output file path
            ids: Optional IDs for the vectors

        Returns:
            True if save was successful
        """
        try:
            data = {
                "vectors": vectors.tolist(),
                "shape": vectors.shape,
                "ids": ids
            }

            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.json':
                import json
                with open(file_path, 'w') as f:
                    json.dump(data, f)
            elif file_ext == '.npy':
                np.save(file_path, vectors)
                if ids:
                    ids_path = file_path.replace('.npy', '_ids.json')
                    with open(ids_path, 'w') as f:
                        import json
                        json.dump(ids, f)
            else:
                # Use pickle for other formats
                with open(file_path, 'wb') as f:
                    import pickle
                    pickle.dump(data, f)

            logger.info(f"Saved {len(vectors)} vectors to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving vectors: {e}")
            return False

    @staticmethod
    def load_vectors(file_path: str) -> Tuple[np.ndarray, Optional[List[Any]]]:
        """
        Load vectors from a file.

        Args:
            file_path: Input file path

        Returns:
            Tuple of (vectors, ids)
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.npy':
                vectors = np.load(file_path)
                # Try to load corresponding IDs
                ids_path = file_path.replace('.npy', '_ids.json')
                ids = None
                if Path(ids_path).exists():
                    with open(ids_path, 'r') as f:
                        import json
                        ids = json.load(f)
                return vectors, ids
            elif file_ext == '.json':
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                vectors = np.array(data["vectors"], dtype=np.float32)
                ids = data.get("ids")
                return vectors, ids
            else:
                # Use pickle for other formats
                with open(file_path, 'rb') as f:
                    import pickle
                    data = pickle.load(f)
                vectors = np.array(data["vectors"], dtype=np.float32)
                ids = data.get("ids")
                return vectors, ids

        except Exception as e:
            logger.error(f"Error loading vectors from {file_path}: {e}")
            return np.array([]).reshape(0, 0), None

    @staticmethod
    def merge_vector_batches(vector_batches: List[np.ndarray]) -> np.ndarray:
        """
        Merge multiple batches of vectors.

        Args:
            vector_batches: List of vector batches

        Returns:
            Merged vectors
        """
        if not vector_batches:
            return np.array([]).reshape(0, 0)

        # Filter out empty batches
        non_empty_batches = [batch for batch in vector_batches if len(batch) > 0]
        if not non_empty_batches:
            return np.array([]).reshape(0, 0)

        # Check dimension consistency
        expected_dim = non_empty_batches[0].shape[1]
        for i, batch in enumerate(non_empty_batches):
            if batch.shape[1] != expected_dim:
                raise ValueError(f"Batch {i} has dimension {batch.shape[1]}, expected {expected_dim}")

        return np.vstack(non_empty_batches)