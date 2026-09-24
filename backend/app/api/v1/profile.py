from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.schemas.profile import StudentProfileOut, StudentProfileUpdate, ReadinessScoreOut, ReadinessMetric

router = APIRouter()

@router.get("/student", response_model=StudentProfileOut)
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        # If user is recruiter or admin viewing student, get default student profile for preview
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")

    skills_data = []
    for s in profile.skills:
        if s.skill:
            skills_data.append({
                "id": s.id,
                "skill_id": s.skill_id,
                "name": s.skill.name,
                "category": s.skill.category,
                "proficiency": s.proficiency,
                "source": s.source,
                "is_verified": s.is_verified,
                "verified_by_certificate_id": s.verified_by_certificate_id
            })

    certs_data = []
    for c in profile.certificates:
        certs_data.append({
            "id": c.id,
            "title": c.title,
            "issuing_org": c.issuing_org,
            "verification_status": c.verification_status,
            "badge_tier": c.badge_tier,
            "verification_score": c.verification_score
        })

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": profile.user.full_name if profile.user else "Student",
        "email": profile.user.email if profile.user else "",
        "college_name": profile.user.college_name if profile.user else "National Institute of Technology",
        "headline": profile.headline,
        "bio": profile.bio,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "portfolio_url": profile.portfolio_url,
        "resume_file_url": profile.resume_file_url,
        "graduation_year": profile.graduation_year,
        "department": profile.department,
        "cgpa": profile.cgpa,
        "placement_readiness_score": profile.placement_readiness_score,
        "skills": skills_data,
        "certificates": certs_data
    }

@router.put("/student", response_model=StudentProfileOut)
def update_student_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return get_student_profile(current_user=current_user, db=db)

@router.get("/readiness", response_model=ReadinessScoreOut)
def get_readiness_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="No profile found")

    total_skills = len(profile.skills)
    verified_skills = [s.skill.name for s in profile.skills if s.is_verified and s.skill]
    unverified_skills = [s.skill.name for s in profile.skills if not s.is_verified and s.skill]
    verified_certs = sum(1 for c in profile.certificates if c.verification_status == "VERIFIED")

    metrics = [
        ReadinessMetric(
            label="Verified Credentials",
            score=min(35.0, verified_certs * 15.0),
            max_score=35.0,
            description="Weight awarded for tamper-proof certificates with Gold or Silver badges."
        ),
        ReadinessMetric(
            label="Skill Breadth & Depth",
            score=min(30.0, total_skills * 4.0),
            max_score=30.0,
            description="Extracted and certified competencies across frontend, backend, and cloud."
        ),
        ReadinessMetric(
            label="Resume & Portfolio Completeness",
            score=20.0 if profile.resume_file_url and profile.github_url else 12.0,
            max_score=20.0,
            description="Presence of parsed resume, active GitHub, and project portfolio links."
        ),
        ReadinessMetric(
            label="Academic Fit",
            score=min(15.0, (profile.cgpa or 8.0) * 1.6),
            max_score=15.0,
            description="Undergraduate CGPA and department domain relevance."
        )
    ]

    overall = profile.placement_readiness_score or sum(m.score for m in metrics)
    overall = min(100.0, round(overall, 1))

    rating = "Ready to Place" if overall >= 80 else ("Near Ready" if overall >= 60 else "Developing")

    return {
        "overall_score": overall,
        "rating": rating,
        "metrics": metrics,
        "key_strengths": verified_skills[:4] if verified_skills else ["Core Computer Science Fundamentals"],
        "critical_gaps": ["Cloud Deployment & CI/CD", "Production Caching (Redis)"],
        "suggested_action": "Earn a Gold Badge in Cloud Architecture to elevate your readiness score to 90%+."
    }
