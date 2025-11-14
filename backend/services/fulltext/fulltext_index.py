"""
Full-text search index implementation using Whoosh.

This module provides a comprehensive full-text search solution with BM25
relevance scoring and efficient indexing capabilities.
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from whoosh import fields, index, scoring
from whoosh.analysis import StandardAnalyzer
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser.plugins import PrefixPlugin, WildcardPlugin, FuzzyTermPlugin
from whoosh.query import And, Or, Term, Every
from whoosh import writing

from core.config import settings

logger = logging.getLogger(__name__)


class FullTextIndex:
    """
    Full-text search index using Whoosh.

    Provides indexing and searching capabilities with BM25 relevance scoring.
    """

    def __init__(
        self,
        index_dir: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize full-text search index.

        Args:
            index_dir: Directory to store the index
            schema_fields: Custom schema fields configuration
        """
        # Index directory
        self.index_dir = Path(index_dir or settings.FULLTEXT_INDEX_PATH)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Initialize analyzers
        self.chinese_analyzer = StandardAnalyzer(
            stoplist=None,
            minsize=2,
            maxsize=20
        )
        self.standard_analyzer = StandardAnalyzer()

        # Define schema
        self.schema = self._create_schema(schema_fields)

        # Initialize index
        self.index = None
        self._open_index()

    def _create_schema(self, custom_fields: Optional[Dict[str, Any]] = None):
        """Create Whoosh schema for full-text search."""
        schema_dict = {
            # Primary identifier
            'id': fields.NUMERIC(stored=True, unique=True),

            # Content fields with analyzer
            'title': fields.TEXT(
                analyzer=self.chinese_analyzer,
                stored=True,
                phrase=True,
                vector=True
            ),
            'content': fields.TEXT(
                analyzer=self.chinese_analyzer,
                stored=True,
                phrase=True,
                vector=True
            ),
            'filename': fields.TEXT(
                analyzer=self.chinese_analyzer,
                stored=True,
                phrase=True
            ),

            # Metadata fields
            'file_path': fields.TEXT(stored=True, analyzer=self.standard_analyzer),
            'extension': fields.ID(stored=True),
            'content_type': fields.ID(stored=True),
            'file_size': fields.NUMERIC(stored=True),
            'created_at': fields.DATETIME(stored=True),
            'modified_at': fields.DATETIME(stored=True),
            'tags': fields.KEYWORD(stored=True, commas=True),
            'language': fields.ID(stored=True),

            # Search optimization fields
            'chunk_index': fields.NUMERIC(stored=True),
            'file_id': fields.NUMERIC(stored=True),
            'search_boost': fields.NUMERIC(stored=True, default=1.0),
            'access_count': fields.NUMERIC(stored=True, default=0)
        }

        # Add custom fields if provided
        if custom_fields:
            schema_dict.update(custom_fields)

        return fields.Schema(**schema_dict)

    def _open_index(self) -> None:
        """Open existing index or create new one."""
        try:
            # Check if index exists
            exists = False
            try:
                exists = index.exists_in(str(self.index_dir)) if hasattr(index, 'exists_in') else self.index_dir.exists()
            except:
                exists = self.index_dir.exists()

            if exists:
                self.index = index.open_dir(str(self.index_dir))
                logger.info(f"Opened existing full-text index at {self.index_dir}")
            else:
                self.index = index.create_in(str(self.index_dir), self.schema)
                logger.info(f"Created new full-text index at {self.index_dir}")
        except Exception as e:
            logger.error(f"Error opening index: {e}")
            # Try to create a new index if opening failed
            try:
                self.index = index.create_in(str(self.index_dir), self.schema)
                logger.info(f"Created new index after error at {self.index_dir}")
            except Exception as e2:
                logger.error(f"Failed to create new index: {e2}")
                raise

    def add_document(
        self,
        doc_id: int,
        title: str,
        content: str,
        filename: str,
        file_path: str,
        extension: str,
        content_type: str,
        file_size: int,
        created_at: Union[datetime, str],
        modified_at: Union[datetime, str],
        tags: Optional[List[str]] = None,
        language: str = "zh",
        chunk_index: Optional[int] = None,
        file_id: Optional[int] = None,
        search_boost: float = 1.0,
        access_count: int = 0,
        **extra_fields
    ) -> bool:
        """
        Add a document to the full-text index.

        Args:
            doc_id: Unique document identifier
            title: Document title
            content: Document content
            filename: Filename
            file_path: File path
            extension: File extension
            content_type: Content type
            file_size: File size in bytes
            created_at: Creation date
            modified_at: Modification date
            tags: List of tags
            language: Document language
            chunk_index: Chunk index for large documents
            file_id: Parent file ID
            search_boost: Search boost factor
            access_count: Number of accesses

        Returns:
            True if successful
        """
        try:
            writer = self.index.writer()

            # Convert tags list to string if provided
            tags_str = ','.join(tags) if tags else ''

            # Prepare document data
            doc_data = {
                'id': doc_id,
                'title': title,
                'content': content,
                'filename': filename,
                'file_path': file_path,
                'extension': extension,
                'content_type': content_type,
                'file_size': file_size,
                'created_at': created_at,
                'modified_at': modified_at,
                'tags': tags_str,
                'language': language,
                'search_boost': search_boost,
                'access_count': access_count
            }

            # Add optional fields
            if chunk_index is not None:
                doc_data['chunk_index'] = chunk_index
            if file_id is not None:
                doc_data['file_id'] = file_id

            # Add extra fields
            doc_data.update(extra_fields)

            # Add document
            writer.add_document(**doc_data)
            writer.commit()

            logger.debug(f"Added document {doc_id} to full-text index")
            return True

        except Exception as e:
            logger.error(f"Error adding document {doc_id} to full-text index: {e}")
            return False

    def search(
        self,
        query_str: str,
        fields: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        boost_fields: Optional[Dict[str, float]] = None,
        use_bm25: bool = True,
        phrase_search: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search the full-text index.

        Args:
            query_str: Search query string
            fields: Fields to search (default: ['title', 'content'])
            limit: Maximum number of results
            offset: Number of results to skip
            filters: Field filters
            boost_fields: Field boosting factors
            use_bm25: Use BM25 relevance scoring
            phrase_search: Enable phrase search

        Returns:
            List of search results with scores and metadata
        """
        try:
            if not query_str or not query_str.strip():
                return []

            # Default search fields
            if not fields:
                fields = ['title', 'content']

            # Create searcher
            with self.index.searcher() as searcher:
                # Create query parser
                try:
                    if len(fields) == 1:
                        parser = QueryParser(fields[0], self.schema)
                    else:
                        parser = MultifieldParser(fields, self.schema)

                    # Add plugins for enhanced search functionality
                    parser.add_plugin(PrefixPlugin())
                    parser.add_plugin(WildcardPlugin())
                    parser.add_plugin(FuzzyTermPlugin())

                    # Parse query
                    parsed_query = parser.parse(query_str)

                except Exception as parse_error:
                    logger.warning(f"Query parsing error for '{query_str}': {parse_error}, using fallback search")
                    # Fallback to simple term search
                    if len(fields) == 1:
                        parsed_query = Term(fields[0], query_str)
                    else:
                        # Create OR query for multiple fields
                        term_queries = [Term(field, query_str) for field in fields]
                        parsed_query = Or(term_queries)

                # Apply filters
                if filters:
                    filter_terms = []
                    for field, value in filters.items():
                        if isinstance(value, list):
                            filter_terms.append(Or([Term(field, v) for v in value]))
                        else:
                            filter_terms.append(Term(field, value))

                    if filter_terms:
                        parsed_query = And([parsed_query] + filter_terms)

                # Configure BM25 scoring
                if use_bm25:
                    searcher.weighting = scoring.BM25F(
                        title_B=1.5,
                        title_K1=1.2,
                        content_K1=1.2,
                        content_B=0.75
                    )

                # Execute search with compatibility for Whoosh 2.7.4
                try:
                    results = searcher.search(
                        parsed_query,
                        limit=limit,
                        offset=offset,
                        scored=True,
                        terms=True
                    )
                except TypeError:
                    # Fallback for older Whoosh versions without offset parameter
                    results = searcher.search(
                        parsed_query,
                        limit=limit + offset,
                        scored=True,
                        terms=True
                    )
                    # Manually handle offset
                    if offset > 0 and len(results) > offset:
                        results = results[offset:offset + limit]
                    elif offset > 0:
                        results = []

                # Format results
                formatted_results = []
                for hit in results:
                    result_data = {
                        'score': hit.score,
                        'doc_id': hit['id'],
                        'rank': hit.rank + 1,
                    }

                    # Access stored fields
                    for field in ['title', 'content', 'filename', 'file_path', 'extension',
                                'content_type', 'file_size', 'created_at', 'modified_at',
                                'tags', 'language', 'file_id', 'chunk_index']:
                        try:
                            result_data[field] = hit[field]
                        except KeyError:
                            result_data[field] = '' if field in ['title', 'content', 'filename',
                                                               'file_path', 'extension',
                                                               'content_type', 'tags', 'language'] else 0

                    # Handle tags field
                    if result_data.get('tags') and isinstance(result_data['tags'], str):
                        result_data['tags'] = result_data['tags'].split(',')
                    elif not result_data.get('tags'):
                        result_data['tags'] = []

                    # Add matched terms if available
                    if hasattr(hit, 'matched_terms'):
                        try:
                            result_data['matched_terms'] = list(hit.matched_terms())
                        except:
                            result_data['matched_terms'] = []
                    else:
                        result_data['matched_terms'] = []

                    # Add highlights
                    if hit.highlights('title'):
                        result_data['title_highlights'] = hit.highlights('title')
                    if hit.highlights('content'):
                        result_data['content_highlights'] = hit.highlights('content')

                    formatted_results.append(result_data)

                return formatted_results

        except Exception as e:
            logger.error(f"Error searching full-text index: {e}")
            return []

    def update_document(
        self,
        doc_id: int,
        **updates
    ) -> bool:
        """
        Update a document in the index.

        Args:
            doc_id: Document ID to update
            **updates: Fields to update

        Returns:
            True if successful
        """
        try:
            writer = self.index.writer()

            # Delete existing document
            writer.delete_by_term('id', doc_id)

            # Add updated document
            writer.add_document(id=doc_id, **updates)
            writer.commit()

            logger.debug(f"Updated document {doc_id} in full-text index")
            return True

        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False

    def delete_document(self, doc_id: int) -> bool:
        """
        Delete a document from the index.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if successful
        """
        try:
            writer = self.index.writer()
            writer.delete_by_term('id', doc_id)
            writer.commit()

            logger.debug(f"Deleted document {doc_id} from full-text index")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    def delete_documents_by_field(self, field: str, value: Any) -> bool:
        """
        Delete all documents matching a field value.

        Args:
            field: Field name
            value: Field value

        Returns:
            True if successful
        """
        try:
            writer = self.index.writer()
            writer.delete_by_term(field, value)
            writer.commit()

            logger.debug(f"Deleted documents with {field}={value} from full-text index")
            return True

        except Exception as e:
            logger.error(f"Error deleting documents by {field}={value}: {e}")
            return False

    def suggest_terms(
        self,
        prefix: str,
        field: str = 'content',
        limit: int = 10
    ) -> List[str]:
        """
        Get term suggestions for autocomplete.

        Args:
            prefix: Partial term
            field: Field to search in
            limit: Maximum suggestions

        Returns:
            List of suggested terms
        """
        try:
            with self.index.searcher() as searcher:
                from whoosh.analysis import StandardAnalyzer
                analyzer = StandardAnalyzer()

                # Get all terms from the field
                terms = []
                reader = searcher.reader()

                if reader.has_field(field):
                    field_obj = self.schema[field]

                    # Generate suggestions based on prefix
                    for term_bytes in reader.field_terms(field):
                        term_text = term_bytes.decode('utf-8')
                        if term_text.lower().startswith(prefix.lower()):
                            terms.append(term_text)
                            if len(terms) >= limit:
                                break

                return terms

        except Exception as e:
            logger.error(f"Error getting term suggestions: {e}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Statistics dictionary
        """
        try:
            with self.index.searcher() as searcher:
                reader = searcher.reader()

                stats = {
                    'doc_count': reader.doc_count(),
                    'field_names': list(reader.field_names()),
                    'index_size': 0,
                    'last_modified': None
                }

                # Calculate index size
                try:
                    total_size = 0
                    for file_path in self.index_dir.iterdir():
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                    stats['index_size'] = total_size
                except:
                    pass

                return stats

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {'error': str(e)}

    def optimize_index(self) -> bool:
        """
        Optimize the index for better performance.

        Returns:
            True if successful
        """
        try:
            logger.info("Optimizing full-text search index...")
            writer = self.index.writer()
            writer.commit(optimize=True)
            logger.info("Full-text search index optimization completed")
            return True

        except Exception as e:
            logger.error(f"Error optimizing index: {e}")
            return False

    def rebuild_index(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Rebuild the entire index with new documents.

        Args:
            documents: List of documents to index

        Returns:
            True if successful
        """
        try:
            # Clear existing index
            self.index = index.create_in(str(self.index_dir), self.schema)

            # Add all documents
            writer = self.index.writer()
            for doc in documents:
                writer.add_document(**doc)
            writer.commit()

            logger.info(f"Rebuilt index with {len(documents)} documents")
            return True

        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False

    def clear_index(self) -> bool:
        """
        Clear all documents from the index.

        Returns:
            True if successful
        """
        try:
            self.index = index.create_in(str(self.index_dir), self.schema)
            logger.info("Cleared full-text search index")
            return True

        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False


# Global full-text index instance
fulltext_index = FullTextIndex()