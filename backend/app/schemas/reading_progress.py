"""Pydantic schemas for reading progress."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReadingProgressSave(BaseModel):
    """Schema for saving reading progress."""
    session_id: str
    repo_id: int
    filepath: str
    scroll_position: int


class ReadingProgressResponse(BaseModel):
    """Schema for reading progress response."""
    session_id: str
    repo_id: int
    filepath: str
    scroll_position: int
    content_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingProgressResult(BaseModel):
    """Schema for progress result returned to client."""
    scroll_position: int
