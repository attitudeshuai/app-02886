"""Database model for reading progress."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint

from app.database import Base


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False)
    repository_id = Column(Integer, nullable=False)
    filepath = Column(String(500), nullable=False)
    scroll_position = Column(Float, nullable=False, default=0.0)
    content_hash = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "session_id", "repository_id", "filepath",
            name="uq_reading_progress_session_doc"
        ),
    )

    def __repr__(self):
        return f"<ReadingProgress {self.session_id}:{self.filepath}>"
