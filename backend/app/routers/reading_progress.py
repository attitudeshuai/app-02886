"""Reading progress API routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reading_progress import ReadingProgressSave, ReadingProgressResult
from app.services.reading_progress_service import reading_progress_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reading-progress", tags=["reading-progress"])


@router.get("", response_model=ReadingProgressResult)
async def get_reading_progress(
    session_id: str = Query(..., description="User session identifier"),
    repo_id: int = Query(..., description="Repository ID"),
    filepath: str = Query(..., description="Document file path"),
    db: Session = Depends(get_db),
):
    """Get the saved reading progress for a document.

    Returns scroll_position=0 if no progress exists or if the document
    content has changed since the progress was last saved.
    """
    scroll_position = reading_progress_service.get_progress(
        db, session_id=session_id, repo_id=repo_id, filepath=filepath
    )
    return ReadingProgressResult(scroll_position=scroll_position)


@router.put("", response_model=ReadingProgressResult)
async def save_reading_progress(
    data: ReadingProgressSave,
    db: Session = Depends(get_db),
):
    """Save or update reading progress for a document.

    The body includes the session ID, repository ID, file path, and
    current scroll position. The backend also records a content hash so
    that progress is automatically reset when the document changes.
    """
    result = reading_progress_service.save_progress(
        db,
        session_id=data.session_id,
        repo_id=data.repo_id,
        filepath=data.filepath,
        scroll_position=data.scroll_position,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="仓库不存在")

    return ReadingProgressResult(scroll_position=result.scroll_position)
