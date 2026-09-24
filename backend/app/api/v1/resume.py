import os
import shutil
from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.student import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.services.resume_parser import ResumeParser
from app.services.skill_service import get_or_create_skill

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")

    # Save file
    file_name = f"student_{profile.id}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, "resumes", file_name)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse resume
    parsed = ResumeParser.parse_resume(save_path)

    # Update profile
    try:
        profile.resume_file_url = f"/uploads/resumes/{file_name}"
        profile.resume_raw_text = parsed["raw_text"][:5000]
        
        details = parsed.get("profile_details", {})
        if details.get("github_url") and not profile.github_url:
            profile.github_url = details["github_url"]
        if details.get("linkedin_url") and not profile.linkedin_url:
            profile.linkedin_url = details["linkedin_url"]
        if parsed.get("headline"):
            profile.headline = parsed["headline"]

        # Save extracted skills idempotently
        newly_added_skills = []
        for skill_info in parsed.get("extracted_skills", []):
            skill_name = skill_info["name"]
            category = skill_info.get("category", "technical")
            
            skill = get_or_create_skill(db, skill_name, category)

            # Check if student already has this skill
            existing_ss = db.query(StudentSkill).filter(
                StudentSkill.student_id == profile.id,
                StudentSkill.skill_id == skill.id
            ).first()

            if not existing_ss:
                st_skill = StudentSkill(
                    student_id=profile.id,
                    skill_id=skill.id,
                    proficiency="intermediate",
                    source="resume",
                    is_verified=False
                )
                db.add(st_skill)
                newly_added_skills.append(skill.name)

        db.commit()

        # Recalculate readiness
        total_skills = len(profile.skills)
        verified_skills = sum(1 for s in profile.skills if s.is_verified)
        profile.placement_readiness_score = min(95.0, 25.0 + (verified_skills * 8.0) + (total_skills * 2.5))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save resume skills: {str(e)}")

    return {
        "status": "success",
        "message": f"Resume parsed successfully! Extracted {len(parsed['extracted_skills'])} skills.",
        "headline": profile.headline,
        "extracted_skills": parsed["extracted_skills"],
        "new_skills_added": newly_added_skills,
        "readiness_score": profile.placement_readiness_score
    }
