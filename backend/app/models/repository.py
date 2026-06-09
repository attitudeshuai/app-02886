"""Database models for repositories and documents."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Repository(Base):
    """Git repository model."""
    
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    local_path = Column(String(500), nullable=False)
    branch = Column(String(100), default="main")
    status = Column(String(50), default="pending")  # pending, cloning, ready, error
    error_message = Column(Text, nullable=True)
    doc_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Repository {self.name}>"


class Document(Base):
    """Document file model."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)  # Relative path in repo
    extension = Column(String(20), nullable=False)
    title = Column(String(255), nullable=True)
    size = Column(Integer, default=0)
    content_hash = Column(String(32), nullable=True)
    is_indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filepath}>"
