"""Service for reading progress operations."""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.reading_progress import ReadingProgress
from app.models.repository import Document

logger = logging.getLogger(__name__)


class ReadingProgressService:

    def save_progress(
        self,
        db: Session,
        session_id: str,
        repository_id: int,
        filepath: str,
        scroll_position: float,
    ) -> ReadingProgress:
        doc = db.query(Document).filter(
            Document.repository_id == repository_id,
            Document.filepath == filepath,
        ).first()

        current_hash = doc.content_hash if doc else None

        existing = db.query(ReadingProgress).filter(
            ReadingProgress.session_id == session_id,
            ReadingProgress.repository_id == repository_id,
            ReadingProgress.filepath == filepath,
        ).first()

        if existing:
            if existing.content_hash != current_hash:
                scroll_position = 0.0
            existing.scroll_position = scroll_position
            existing.content_hash = current_hash
            db.commit()
            db.refresh(existing)
            return existing

        progress = ReadingProgress(
            session_id=session_id,
            repository_id=repository_id,
            filepath=filepath,
            scroll_position=scroll_position,
            content_hash=current_hash,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    def get_progress(
        self,
        db: Session,
        session_id: str,
        repository_id: int,
        filepath: str,
    ) -> Optional[ReadingProgress]:
        return db.query(ReadingProgress).filter(
            ReadingProgress.session_id == session_id,
            ReadingProgress.repository_id == repository_id,
            ReadingProgress.filepath == filepath,
        ).first()

    def get_current_content_hash(
        self,
        db: Session,
        repository_id: int,
        filepath: str,
    ) -> Optional[str]:
        doc = db.query(Document).filter(
            Document.repository_id == repository_id,
            Document.filepath == filepath,
        ).first()
        return doc.content_hash if doc else None


reading_progress_service = ReadingProgressService()
