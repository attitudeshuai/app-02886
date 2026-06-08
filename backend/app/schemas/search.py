"""Pydantic schemas for Search."""
from pydantic import BaseModel
from app.schemas.document import DocumentResponse
from app.schemas.repository import RepositoryResponse


class SearchResult(BaseModel):
    """Schema for a single search result."""
    document: DocumentResponse
    repository: RepositoryResponse
    highlights: list[str]
    score: float


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    total: int
    results: list[SearchResult]
