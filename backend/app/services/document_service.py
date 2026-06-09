"""Document service for scanning and managing documents."""
import os
import re
import hashlib
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.repository import Repository, Document
from app.schemas.document import TreeNode

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations."""
    
    def __init__(self):
        self.doc_extensions = settings.DOC_EXTENSIONS
        self.max_file_size = settings.MAX_FILE_SIZE
    
    def scan_documents(
        self, 
        db: Session,
        repository: Repository
    ) -> int:
        """
        Scan repository for document files and save to database.
        
        Returns:
            Number of documents found
        """
        local_path = Path(repository.local_path)
        
        if not local_path.exists():
            logger.error(f"Repository path does not exist: {local_path}")
            return 0
        
        # Clear existing documents
        db.query(Document).filter(Document.repository_id == repository.id).delete()
        
        doc_count = 0
        
        for root, dirs, files in os.walk(local_path):
            # Skip hidden directories and common non-doc directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'venv', '.git', 'dist', 'build'
            ]]
            
            for filename in files:
                filepath = Path(root) / filename
                extension = filepath.suffix.lower()
                
                if extension not in self.doc_extensions:
                    continue
                
                # Check file size
                try:
                    size = filepath.stat().st_size
                    if size > self.max_file_size:
                        continue
                except OSError:
                    continue
                
                # Get relative path
                rel_path = filepath.relative_to(local_path)
                
                # Extract title from content (first heading)
                title = self._extract_title(filepath)
                content_hash = self._compute_content_hash(filepath)

                doc = Document(
                    repository_id=repository.id,
                    filename=filename,
                    filepath=str(rel_path),
                    extension=extension,
                    title=title,
                    size=size,
                    content_hash=content_hash,
                    is_indexed=False
                )
                db.add(doc)
                doc_count += 1
        
        db.commit()
        
        # Update repository doc count
        repository.doc_count = doc_count
        db.commit()
        
        logger.info(f"Scanned {doc_count} documents for repository {repository.name}")
        return doc_count
    
    def _extract_title(self, filepath: Path) -> Optional[str]:
        """Extract title from document (first heading)."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Read first 2000 chars
                
                # Look for first markdown heading
                match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if match:
                    return match.group(1).strip()[:255]
                
                # Look for first line as title
                lines = content.strip().split('\n')
                if lines:
                    first_line = lines[0].strip()
                    if first_line and len(first_line) < 255:
                        return first_line
                        
        except Exception as e:
            logger.debug(f"Failed to extract title from {filepath}: {e}")
        
        return None

    def _compute_content_hash(self, filepath: Path) -> Optional[str]:
        try:
            content = filepath.read_bytes()
            return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.debug(f"Failed to compute hash for {filepath}: {e}")
            return None

    def get_document_tree(
        self, 
        repository: Repository
    ) -> list[TreeNode]:
        """
        Build document tree structure for a repository.
        
        Returns:
            List of TreeNode objects
        """
        local_path = Path(repository.local_path)
        
        if not local_path.exists():
            return []
        
        return self._build_tree(local_path, local_path)
    
    def _build_tree(
        self, 
        current_path: Path, 
        base_path: Path
    ) -> list[TreeNode]:
        """Recursively build tree structure."""
        nodes = []
        
        try:
            items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return nodes
        
        for item in items:
            # Skip hidden files/dirs
            if item.name.startswith('.'):
                continue
            
            # Skip non-doc directories
            if item.is_dir() and item.name in [
                'node_modules', '__pycache__', 'venv', 'dist', 'build'
            ]:
                continue
            
            rel_path = item.relative_to(base_path)
            
            if item.is_dir():
                # Check if directory contains any documents
                children = self._build_tree(item, base_path)
                if children:  # Only include directories with documents
                    nodes.append(TreeNode(
                        name=item.name,
                        path=str(rel_path),
                        type='directory',
                        children=children
                    ))
            else:
                # Check if it's a document file
                if item.suffix.lower() in self.doc_extensions:
                    nodes.append(TreeNode(
                        name=item.name,
                        path=str(rel_path),
                        type='file',
                        extension=item.suffix.lower()
                    ))
        
        return nodes
    
    def get_document_content(
        self, 
        repository: Repository,
        filepath: str
    ) -> Optional[str]:
        """
        Read document content.
        
        Returns:
            Document content as string, or None if not found
        """
        local_path = Path(repository.local_path)
        full_path = local_path / filepath
        
        # Security check - prevent path traversal
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(local_path.resolve())):
                logger.warning(f"Path traversal attempt: {filepath}")
                return None
        except Exception:
            return None
        
        if not full_path.exists():
            return None
        
        # Check file size
        if full_path.stat().st_size > self.max_file_size:
            return "文件过大，无法显示"
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read document {filepath}: {e}")
            return None


# Singleton instance
document_service = DocumentService()
