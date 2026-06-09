"""Reading progress API routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reading_progress import ReadingProgressSave, ReadingProgressResponse, ReadingProgressGetResponse
from app.services.reading_progress_service import reading_progress_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reading-progress", tags=["reading-progress"])


@router.put("", response_model=ReadingProgressResponse)
async def save_reading_progress(
    data: ReadingProgressSave,
    db: Session = Depends(get_db),
):
    progress = reading_progress_service.save_progress(
        db=db,
        session_id=data.session_id,
        repository_id=data.repository_id,
        filepath=data.filepath,
        scroll_position=data.scroll_position,
    )
    return progress


@router.get("", response_model=Optional[ReadingProgressGetResponse])
async def get_reading_progress(
    session_id: str = Query(..., description="Session ID"),
    repository_id: int = Query(..., description="Repository ID"),
    filepath: str = Query(..., description="Document file path"),
    db: Session = Depends(get_db),
):
    progress = reading_progress_service.get_progress(
        db=db,
        session_id=session_id,
        repository_id=repository_id,
        filepath=filepath,
    )
    if not progress:
        return None

    current_hash = reading_progress_service.get_current_content_hash(
        db=db,
        repository_id=repository_id,
        filepath=filepath,
    )

    return ReadingProgressGetResponse(
        id=progress.id,
        session_id=progress.session_id,
        repository_id=progress.repository_id,
        filepath=progress.filepath,
        scroll_position=progress.scroll_position,
        content_hash=progress.content_hash,
        created_at=progress.created_at,
        updated_at=progress.updated_at,
        current_content_hash=current_hash,
    )
