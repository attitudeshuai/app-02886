"""Export API routes."""
import io
import zipfile
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Repository, Document
from app.services.document_service import document_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["export"])


@router.get("/repositories/{repo_id}/export")
async def export_document(
    repo_id: int,
    filepath: str = Query(..., description="Document file path"),
    db: Session = Depends(get_db)
):
    """Export a single document as Markdown."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    doc = db.query(Document).filter(
        Document.repository_id == repo_id,
        Document.filepath == filepath
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    content = document_service.get_document_content(repo, filepath)
    if content is None:
        raise HTTPException(status_code=404, detail="无法读取文档内容")
    
    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{doc.filename}"'
        }
    )


@router.get("/repositories/{repo_id}/export-all")
async def export_all_documents(
    repo_id: int,
    db: Session = Depends(get_db)
):
    """Export all documents as ZIP."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    
    if repo.status != "ready":
        raise HTTPException(status_code=400, detail="仓库尚未准备就绪")
    
    documents = db.query(Document).filter(
        Document.repository_id == repo_id
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="没有可导出的文档")
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc in documents:
            content = document_service.get_document_content(repo, doc.filepath)
            if content:
                zip_file.writestr(doc.filepath, content.encode('utf-8'))
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{repo.name}-docs.zip"'
        }
    )
