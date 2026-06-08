"""Git repository service for cloning and managing repositories."""
import os
import shutil
import logging
import hashlib
from pathlib import Path
from typing import Optional

from git import Repo, GitCommandError

from app.config import settings

logger = logging.getLogger(__name__)


class GitService:
    """Service for Git operations."""
    
    def __init__(self):
        self.repos_dir = settings.REPOS_DIR
    
    def _get_repo_dir_name(self, url: str) -> str:
        """Generate a unique directory name for a repository."""
        # Extract repo name from URL
        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # Add hash to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{repo_name}_{url_hash}"
    
    def get_repo_path(self, url: str) -> Path:
        """Get the local path for a repository."""
        dir_name = self._get_repo_dir_name(url)
        return self.repos_dir / dir_name
    
    def clone_repository(
        self, 
        url: str, 
        branch: str = "main"
    ) -> tuple[Path, Optional[str]]:
        """
        Clone a repository using shallow clone.
        
        Returns:
            Tuple of (local_path, error_message)
        """
        local_path = self.get_repo_path(url)
        
        try:
            # Remove existing directory if exists
            if local_path.exists():
                shutil.rmtree(local_path)
            
            logger.info(f"Cloning repository: {url} to {local_path}")
            
            # Clone with shallow depth
            Repo.clone_from(
                url,
                local_path,
                branch=branch,
                depth=settings.GIT_CLONE_DEPTH,
                single_branch=True
            )
            
            logger.info(f"Successfully cloned repository: {url}")
            return local_path, None
            
        except GitCommandError as e:
            error_msg = str(e)
            logger.error(f"Failed to clone repository {url}: {error_msg}")
            
            # Try with default branch if specified branch fails
            if branch != "main":
                try:
                    logger.info(f"Retrying with branch 'main'")
                    Repo.clone_from(
                        url,
                        local_path,
                        branch="main",
                        depth=settings.GIT_CLONE_DEPTH,
                        single_branch=True
                    )
                    return local_path, None
                except GitCommandError:
                    pass
            
            # Try with 'master' branch as fallback
            try:
                logger.info(f"Retrying with branch 'master'")
                Repo.clone_from(
                    url,
                    local_path,
                    branch="master",
                    depth=settings.GIT_CLONE_DEPTH,
                    single_branch=True
                )
                return local_path, None
            except GitCommandError as e2:
                return local_path, f"克隆失败: {str(e2)}"
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Failed to clone repository {url}: {error_msg}")
            return local_path, error_msg
    
    def pull_repository(self, local_path: Path) -> Optional[str]:
        """
        Pull latest changes for a repository.
        
        Returns:
            Error message if failed, None if successful
        """
        try:
            repo = Repo(local_path)
            origin = repo.remotes.origin
            origin.pull()
            logger.info(f"Successfully pulled repository: {local_path}")
            return None
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to pull repository {local_path}: {error_msg}")
            return error_msg
    
    def delete_repository(self, local_path: Path) -> bool:
        """Delete a local repository."""
        try:
            if local_path.exists():
                shutil.rmtree(local_path)
                logger.info(f"Deleted repository: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete repository {local_path}: {e}")
            return False
    
    def get_repo_info(self, local_path: Path) -> dict:
        """Get repository information."""
        try:
            repo = Repo(local_path)
            return {
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha[:8],
                "commit_message": repo.head.commit.message.strip()[:100]
            }
        except Exception as e:
            logger.error(f"Failed to get repo info: {e}")
            return {}


# Singleton instance
git_service = GitService()
