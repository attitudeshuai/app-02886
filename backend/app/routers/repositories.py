"""Repository API routes."""
import logging
import re
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Repository, Document
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.schemas.document import DocumentContent, TreeNode
from app.services.git_service import git_service
from app.services.document_service import document_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["repositories"])


def extract_repo_name(url: str) -> str:
    """Extract repository name from URL."""
    # Remove trailing slash and .git
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Get last part of URL
    parts = url.split('/')
    return parts[-1] if parts else 'unknown'


def clone_and_scan(repo_id: int, url: str, branch: str, db_url: str):
    """Background task to clone repository and scan documents."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            return
        
        # Update status to cloning
        repo.status = "cloning"
        db.commit()
        
        # Clone repository
        local_path, error = git_service.clone_repository(url, branch)
        
        if error:
            repo.status = "error"
            repo.error_message = error
            db.commit()
            return
        
        # Update local path
        repo.local_path = str(local_path)
        db.commit()
        
        # Scan documents
        doc_count = document_service.scan_documents(db, repo)
        
        # Update status to ready
        repo.status = "ready"
        repo.doc_count = doc_count
        db.commit()
        
        logger.info(f"Repository {repo.name} ready with {doc_count} documents")
        
    except Exception as e:
        logger.error(f"Error processing repository: {e}")
        try:
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            if repo:
                repo.status = "error"
                repo.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        db.close()


@router.get("", response_model=list[RepositoryResponse])
async def list_repositories(db: Session = Depends(get_db)):
    """List all repositories."""
    repos = db.query(Repository).order_by(Repository.created_at.desc()).all()
    return repos


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: int, db: Session = Depends(get_db)):
    """Get a single repository by ID."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return repo


@router.post("", response_model=RepositoryResponse)
async def create_repository(
    data: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new repository."""
    # Check if URL already exists
    existing = db.query(Repository).filter(Repository.url == data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="该仓库已添加")
    
    # Extract repo name
    name = extract_repo_name(data.url)
    
    # Create repository record
    repo = Repository(
        name=name,
        url=data.url,
        branch=data.branch or "main",
        local_path="",  # Will be set after cloning
        status="pending"
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    
    # Start background clone task
    from app.config import settings
    background_tasks.add_task(
        clone_and_scan,
        repo.id,
        data.url,
        data.branch or "main",
        settings.DATABASE_URL
    )
    
    return repo


@router.delete("/{repo_id}")
async def delete_repository(repo_id: int, db: Session = Depends(get_db)):
    """Delete a repository."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    # Delete local files
    if repo.local_path:
        git_service.delete_repository(Path(repo.local_path))
    
    # Delete from database
    db.delete(repo)
    db.commit()
    
    return {"message": "仓库已删除"}


@router.post("/{repo_id}/refresh", response_model=RepositoryResponse)
async def refresh_repository(
    repo_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh a repository (pull latest changes)."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    # Re-clone the repository
    repo.status = "pending"
    db.commit()
    
    from app.config import settings
    background_tasks.add_task(
        clone_and_scan,
        repo.id,
        repo.url,
        repo.branch,
        settings.DATABASE_URL
    )
    
    return repo


@router.get("/{repo_id}/tree", response_model=list[TreeNode])
async def get_document_tree(repo_id: int, db: Session = Depends(get_db)):
    """Get document tree for a repository."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    if repo.status != "ready":
        raise HTTPException(status_code=400, detail="仓库尚未准备就绪")
    
    tree = document_service.get_document_tree(repo)
    return tree


@router.get("/{repo_id}/documents", response_model=DocumentContent)
async def get_document_content(
    repo_id: int,
    filepath: str = Query(..., description="Document file path"),
    db: Session = Depends(get_db)
):
    """Get document content by filepath."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    # Get document from database
    doc = db.query(Document).filter(
        Document.repository_id == repo_id,
        Document.filepath == filepath
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # Read content
    content = document_service.get_document_content(repo, filepath)
    if content is None:
        raise HTTPException(status_code=404, detail="无法读取文档内容")
    
    return DocumentContent(document=doc, content=content)
