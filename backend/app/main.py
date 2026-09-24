import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.api import api_router
from app.seed.seed_data import seed_database_if_empty

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
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
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

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
