"""Service for managing reading progress."""
import hashlib
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.models.reading_progress import ReadingProgress

logger = logging.getLogger(__name__)


class ReadingProgressService:
    """Service for reading progress operations."""

    def _compute_content_hash(self, local_path: Path, filepath: str) -> Optional[str]:
        """
        Compute a hash of the document's file metadata (size + mtime).
        This is fast and reliable for detecting content changes after a refresh.

        Returns:
            A hex digest string, or None if the file doesn't exist.
        """
        full_path = (local_path / filepath).resolve()

        try:
            if not str(full_path).startswith(str(local_path.resolve())):
                logger.warning(f"Path traversal attempt when computing hash: {filepath}")
                return None
        except Exception:
            return None

        if not full_path.exists() or not full_path.is_file():
            return None

        try:
            stat = full_path.stat()
            raw = f"{stat.st_size}:{int(stat.st_mtime)}"
            return hashlib.md5(raw.encode("utf-8")).hexdigest()
        except OSError as e:
            logger.error(f"Failed to stat file for hash {filepath}: {e}")
            return None

    def save_progress(
        self,
        db: Session,
        session_id: str,
        repo_id: int,
        filepath: str,
        scroll_position: int,
    ) -> Optional[ReadingProgress]:
        """
        Save or update reading progress for a session+document.

        Computes the current content hash and stores it alongside the scroll
        position. If the document later changes (different hash), the progress
        will be reset on the next read.

        Returns:
            The updated ReadingProgress record, or None if the repository
            does not exist.
        """
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            return None

        content_hash = self._compute_content_hash(Path(repo.local_path), filepath)

        progress = (
            db.query(ReadingProgress)
            .filter(
                ReadingProgress.session_id == session_id,
                ReadingProgress.repo_id == repo_id,
                ReadingProgress.filepath == filepath,
            )
            .first()
        )

        if progress:
            progress.scroll_position = scroll_position
            progress.content_hash = content_hash
        else:
            progress = ReadingProgress(
                session_id=session_id,
                repo_id=repo_id,
                filepath=filepath,
                scroll_position=scroll_position,
                content_hash=content_hash,
            )
            db.add(progress)

        db.commit()
        db.refresh(progress)
        return progress

    def get_progress(
        self,
        db: Session,
        session_id: str,
        repo_id: int,
        filepath: str,
    ) -> int:
        """
        Retrieve the saved scroll position for a session+document.

        Read-only: if the document content has changed since progress was
        saved (detected via content hash mismatch), returns 0 without
        modifying the database. The actual reset of the stored record
        happens on the next call to save_progress.

        Returns:
            The scroll position in pixels, or 0 if no valid progress exists.
        """
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            return 0

        progress = (
            db.query(ReadingProgress)
            .filter(
                ReadingProgress.session_id == session_id,
                ReadingProgress.repo_id == repo_id,
                ReadingProgress.filepath == filepath,
            )
            .first()
        )

        if not progress:
            return 0

        current_hash = self._compute_content_hash(Path(repo.local_path), filepath)

        if progress.content_hash != current_hash:
            return 0

        return progress.scroll_position


reading_progress_service = ReadingProgressService()
