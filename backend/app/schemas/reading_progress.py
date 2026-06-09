"""Pydantic schemas for Reading Progress."""
from datetime import datetime
from pydantic import BaseModel


class ReadingProgressBase(BaseModel):
    """Base schema for reading progress."""
    scroll_position: float


class ReadingProgressCreate(ReadingProgressBase):
    """Schema for creating reading progress."""
    session_id: str
    repository_id: int
    filepath: str


class ReadingProgressUpdate(ReadingProgressBase):
    """Schema for updating reading progress."""
    pass


class ReadingProgressResponse(ReadingProgressBase):
    """Schema for reading progress response."""
    id: int
    session_id: str
    repository_id: int
    filepath: str
    last_read_at: datetime
    
    class Config:
        from_attributes = True
