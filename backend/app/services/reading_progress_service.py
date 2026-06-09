"""Reading progress service for managing document reading positions."""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.reading_progress import ReadingProgress
from app.models.repository import Document

logger = logging.getLogger(__name__)


class ReadingProgressService:
    """Service for reading progress operations."""
    
    def get_progress(
        self,
        db: Session,
        session_id: str,
        repository_id: int,
        filepath: str
    ) -> Optional[ReadingProgress]:
        """
        Get reading progress for a specific document and session.
        
        Args:
            db: Database session
            session_id: User session ID
            repository_id: Repository ID
            filepath: Document file path
            
        Returns:
            ReadingProgress object or None if not found
        """
        return db.query(ReadingProgress).filter(
            ReadingProgress.session_id == session_id,
            ReadingProgress.repository_id == repository_id,
            ReadingProgress.filepath == filepath
        ).first()
    
    def save_progress(
        self,
        db: Session,
        session_id: str,
        repository_id: int,
        filepath: str,
        scroll_position: float
    ) -> ReadingProgress:
        """
        Save or update reading progress.
        
        Args:
            db: Database session
            session_id: User session ID
            repository_id: Repository ID
            filepath: Document file path
            scroll_position: Scroll position (0.0 to 1.0)
            
        Returns:
            Updated ReadingProgress object
        """
        progress = self.get_progress(db, session_id, repository_id, filepath)
        
        if progress:
            progress.scroll_position = scroll_position
        else:
            progress = ReadingProgress(
                session_id=session_id,
                repository_id=repository_id,
                filepath=filepath,
                scroll_position=scroll_position
            )
            db.add(progress)
        
        db.commit()
        db.refresh(progress)
        return progress
    
    def reset_progress(
        self,
        db: Session,
        session_id: str,
        repository_id: int,
        filepath: str
    ) -> bool:
        """
        Reset reading progress for a document.
        
        Args:
            db: Database session
            session_id: User session ID
            repository_id: Repository ID
            filepath: Document file path
            
        Returns:
            True if progress was reset, False if no progress existed
        """
        progress = self.get_progress(db, session_id, repository_id, filepath)
        if progress:
            progress.scroll_position = 0.0
            db.commit()
            return True
        return False
    
    def reset_all_progress_for_repository(
        self,
        db: Session,
        repository_id: int
    ) -> int:
        """
        Reset all reading progress for a repository (when documents are updated).
        
        Args:
            db: Database session
            repository_id: Repository ID
            
        Returns:
            Number of progress records reset
        """
        count = db.query(ReadingProgress).filter(
            ReadingProgress.repository_id == repository_id
        ).update({"scroll_position": 0.0})
        db.commit()
        return count
    
    def delete_progress_for_repository(
        self,
        db: Session,
        repository_id: int
    ) -> int:
        """
        Delete all reading progress for a repository.
        
        Args:
            db: Database session
            repository_id: Repository ID
            
        Returns:
            Number of progress records deleted
        """
        count = db.query(ReadingProgress).filter(
            ReadingProgress.repository_id == repository_id
        ).delete()
        db.commit()
        return count
    
    def delete_progress_for_document(
        self,
        db: Session,
        repository_id: int,
        filepath: str
    ) -> int:
        """
        Delete all reading progress for a specific document.
        
        Args:
            db: Database session
            repository_id: Repository ID
            filepath: Document file path
            
        Returns:
            Number of progress records deleted
        """
        count = db.query(ReadingProgress).filter(
            ReadingProgress.repository_id == repository_id,
            ReadingProgress.filepath == filepath
        ).delete()
        db.commit()
        return count


# Singleton instance
reading_progress_service = ReadingProgressService()
