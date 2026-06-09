"""Database model for reading progress memory."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint

from app.database import Base


class ReadingProgress(Base):
    """Reading progress per session + document."""

    __tablename__ = "reading_progress"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "repository_id", "filepath",
            name="uq_reading_progress_session_repo_filepath"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), nullable=False, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    filepath = Column(String(500), nullable=False)
    # Normalized scroll position in [0, 1] so it survives layout/font changes
    scroll_ratio = Column(Float, nullable=False, default=0.0)
    # Absolute scroll offset in pixels (best-effort, used as fallback)
    scroll_top = Column(Integer, nullable=False, default=0)
    # Hash of document content; used to invalidate progress when document changes
    content_hash = Column(String(64), nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<ReadingProgress session={self.session_id} "
            f"repo={self.repository_id} path={self.filepath} ratio={self.scroll_ratio}>"
        )
