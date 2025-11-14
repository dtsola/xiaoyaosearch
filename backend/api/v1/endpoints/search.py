"""
Search API endpoints with integrated AI query understanding.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.config import settings
from schemas.search import SearchRequest, SearchResponse, SearchSuggestion, SearchHistory
from services.llm.query_understanding_service import QueryUnderstandingService
from services.llm.models.llm_response import LLMProvider
from dao.search_history_dao import SearchHistoryDAO

logger = logging.getLogger(__name__)

router = APIRouter()

# Global query understanding service
_query_service = None

def get_query_understanding_service():
    """Get or create query understanding service instance."""
    global _query_service
    if _query_service is None and settings.QUERY_UNDERSTANDING_ENABLED:
        _query_service = QueryUnderstandingService(
            provider_type=LLMProvider(settings.LLM_PROVIDER),
            enable_caching=settings.LLM_ENABLE_CACHING
        )
    return _query_service


@router.post("/", response_model=SearchResponse)
async def search(
    search_request: SearchRequest,
    use_ai_understanding: bool = Query(False, description="Whether to use AI query understanding"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for files based on query with optional AI understanding.

    Supports text, voice, and image search modes with hybrid,
    vector, and fulltext search algorithms.

    When AI understanding is enabled, performs query intent analysis,
    keyword extraction, time parsing, and query expansion.
    """
    search_history_dao = SearchHistoryDAO()
    enhanced_query = search_request.query
    ai_analysis_time_ms = 0
    query_understanding_result = None

    # Apply AI query understanding if enabled and available
    if use_ai_understanding and settings.QUERY_UNDERSTANDING_ENABLED:
        try:
            query_service = get_query_understanding_service()
            if query_service:
                import time
                start_time = time.time()

                from services.llm.models.query_intent import QueryAnalysisRequest
                ai_request = QueryAnalysisRequest(
                    query=search_request.query,
                    options={
                        'analyze_intent': settings.QUERY_ANALYZE_INTENT,
                        'extract_keywords': settings.QUERY_EXTRACT_KEYWORDS,
                        'parse_time': settings.QUERY_PARSE_TIME,
                        'expand_query': settings.QUERY_EXPAND_QUERY
                    }
                )

                # Perform AI query analysis
                analysis_result = await query_service.understand_query(ai_request)
                query_understanding_result = analysis_result

                # Enhanced query with AI analysis
                if analysis_result['success'] and 'parsed_query' in analysis_result:
                    parsed_query = analysis_result['parsed_query']

                    # Use expanded query if available
                    if parsed_query.get('expanded_query') and search_request.search_mode == 'hybrid':
                        expanded_terms = parsed_query['expanded_query']
                        if expanded_terms:
                            enhanced_query = f"{search_request.query} {' '.join(expanded_terms[:5])}"  # Limit to top 5 terms

                ai_analysis_time_ms = int((time.time() - start_time) * 1000)
                logger.info(f"AI query understanding completed in {ai_analysis_time_ms}ms")

        except Exception as e:
            logger.warning(f"AI query understanding failed: {str(e)}, using original query")
            # Continue with original query if AI fails

    try:
        # TODO: Integrate with actual search engines (vector, fulltext, etc.)
        # This is where you would call the search service components

        # Save search history
        await search_history_dao.create_history(
            db=db,
            query_text=search_request.query,
            query_type=search_request.query_type,
            search_mode=search_request.search_mode,
            limit=search_request.limit,
            filters_json=search_request.filters.dict() if search_request.filters else None,
            result_count=0,  # TODO: Get actual result count
            search_time_ms=ai_analysis_time_ms
        )

        # Placeholder response - replace with actual search implementation
        return SearchResponse(
            results=[],
            total=0,
            query=search_request.query,
            search_time_ms=ai_analysis_time_ms,
            search_mode=search_request.search_mode,
            filters_applied=search_request.filters.dict() if search_request.filters else None,
            suggestions=[],  # TODO: Get actual suggestions
            query_understanding=query_understanding_result
        )

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions", response_model=List[SearchSuggestion])
async def get_search_suggestions(
    q: str = Query(..., description="Query prefix for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    use_ai_suggestions: bool = Query(True, description="Whether to use AI-powered suggestions"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions based on query prefix.

    Returns historical searches, query completions, and corrections.
    When AI is enabled, provides intelligent query suggestions.
    """
    suggestions = []

    # AI-powered suggestions
    if use_ai_suggestions and settings.QUERY_UNDERSTANDING_ENABLED:
        try:
            query_service = get_query_understanding_service()
            if query_service:
                ai_suggestions = await query_service.get_query_suggestions(q, limit)

                for suggestion in ai_suggestions:
                    suggestions.append(SearchSuggestion(
                        text=suggestion.get('text', ''),
                        type=suggestion.get('type', 'completion'),
                        score=suggestion.get('score', 0.5)
                    ))

        except Exception as e:
            logger.warning(f"AI suggestions failed: {str(e)}")

    # TODO: Add historical search suggestions from database
    # This would involve querying SearchHistoryDAO for similar queries

    return suggestions[:limit]


@router.get("/history", response_model=List[SearchHistory])
async def get_search_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of history items"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's search history.
    """
    try:
        search_history_dao = SearchHistoryDAO()
        history = await search_history_dao.get_recent_searches(db, limit=limit, offset=offset)

        # Convert to response model
        return [
            SearchHistory(
                id=item.id,
                query_text=item.query_text,
                query_type=item.query_type,
                search_mode=item.search_mode,
                result_count=item.result_count,
                search_time_ms=item.search_time_ms,
                created_at=item.created_at
            )
            for item in history
        ]
    except Exception as e:
        logger.error(f"Failed to get search history: {str(e)}")
        return []


@router.delete("/history")
async def clear_search_history(
    db: AsyncSession = Depends(get_db)
):
    """
    Clear user's search history.
    """
    try:
        search_history_dao = SearchHistoryDAO()
        # TODO: Implement actual history clearing logic
        # This might involve deleting all records from search_history table
        return {"message": "Search history cleared"}
    except Exception as e:
        logger.error(f"Failed to clear search history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear search history")


@router.get("/ai-enhanced")
async def ai_enhanced_search_demo(
    query: str = Query(..., description="Query to analyze with AI"),
    db: AsyncSession = Depends(get_db)
):
    """
    Demonstration endpoint for AI query understanding.

    Shows how AI analysis enhances search queries without performing actual search.
    """
    if not settings.QUERY_UNDERSTANDING_ENABLED:
        raise HTTPException(status_code=503, detail="AI query understanding is disabled")

    try:
        query_service = get_query_understanding_service()
        if not query_service:
            raise HTTPException(status_code=503, detail="Query understanding service unavailable")

        from services.llm.models.query_intent import QueryAnalysisRequest

        ai_request = QueryAnalysisRequest(
            query=query,
            options={
                'analyze_intent': True,
                'extract_keywords': True,
                'parse_time': True,
                'expand_query': True
            }
        )

        result = await query_service.understand_query(ai_request)

        return {
            "original_query": query,
            "ai_enhanced": True,
            "analysis": result,
            "message": "This is a demo endpoint. Use POST /search with use_ai_understanding=true for actual search."
        }

    except Exception as e:
        logger.error(f"AI enhanced search demo failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/query-intent-demo")
async def query_intent_demo(
    query: str = Query(..., description="Query to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Demo endpoint for query intent analysis only.
    """
    if not settings.QUERY_UNDERSTANDING_ENABLED:
        raise HTTPException(status_code=503, detail="AI query understanding is disabled")

    try:
        query_service = get_query_understanding_service()
        if not query_service:
            raise HTTPException(status_code=503, detail="Query understanding service unavailable")

        # Test just the intent analyzer component
        from services.llm.query_processors.intent_analyzer import IntentAnalyzer

        # Create a mock provider for demo purposes
        from services.llm.llm_providers.mock_provider import MockProvider
        mock_provider = MockProvider()
        intent_analyzer = IntentAnalyzer(mock_provider)

        intent_result = await intent_analyzer.analyze_intent(query)

        return {
            "query": query,
            "intent": intent_result.dict() if intent_result else None,
            "message": "Intent analysis completed successfully"
        }

    except Exception as e:
        logger.error(f"Query intent demo failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intent analysis failed: {str(e)}")