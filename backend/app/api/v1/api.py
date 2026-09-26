from fastapi import APIRouter
from app.api.v1 import (
    auth,
    profile,
    resume,
    certificates,
    jobs,
    matching,
    chat,
    recruiter,
    college,
    admin
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Demo Switch"])
api_router.include_router(profile.router, prefix="/profile", tags=["Student Profile & Readiness"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume Parser & Skills"])
api_router.include_router(certificates.router, prefix="/certificates", tags=["Certificate Verification Engine"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Internships & Jobs"])
api_router.include_router(matching.router, prefix="/matching", tags=["Explainable Matching & Learning Roadmap"])
api_router.include_router(chat.router, prefix="/chat", tags=["Bilingual AI Career Counselor"])
api_router.include_router(recruiter.router, prefix="/recruiter", tags=["Company / Recruiter Discovery"])
api_router.include_router(college.router, prefix="/college", tags=["College / TPO Placement Analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["Platform Administrator & Governance"])

@api_router.get("/health")
def api_v1_health():
    return {"status": "healthy", "service": "CareerLens API v1"}
