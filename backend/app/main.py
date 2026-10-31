import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.api.v1.files import get_uploaded_file
from app.api.v1.api import api_router
from app.seed.seed_data import seed_database_if_empty

logger = logging.getLogger("careerlens.main")

from contextlib import asynccontextmanager

from sqlalchemy import inspect, text

def run_sqlite_migrations():
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            if inspector.has_table("users"):
                user_cols = [c["name"] for c in inspector.get_columns("users")]
                if "approval_status" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN approval_status VARCHAR DEFAULT 'APPROVED';"))
                    conn.commit()
                if "phone_number" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR;"))
                    conn.commit()

            if inspector.has_table("certificates"):
                cert_cols = [c["name"] for c in inspector.get_columns("certificates")]
                if "admin_review_status" not in cert_cols:
                    conn.execute(text("ALTER TABLE certificates ADD COLUMN admin_review_status VARCHAR DEFAULT 'NONE';"))
                    conn.commit()
                if "admin_review_reason" not in cert_cols:
                    conn.execute(text("ALTER TABLE certificates ADD COLUMN admin_review_reason TEXT;"))
                    conn.commit()
                if "admin_reviewed_at" not in cert_cols:
                    conn.execute(text("ALTER TABLE certificates ADD COLUMN admin_reviewed_at DATETIME;"))
                    conn.commit()
                if "admin_reviewed_by_id" not in cert_cols:
                    conn.execute(text("ALTER TABLE certificates ADD COLUMN admin_reviewed_by_id INTEGER;"))
                    conn.commit()
    except Exception as e:
        print(f"[CareerLens Migrations] Column migration notice: {e}")

def init_db():
    Base.metadata.create_all(bind=engine)
    run_sqlite_migrations()
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

# Ensure DB tables and seed data exist at import time
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="CareerLens: AI-Powered Verified Career and Internship Matching Platform API",
    version="1.0.0"
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set up CORS with explicit trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if getattr(settings, "ENVIRONMENT", "development").lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Global unhandled exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Pass through HTTPExceptions handled by FastAPI
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    logger.error(f"[CareerLens Unhandled Exception] {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later.", "code": "INTERNAL_SERVER_ERROR"}
    )

# Authenticated access for uploaded files (replaces insecure public StaticFiles mount)
@app.get("/uploads/{category}/{filename}", tags=["Authenticated Uploads"])
def serve_secure_upload(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_uploaded_file(category=category, filename=filename, current_user=current_user, db=db)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {
        "platform": "CareerLens",
        "tagline": "AI-Powered Verified Career & Internship Matching Platform",
        "version": "1.0.0",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CareerLens API"}
