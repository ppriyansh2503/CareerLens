from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.models.job import Job
from app.schemas.matching import ExplainableMatchOut, RoadmapOut
from app.services.matching_engine import MatchingEngine

router = APIRouter()

@router.get("/explain/{job_id}", response_model=ExplainableMatchOut)
def get_explainable_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        student = db.query(StudentProfile).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

    return MatchingEngine.calculate_match(student, job)

@router.get("/roadmap/{job_id}", response_model=RoadmapOut)
@router.post("/roadmap/{job_id}", response_model=RoadmapOut)
def get_skill_gap_roadmap(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        student = db.query(StudentProfile).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

    return MatchingEngine.generate_learning_roadmap(student, job)
