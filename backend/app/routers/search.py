"""Search API routes."""
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Repository, Document
from app.schemas.search import SearchResponse, SearchResult
from app.services.document_service import document_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    repo_id: Optional[int] = Query(None, description="Filter by repository ID"),
    db: Session = Depends(get_db)
):
    """Search documents across all repositories."""
    results = []
    
    # Build base query
    query = db.query(Document).join(Repository)
    
    if repo_id:
        query = query.filter(Document.repository_id == repo_id)
    
    # Only search in ready repositories
    query = query.filter(Repository.status == "ready")
    
    documents = query.all()
    
    for doc in documents:
        repo = doc.repository
        
        # Read document content
        content = document_service.get_document_content(repo, doc.filepath)
        if not content:
            continue
        
        # Simple text search
        if q.lower() not in content.lower():
            continue
        
        # Extract highlights (context around matches)
        highlights = extract_highlights(content, q)
        
        # Calculate simple score based on match count
        score = content.lower().count(q.lower())
        
        results.append(SearchResult(
            document=doc,
            repository=repo,
            highlights=highlights[:3],  # Limit to 3 highlights
            score=score
        ))
    
    # Sort by score
    results.sort(key=lambda x: x.score, reverse=True)
    
    return SearchResponse(
        query=q,
        total=len(results),
        results=results[:50]  # Limit to 50 results
    )


def extract_highlights(content: str, query: str, context_size: int = 100) -> list[str]:
    """Extract text snippets containing the query."""
    highlights = []
    content_lower = content.lower()
    query_lower = query.lower()
    
    # Find all occurrences
    start = 0
    while True:
        pos = content_lower.find(query_lower, start)
        if pos == -1:
            break
        
        # Extract context
        ctx_start = max(0, pos - context_size)
        ctx_end = min(len(content), pos + len(query) + context_size)
        
        snippet = content[ctx_start:ctx_end].strip()
        
        # Clean up snippet
        snippet = ' '.join(snippet.split())  # Normalize whitespace
        
        # Add ellipsis if truncated
        if ctx_start > 0:
            snippet = '...' + snippet
        if ctx_end < len(content):
            snippet = snippet + '...'
        
        highlights.append(snippet)
        start = pos + 1
        
        if len(highlights) >= 5:  # Limit highlights per document
            break
    
    return highlights
