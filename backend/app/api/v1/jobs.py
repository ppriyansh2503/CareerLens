from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.schemas.job import JobOut, JobCreate, JobSkillOut
from app.services.matching_engine import MatchingEngine
from app.services.skill_service import get_or_create_skill

router = APIRouter()

@router.get("/", response_model=List[JobOut])
def get_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).filter(Job.is_active == True).all()
    
    # Check if student profile exists to calculate personalized match
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        student = db.query(StudentProfile).first()

    results = []
    for job in jobs:
        job_skills_out = [
            JobSkillOut(
                id=js.id,
                name=js.skill.name,
                category=js.skill.category,
                is_mandatory=js.is_mandatory,
                weight=js.weight
            ) for js in job.skills if js.skill
        ]

        match_score = None
        match_tier = None
        if student:
            match_res = MatchingEngine.calculate_match(student, job)
            match_score = match_res["overall_score"]
            match_tier = match_res["match_tier"]

        job_dict = {
            "id": job.id,
            "recruiter_id": job.recruiter_id,
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "job_type": job.job_type,
            "stipend_or_salary": job.stipend_or_salary,
            "description": job.description,
            "requirements_summary": job.requirements_summary,
            "is_active": job.is_active,
            "created_at": job.created_at,
            "skills": job_skills_out,
            "match_score": match_score,
            "match_tier": match_tier
        }
        results.append(job_dict)

    # Sort by match score descending if computed
    results.sort(key=lambda j: j.get("match_score") or 0.0, reverse=True)
    return results

@router.get("/{job_id}", response_model=JobOut)
def get_job_by_id(
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

    job_skills_out = [
        JobSkillOut(
            id=js.id,
            name=js.skill.name,
            category=js.skill.category,
            is_mandatory=js.is_mandatory,
            weight=js.weight
        ) for js in job.skills if js.skill
    ]

    match_score = None
    match_tier = None
    if student:
        match_res = MatchingEngine.calculate_match(student, job)
        match_score = match_res["overall_score"]
        match_tier = match_res["match_tier"]

    return {
        "id": job.id,
        "recruiter_id": job.recruiter_id,
        "title": job.title,
        "company_name": job.company_name,
        "location": job.location,
        "job_type": job.job_type,
        "stipend_or_salary": job.stipend_or_salary,
        "description": job.description,
        "requirements_summary": job.requirements_summary,
        "is_active": job.is_active,
        "created_at": job.created_at,
        "skills": job_skills_out,
        "match_score": match_score,
        "match_tier": match_tier
    }

@router.post("/", response_model=JobOut)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "recruiter" and current_user.role != "platform_admin":
        raise HTTPException(
            status_code=403,
            detail="Requires recruiter privileges to post jobs"
        )
    if getattr(current_user, "approval_status", "APPROVED") != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail="Recruiter account pending platform admin approval. Job posting is restricted."
        )

    job = Job(
        recruiter_id=current_user.id,
        title=job_in.title,
        company_name=job_in.company_name,
        location=job_in.location,
        job_type=job_in.job_type,
        stipend_or_salary=job_in.stipend_or_salary,
        description=job_in.description,
        requirements_summary=job_in.requirements_summary
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Attach skills idempotently
    for skill_name in job_in.skills:
        skill = get_or_create_skill(db, skill_name, category="technical")
        job_skill = JobSkill(job_id=job.id, skill_id=skill.id, is_mandatory=True, weight=1.0)
        db.add(job_skill)

    db.commit()
    db.refresh(job)
    return get_job_by_id(job_id=job.id, current_user=current_user, db=db)
