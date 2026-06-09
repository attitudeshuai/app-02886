"""Reading progress API routes.

Provides RESTful endpoints to record and restore a session's last reading
position inside a repository document. The session identifier is carried
in the `X-Session-Id` request header so it does not appear in URLs / logs.
"""
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Document, Repository
from app.schemas.reading_progress import (
    ReadingProgressGetResponse,
    ReadingProgressResponse,
    ReadingProgressUpsert,
)
from app.services.reading_progress_service import reading_progress_service

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/repositories/{repo_id}/reading-progress",
    tags=["reading-progress"],
)


def get_session_id(
    x_session_id: str = Header(
        ...,
        alias="X-Session-Id",
        min_length=1,
        max_length=128,
        description="客户端会话标识",
    ),
) -> str:
    """Extract and validate the session id from the X-Session-Id header."""
    session_id = x_session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="缺少会话标识")
    return session_id


def _get_repository_and_document(
    repo_id: int,
    filepath: str,
    db: Session,
) -> Repository:
    """Fetch a repository and verify the document exists."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")

    doc = (
        db.query(Document)
        .filter(Document.repository_id == repo_id, Document.filepath == filepath)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return repo


@router.get("", response_model=ReadingProgressGetResponse)
async def get_reading_progress(
    repo_id: int,
    filepath: str = Query(..., min_length=1, max_length=500, description="文档相对路径"),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db),
):
    """Get the saved reading progress for a session + document.

    If the document content has changed since the progress was saved, the
    response indicates a reset (the stored row is left untouched, see
    `ReadingProgressService.get_progress`).
    """
    repo = _get_repository_and_document(repo_id, filepath, db)
    progress, reset = reading_progress_service.get_progress(
        db=db,
        repository=repo,
        session_id=session_id,
        filepath=filepath,
    )
    return ReadingProgressGetResponse(progress=progress, reset=reset)


@router.put("", response_model=ReadingProgressResponse)
async def upsert_reading_progress(
    repo_id: int,
    data: ReadingProgressUpsert,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db),
):
    """Create or update the reading progress for a session + document."""
    repo = _get_repository_and_document(repo_id, data.filepath, db)
    progress = reading_progress_service.upsert_progress(
        db=db,
        repository=repo,
        session_id=session_id,
        filepath=data.filepath,
        scroll_ratio=data.scroll_ratio,
        scroll_top=data.scroll_top,
    )
    if progress is None:
        raise HTTPException(status_code=404, detail="无法读取文档内容")
    return progress


@router.delete("")
async def delete_reading_progress(
    repo_id: int,
    filepath: str = Query(..., min_length=1, max_length=500, description="文档相对路径"),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db),
):
    """Delete the saved reading progress for a session + document."""
    repo = _get_repository_and_document(repo_id, filepath, db)
    deleted = reading_progress_service.delete_progress(
        db=db,
        repository=repo,
        session_id=session_id,
        filepath=filepath,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="阅读进度不存在")
    return {"message": "阅读进度已清除"}
