import pytest
from app.core.database import SessionLocal
from app.models.student import StudentProfile
from app.models.job import Job
from app.services.matching_engine import MatchingEngine

def test_explainable_match_calculation():
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        job = db.query(Job).first()
        
        assert student is not None
        assert job is not None

        match = MatchingEngine.calculate_match(student, job)
        
        assert "overall_score" in match
        assert match["overall_score"] >= 0.0 and match["overall_score"] <= 100.0
        assert "score_breakdown" in match
        assert "verified_skills_component" in match["score_breakdown"]
        assert "unverified_skills_component" in match["score_breakdown"]
        assert "skill_analysis" in match
        assert "matched_verified_skills" in match["skill_analysis"]
        assert "missing_critical_skills" in match["skill_analysis"]
        assert "readiness_verdict" in match

        # Test roadmap generation
        roadmap = MatchingEngine.generate_learning_roadmap(student, job)
        assert roadmap["job_id"] == job.id
        assert len(roadmap["weeks"]) == 4
        assert roadmap["weeks"][0]["week_number"] == 1
    finally:
        db.close()
