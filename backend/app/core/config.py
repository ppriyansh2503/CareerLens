import os
from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings

DEMO_SECRET_KEY: str = "careerlens-super-secret-jwt-key-for-hackathon-demo-2026"

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerLens"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEMO_SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 60 minutes for production security
    
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

    @property
    def cors_origins(self) -> List[str]:
        origins = list(self.BACKEND_CORS_ORIGINS)
        if hasattr(self, "FRONTEND_URL") and self.FRONTEND_URL:
            clean_fe = self.FRONTEND_URL.strip().rstrip("/")
            if clean_fe and clean_fe not in origins:
                origins.append(clean_fe)
        env_cors = os.getenv("BACKEND_CORS_ORIGINS", "")
        if env_cors:
            for o in env_cors.split(","):
                co = o.strip()
                if co and co not in origins:
                    origins.append(co)
        return origins

    # Platform Admin Credentials
    PLATFORM_ADMIN_EMAIL: str = os.getenv("PLATFORM_ADMIN_EMAIL", "superadmin@careerlens.io")
    PLATFORM_ADMIN_PASSWORD_HASH: str = os.getenv(
        "PLATFORM_ADMIN_PASSWORD_HASH",
        "$2b$12$t1KNRZXpn4DBrS6GcEf3Iu/ovGLrMcLL28sJxLOCkdbRGy6cZwHdG"
    )

    # Frontend URL for Password Reset Links
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Email / SMTP Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@careerlens.io")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() in ("true", "1", "yes")
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() in ("true", "1", "yes")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @model_validator(mode="after")
    def validate_production_secret(self):
        if getattr(self, "ENVIRONMENT", "development").lower() == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == DEMO_SECRET_KEY:
                raise RuntimeError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "SECRET_KEY must be set to a secure, custom secret in production "
                    "and cannot use the default demo secret key."
                )
        return self

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure upload directories exist
os.makedirs(os.path.join(settings.UPLOAD_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "certificates"), exist_ok=True)
