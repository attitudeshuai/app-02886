"""Pydantic schemas for ReadingProgress."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReadingProgressSave(BaseModel):
    session_id: str
    repository_id: int
    filepath: str
    scroll_position: float


class ReadingProgressResponse(BaseModel):
    id: int
    session_id: str
    repository_id: int
    filepath: str
    scroll_position: float
    content_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingProgressGetResponse(ReadingProgressResponse):
    current_content_hash: Optional[str] = None
