"""Pydantic schemas for Repository."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class RepositoryCreate(BaseModel):
    """Schema for creating a repository."""
    url: str
    branch: Optional[str] = "main"
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and clean the repository URL."""
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        # Remove trailing .git if present
        if v.endswith('.git'):
            v = v[:-4]
        return v


class RepositoryUpdate(BaseModel):
    """Schema for updating a repository."""
    branch: Optional[str] = None


class RepositoryResponse(BaseModel):
    """Schema for repository response."""
    id: int
    name: str
    url: str
    description: Optional[str]
    local_path: str
    branch: str
    status: str
    error_message: Optional[str]
    doc_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RepositoryList(BaseModel):
    """Schema for list of repositories."""
    items: list[RepositoryResponse]
    total: int
