"""Database model for reading progress."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint

from app.database import Base


class ReadingProgress(Base):
    """Reading progress model."""
    
    __tablename__ = "reading_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    filepath = Column(String(500), nullable=False)
    scroll_position = Column(Float, default=0.0)
    last_read_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('session_id', 'repository_id', 'filepath', name='_session_repo_file_uc'),
    )
    
    def __repr__(self):
        return f"<ReadingProgress {self.session_id}:{self.filepath}>"
