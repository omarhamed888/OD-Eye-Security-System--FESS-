from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration using Pydantic Settings"""
    
    # Database - Using SQLite for simpler setup (no PostgreSQL installation needed)
    # For production, use: postgresql://user:pass@localhost:5432/dbname
    DATABASE_URL: str = "sqlite:///./fess_security.db"
    REDIS_URL: str = "redis://localhost:6379/0"  # Optional - for caching
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Camera
    CAMERA_INDEX: int = 0
    CONFIDENCE_THRESHOLD: float = 0.15
    ALERT_COOLDOWN: int = 30
    
    # Telegram
    TELEGRAM_TOKEN: Optional[str] = None
    CHAT_ID: Optional[str] = None
    
    # Paths
    LOGS_DIR: Path = Path("./logs")
    MODELS_DIR: Path = Path("./models")
    KNOWN_FACES_DIR: Path = Path("./known_faces")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Falcon Eye Security System"
    VERSION: str = "2.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
