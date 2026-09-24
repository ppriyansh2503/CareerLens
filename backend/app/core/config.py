import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerLens"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "careerlens-super-secret-jwt-key-for-hackathon-demo-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for demo ease
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./careerlens.db")
    
    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB: int = 10
    
    # AI / LLM
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure upload directories exist
os.makedirs(os.path.join(settings.UPLOAD_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "certificates"), exist_ok=True)
