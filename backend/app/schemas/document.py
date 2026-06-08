"""Pydantic schemas for Document."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    repository_id: int
    filename: str
    filepath: str
    extension: str
    title: Optional[str]
    size: int
    is_indexed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentContent(BaseModel):
    """Schema for document content response."""
    document: DocumentResponse
    content: str


class TreeNode(BaseModel):
    """Schema for file tree node."""
    name: str
    path: str
    type: str  # 'file' or 'directory'
    extension: Optional[str] = None
    children: Optional[list['TreeNode']] = None


# Update forward references
TreeNode.model_rebuild()
