"""Database model for reading progress."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint

from app.database import Base


class ReadingProgress(Base):
    """Reading progress model tracking user's scroll position per document."""

    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    filepath = Column(String(500), nullable=False, index=True)
    scroll_position = Column(Integer, default=0, nullable=False)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "repo_id", "filepath", name="uix_session_repo_filepath"),
    )

    def __repr__(self):
        return f"<ReadingProgress session={self.session_id} repo={self.repo_id} filepath={self.filepath}>"
