import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.api import api_router
from app.seed.seed_data import seed_database_if_empty

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

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for hackathon dev ease
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded static files
uploads_abs_path = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(uploads_abs_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_abs_path), name="uploads")

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
