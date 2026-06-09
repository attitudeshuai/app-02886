"""Reading Progress API routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Repository, Document
from app.schemas.reading_progress import (
    ReadingProgressResponse,
    ReadingProgressUpdate,
)
from app.services.reading_progress_service import reading_progress_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reading-progress", tags=["reading-progress"])


@router.get("", response_model=ReadingProgressResponse)
async def get_reading_progress(
    repository_id: int = Query(..., description="Repository ID"),
    filepath: str = Query(..., description="Document file path"),
    session_id: str = Query(..., description="User session ID"),
    db: Session = Depends(get_db),
):
    """Get reading progress for a document."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    doc = db.query(Document).filter(
        Document.repository_id == repository_id,
        Document.filepath == filepath
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    progress = reading_progress_service.get_progress(
        db, session_id, repository_id, filepath
    )
    
    if not progress:
        raise HTTPException(status_code=404, detail="未找到阅读进度")
    
    return progress


@router.put("", response_model=ReadingProgressResponse)
async def update_reading_progress(
    data: ReadingProgressUpdate,
    repository_id: int = Query(..., description="Repository ID"),
    filepath: str = Query(..., description="Document file path"),
    session_id: str = Query(..., description="User session ID"),
    db: Session = Depends(get_db),
):
    """Save or update reading progress for a document."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    doc = db.query(Document).filter(
        Document.repository_id == repository_id,
        Document.filepath == filepath
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if data.scroll_position < 0 or data.scroll_position > 1:
        raise HTTPException(status_code=400, detail="滚动位置必须在 0 到 1 之间")
    
    progress = reading_progress_service.save_progress(
        db, session_id, repository_id, filepath, data.scroll_position
    )
    
    return progress


@router.delete("")
async def reset_reading_progress(
    repository_id: int = Query(..., description="Repository ID"),
    filepath: str = Query(..., description="Document file path"),
    session_id: str = Query(..., description="User session ID"),
    db: Session = Depends(get_db),
):
    """Reset reading progress for a document."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    progress = reading_progress_service.get_progress(
        db, session_id, repository_id, filepath
    )
    
    if not progress:
        raise HTTPException(status_code=404, detail="未找到阅读进度")
    
    reading_progress_service.reset_progress(
        db, session_id, repository_id, filepath
    )
    
    return {"message": "阅读进度已重置"}
