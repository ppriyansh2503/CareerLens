import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.skill import Skill
from app.models.student import StudentProfile
from app.services.skill_service import normalize_skill_name, get_or_create_skill

client = TestClient(app)

def test_normalize_skill_name():
    assert normalize_skill_name("Git / GitHub") == "gitgithub"
    assert normalize_skill_name("git / github") == "gitgithub"
    assert normalize_skill_name("Next.js") == "nextjs"
    assert normalize_skill_name("CI/CD Pipelines") == "cicdpipelines"
    assert normalize_skill_name("Go (Golang)") == "gogolang"
    assert normalize_skill_name("Python") == "python"

def test_get_or_create_skill_idempotence():
    db = SessionLocal()
    try:
        # Existing seeded skill 'Git / GitHub'
        existing = db.query(Skill).filter(Skill.name == "Git / GitHub").first()
        assert existing is not None

        # Fetch with exact name
        s1 = get_or_create_skill(db, "Git / GitHub")
        assert s1.id == existing.id

        # Fetch with different casing and spacing
        s2 = get_or_create_skill(db, "git / github")
        assert s2.id == existing.id

        # Fetch with slashes variation
        s3 = get_or_create_skill(db, "Git/GitHub")
        assert s3.id == existing.id

        # Ensure no duplicates were inserted
        all_git_skills = db.query(Skill).filter(Skill.normalized_name == "gitgithub").all()
        assert len(all_git_skills) == 1
    finally:
        db.close()

def test_resume_upload_with_existing_skills():
    # Login as demo student to get token
    auth_res = client.post("/api/v1/auth/demo-switch/student")
    assert auth_res.status_code == 200
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Resume text containing already-existing skills like 'Git / GitHub', 'Python', 'AWS', etc.
    resume_content = b"""%PDF-1.4
Candidate: Aarav Sharma
Email: aarav.sharma@example.com
GitHub: github.com/aarav-sharma-dev
LinkedIn: linkedin.com/in/aarav-sharma
Core Skills: Git / GitHub, Python, FastAPI, Docker, AWS, React, PostgreSQL, Redis, Linux
Education: IIIT Delhi, B.Tech CSE (2026), CGPA 8.8
%%EOF
"""
    file_payload = ("test_resume.pdf", io.BytesIO(resume_content), "application/pdf")
    
    # First upload
    response1 = client.post(
        "/api/v1/resume/upload",
        files={"file": file_payload},
        headers=headers
    )
    assert response1.status_code == 200, f"Upload failed: {response1.text}"
    data1 = response1.json()
    assert data1["status"] == "success"
    
    # Check that Git / GitHub was extracted
    extracted_names = [s["name"] for s in data1["extracted_skills"]]
    assert "Git / GitHub" in extracted_names

    # Second upload of the exact same resume (idempotency test)
    file_payload2 = ("test_resume.pdf", io.BytesIO(resume_content), "application/pdf")
    response2 = client.post(
        "/api/v1/resume/upload",
        files={"file": file_payload2},
        headers=headers
    )
    assert response2.status_code == 200, f"Repeated upload failed: {response2.text}"
    data2 = response2.json()
    assert data2["status"] == "success"

    # Verify skills table still has only 1 Git / GitHub record
    db = SessionLocal()
    try:
        git_skills = db.query(Skill).filter(Skill.name == "Git / GitHub").all()
        assert len(git_skills) == 1
    finally:
        db.close()
