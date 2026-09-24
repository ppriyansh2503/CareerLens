from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate

router = APIRouter()

@router.get("/candidates")
def discover_candidates(
    skill: Optional[str] = Query(None, description="Filter by skill name"),
    badge: Optional[str] = Query(None, description="Filter by badge tier: GOLD, SILVER, or ALL"),
    verified_only: bool = Query(False, description="Show only candidates with verified skills"),
    min_readiness: float = Query(0.0, description="Minimum readiness score"),
    db: Session = Depends(get_db)
):
    query = db.query(StudentProfile)
    
    if min_readiness > 0:
        query = query.filter(StudentProfile.placement_readiness_score >= min_readiness)

    students = query.all()
    results = []

    for s in students:
        # Check verified badges
        gold_count = sum(1 for c in s.certificates if c.badge_tier == "GOLD")
        silver_count = sum(1 for c in s.certificates if c.badge_tier == "SILVER")
        highest_badge = "GOLD" if gold_count > 0 else ("SILVER" if silver_count > 0 else "NONE")

        if badge and badge.upper() != "ALL":
            if highest_badge != badge.upper():
                continue

        verified_skills = [sk.skill.name for sk in s.skills if sk.is_verified and sk.skill]
        all_skills = [sk.skill.name for sk in s.skills if sk.skill]

        if verified_only and not verified_skills:
            continue

        if skill:
            skill_lower = skill.lower()
            if not any(skill_lower in sk_name.lower() for sk_name in all_skills):
                continue

        results.append({
            "student_id": s.id,
            "user_id": s.user_id,
            "full_name": s.user.full_name if s.user else "Candidate",
            "college_name": s.user.college_name if s.user else "Engineering Institute",
            "headline": s.headline or "Software Engineer Candidate",
            "department": s.department,
            "graduation_year": s.graduation_year,
            "cgpa": s.cgpa,
            "placement_readiness_score": s.placement_readiness_score,
            "highest_badge": highest_badge,
            "gold_badges_count": gold_count,
            "silver_badges_count": silver_count,
            "verified_skills": verified_skills,
            "all_skills": all_skills[:8],
            "certificates_count": len(s.certificates),
            "resume_url": s.resume_file_url,
            "github_url": s.github_url,
            "linkedin_url": s.linkedin_url
        })

    # Sort candidates by verified status and readiness score
    results.sort(
        key=lambda c: (1 if c["highest_badge"] == "GOLD" else (0.5 if c["highest_badge"] == "SILVER" else 0), c["placement_readiness_score"]),
        reverse=True
    )
    return results

@router.get("/candidate/{student_id}")
def get_candidate_credibility_card(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    certs_audit = []
    for c in student.certificates:
        certs_audit.append({
            "id": c.id,
            "title": c.title,
            "issuing_org": c.issuing_org,
            "badge_tier": c.badge_tier,
            "verification_score": c.verification_score,
            "verification_status": c.verification_status,
            "qr_detected": c.qr_detected,
            "file_hash_sha256": c.file_hash_sha256,
            "verified_at": c.verified_at
        })

    return {
        "candidate": {
            "student_id": student.id,
            "full_name": student.user.full_name if student.user else "Candidate",
            "email": student.user.email if student.user else "",
            "college_name": student.user.college_name if student.user else "Engineering College",
            "department": student.department,
            "graduation_year": student.graduation_year,
            "cgpa": student.cgpa,
            "placement_readiness_score": student.placement_readiness_score,
            "headline": student.headline,
            "bio": student.bio,
            "github_url": student.github_url,
            "linkedin_url": student.linkedin_url,
            "portfolio_url": student.portfolio_url,
            "resume_url": student.resume_file_url
        },
        "verified_credentials": certs_audit,
        "verified_skills": [s.skill.name for s in student.skills if s.is_verified and s.skill],
        "self_reported_skills": [s.skill.name for s in student.skills if not s.is_verified and s.skill],
        "credibility_multiplier": "2.4x (High Trust Profile backed by institutional credentials)"
    }
