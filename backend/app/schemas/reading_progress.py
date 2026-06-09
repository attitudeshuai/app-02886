"""Pydantic schemas for ReadingProgress."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReadingProgressUpsert(BaseModel):
    """Schema for creating or updating reading progress."""

    filepath: str = Field(..., min_length=1, max_length=500)
    scroll_ratio: float = Field(0.0, ge=0.0, le=1.0)
    scroll_top: int = Field(0, ge=0)


class ReadingProgressResponse(BaseModel):
    """Schema for reading progress response."""

    id: int
    session_id: str
    repository_id: int
    filepath: str
    scroll_ratio: float
    scroll_top: int
    content_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingProgressGetResponse(BaseModel):
    """Schema returned when querying current progress.

    `progress` will be None when there is no saved progress, or when the
    saved progress was reset because the document content has changed.
    """

    progress: Optional[ReadingProgressResponse] = None
    reset: bool = False
