from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel

from .config import settings
from .searcher import HybridSearcher

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["search"])

# Initialize searcher
searcher = HybridSearcher(settings.posts_collection_name)


class PostSearchResult(BaseModel):
    id: str
    content: str
    media_urls: List[str]


class SearchResponse(BaseModel):
    results: List[PostSearchResult]
    total: int
    offset: int
    limit: int


@router.get("/search", response_model=SearchResponse)
async def search_posts(
    q: str = Query(..., description="Search query"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(15, ge=1, le=100, description="Number of results to return"),
):
    """Search for posts using hybrid search (dense + sparse vectors)."""
    # Get point IDs from searcher
    point_ids = searcher.search(text=q, offset=offset, limit=limit)

    # Get full point data including payload
    points = searcher.qdrant_client.retrieve(
        collection_name=settings.posts_collection_name, ids=point_ids, with_payload=True
    )

    # Convert to response format
    results = [
        PostSearchResult(
            id=point.id,
            content=point.payload["content"],
            media_urls=point.payload["media_urls"],
        )
        for point in points
    ]

    return SearchResponse(
        results=results, total=len(results), offset=offset, limit=limit
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ml-search"}