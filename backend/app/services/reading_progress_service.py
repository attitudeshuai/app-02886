"""Service for managing user reading progress."""
import hashlib
import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.reading_progress import ReadingProgress
from app.models.repository import Repository
from app.services.document_service import document_service

logger = logging.getLogger(__name__)


class ReadingProgressService:
    """Service for storing and retrieving document reading progress."""

    @staticmethod
    def _hash_content(content: str) -> str:
        """Compute a stable hash for a document's textual content."""
        return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    def _current_content_hash(
        self,
        repository: Repository,
        filepath: str,
    ) -> Optional[str]:
        """Read the document and compute its current content hash."""
        content = document_service.get_document_content(repository, filepath)
        if content is None:
            return None
        return self._hash_content(content)

    def get_progress(
        self,
        db: Session,
        repository: Repository,
        session_id: str,
        filepath: str,
    ) -> Tuple[Optional[ReadingProgress], bool]:
        """Get a session's reading progress for a document.

        Returns a tuple `(progress, reset)`. This is a read-only operation:
        when the document content has changed since the progress was saved
        (or the document is unreadable), `(None, True)` is returned to tell
        the caller to reset to the top, but the stored row is left intact.
        Stale records will be overwritten naturally on the next `upsert_progress`,
        or cleared when the repository / document is removed.
        """
        progress = (
            db.query(ReadingProgress)
            .filter(
                ReadingProgress.session_id == session_id,
                ReadingProgress.repository_id == repository.id,
                ReadingProgress.filepath == filepath,
            )
            .first()
        )

        if not progress:
            return None, False

        current_hash = self._current_content_hash(repository, filepath)
        if current_hash is None:
            # Document is missing or unreadable; signal reset without
            # mutating the database from a GET handler.
            return None, True

        if progress.content_hash and progress.content_hash != current_hash:
            logger.info(
                "Reading progress stale for session=%s repo=%s path=%s; "
                "signalling reset (no DB mutation)",
                session_id,
                repository.id,
                filepath,
            )
            return None, True

        return progress, False

    def upsert_progress(
        self,
        db: Session,
        repository: Repository,
        session_id: str,
        filepath: str,
        scroll_ratio: float,
        scroll_top: int,
    ) -> Optional[ReadingProgress]:
        """Create or update reading progress for a document.

        Returns the persisted ReadingProgress, or None if the document
        cannot be found / read.
        """
        current_hash = self._current_content_hash(repository, filepath)
        if current_hash is None:
            return None

        # Clamp ratio defensively (Pydantic also enforces this).
        if scroll_ratio < 0.0:
            scroll_ratio = 0.0
        elif scroll_ratio > 1.0:
            scroll_ratio = 1.0
        if scroll_top < 0:
            scroll_top = 0

        progress = (
            db.query(ReadingProgress)
            .filter(
                ReadingProgress.session_id == session_id,
                ReadingProgress.repository_id == repository.id,
                ReadingProgress.filepath == filepath,
            )
            .first()
        )

        if progress:
            progress.scroll_ratio = scroll_ratio
            progress.scroll_top = scroll_top
            progress.content_hash = current_hash
        else:
            progress = ReadingProgress(
                session_id=session_id,
                repository_id=repository.id,
                filepath=filepath,
                scroll_ratio=scroll_ratio,
                scroll_top=scroll_top,
                content_hash=current_hash,
            )
            db.add(progress)

        db.commit()
        db.refresh(progress)
        return progress

    def delete_progress(
        self,
        db: Session,
        repository: Repository,
        session_id: str,
        filepath: str,
    ) -> bool:
        """Delete reading progress for a document. Returns True if deleted."""
        progress = (
            db.query(ReadingProgress)
            .filter(
                ReadingProgress.session_id == session_id,
                ReadingProgress.repository_id == repository.id,
                ReadingProgress.filepath == filepath,
            )
            .first()
        )
        if not progress:
            return False
        db.delete(progress)
        db.commit()
        return True


# Singleton instance
reading_progress_service = ReadingProgressService()
