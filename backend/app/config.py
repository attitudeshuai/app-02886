"""Application configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "Git Doc Fetcher"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/db/app.db"
    
    # Storage paths
    DATA_DIR: Path = Path("./data")
    REPOS_DIR: Path = Path("./data/repos")
    DB_DIR: Path = Path("./data/db")
    
    # Document settings
    DOC_EXTENSIONS: list[str] = [".md", ".txt", ".rst", ".adoc"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Git settings
    GIT_CLONE_DEPTH: int = 1  # Shallow clone
    
    class Config:
        env_file = ".env"


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.REPOS_DIR.mkdir(parents=True, exist_ok=True)
settings.DB_DIR.mkdir(parents=True, exist_ok=True)
