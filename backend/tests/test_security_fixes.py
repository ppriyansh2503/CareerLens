import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings, Settings, DEMO_SECRET_KEY
from app.core.database import SessionLocal
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate

client = TestClient(app)

@pytest.fixture(scope="module")
def student_auth():
    res = client.post("/api/v1/auth/demo-switch/student")
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def recruiter_auth():
    res = client.post("/api/v1/auth/demo-switch/recruiter")
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def college_auth():
    res = client.post("/api/v1/auth/demo-switch/college_admin")
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def admin_auth(admin_credentials):
    res = client.post("/api/v1/auth/login", json=admin_credentials)
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# FIX 1: REMOVE UNAUTHENTICATED STUDENT FALLBACK (Strict HTTP 401)
# ============================================================================
def test_unauthenticated_requests_receive_401():
    protected_endpoints = [
        ("GET", "/api/v1/profile/student"),
        ("GET", "/api/v1/profile/readiness"),
        ("GET", "/api/v1/jobs"),
        ("GET", "/api/v1/certificates"),
        ("POST", "/api/v1/chat/message"),
        ("GET", "/api/v1/college/analytics"),
        ("GET", "/api/v1/college/students"),
        ("GET", "/api/v1/recruiter/candidates"),
        ("GET", "/api/v1/admin/stats"),
        ("GET", "/api/v1/uploads/resumes/sample.pdf"),
        ("GET", "/api/v1/files/resumes/sample.pdf"),
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={"content": "test"})
        assert res.status_code == 401, f"{method} {path} should return 401 Unauthorized but returned {res.status_code}"


# ============================================================================
# FIX 2: SECURE/DISABLE DEMO ROLE SWITCHER
# ============================================================================
def test_demo_switch_platform_admin_blocked():
    res = client.post("/api/v1/auth/demo-switch/platform_admin")
    assert res.status_code == 403
    assert "platform_admin is not allowed" in res.json()["detail"]

def test_demo_switch_production_disabled():
    original_env = settings.ENVIRONMENT
    try:
        settings.ENVIRONMENT = "production"
        res = client.post("/api/v1/auth/demo-switch/student")
        assert res.status_code == 404
    finally:
        settings.ENVIRONMENT = original_env


# ============================================================================
# FIX 3: PREVENT PLATFORM_ADMIN SELF-REGISTRATION & REQUIRE APPROVAL
# ============================================================================
def test_platform_admin_registration_rejected():
    res = client.post("/api/v1/auth/register", json={
        "email": f"hacker_admin_{uuid.uuid4().hex[:6]}@careerlens.io",
        "password": "Password123!",
        "full_name": "Rogue Admin",
        "role": "platform_admin"
    })
    assert res.status_code in [400, 422]

def test_unapproved_platform_admin_rejected_in_get_current_admin():
    db = SessionLocal()
    try:
        unapproved_email = f"pending_admin_{uuid.uuid4().hex[:6]}@careerlens.io"
        user = User(
            email=unapproved_email,
            password_hash=get_password_hash("Password123!"),
            full_name="Pending Admin",
            role="platform_admin",
            approval_status="PENDING"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(subject=user.id, role="platform_admin")
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/v1/admin/stats", headers=headers)
        assert res.status_code == 403
        assert "pending administrator approval" in res.json()["detail"]
    finally:
        db.close()


# ============================================================================
# FIX 4: REMOVE DEFAULT PRODUCTION JWT SECRET FALLBACK
# ============================================================================
def test_production_secret_key_validation():
    # In production, default demo secret must raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=DEMO_SECRET_KEY
        )
    assert "SECRET_KEY must be set to a secure, custom secret in production" in str(exc_info.value)

    # In production, custom secret succeeds
    valid_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="production-super-strong-custom-secret-key-12345"
    )
    assert valid_settings.SECRET_KEY == "production-super-strong-custom-secret-key-12345"


# ============================================================================
# FIX 5: PROTECT UPLOADED RESUMES AND CERTIFICATES & PATH TRAVERSAL
# ============================================================================
def test_uploaded_files_access_control(student_auth, recruiter_auth, admin_auth):
    # Ensure sample resume exists on disk for testing
    resumes_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(resumes_dir, exist_ok=True)
    sample_filename = f"test_access_{uuid.uuid4().hex[:8]}.pdf"
    sample_file_path = os.path.join(resumes_dir, sample_filename)
    with open(sample_file_path, "wb") as f:
        f.write(b"%PDF-1.4\nTest Resume Content\n%%EOF")

    db = SessionLocal()
    try:
        # Create student 1
        s1_user = User(
            email=f"student1_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Student One",
            role="student",
            approval_status="APPROVED",
            college_name="College Alpha"
        )
        db.add(s1_user)
        db.commit()
        db.refresh(s1_user)

        s1_profile = StudentProfile(
            user_id=s1_user.id,
            resume_file_url=f"/uploads/resumes/{sample_filename}",
            placement_readiness_score=85.0
        )
        db.add(s1_profile)
        db.commit()
        db.refresh(s1_profile)

        # Create student 2 (unrelated)
        s2_user = User(
            email=f"student2_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Student Two",
            role="student",
            approval_status="APPROVED",
            college_name="College Beta"
        )
        db.add(s2_user)
        db.commit()
        db.refresh(s2_user)

        s1_token = create_access_token(subject=s1_user.id, role="student")
        s2_token = create_access_token(subject=s2_user.id, role="student")

        s1_headers = {"Authorization": f"Bearer {s1_token}"}
        s2_headers = {"Authorization": f"Bearer {s2_token}"}

        # 1. Unauthenticated request -> 401
        res_unauth = client.get(f"/uploads/resumes/{sample_filename}")
        assert res_unauth.status_code == 401

        # 2. Student 2 attempting to view Student 1's resume -> 403 Forbidden
        res_s2 = client.get(f"/uploads/resumes/{sample_filename}", headers=s2_headers)
        assert res_s2.status_code == 403
        assert "do not have permission" in res_s2.json()["detail"]

        # 3. Student 1 viewing their own resume -> 200 OK
        res_s1 = client.get(f"/uploads/resumes/{sample_filename}", headers=s1_headers)
        assert res_s1.status_code == 200
        assert b"%PDF-1.4" in res_s1.content

        # 4. Recruiter viewing student's resume -> 200 OK
        res_rec = client.get(f"/uploads/resumes/{sample_filename}", headers=recruiter_auth)
        assert res_rec.status_code == 200

        # 5. Platform Admin viewing student's resume -> 200 OK
        res_adm = client.get(f"/uploads/resumes/{sample_filename}", headers=admin_auth)
        assert res_adm.status_code == 200

        # 6. Path traversal attempt -> 400 or 404
        res_traversal = client.get("/uploads/resumes/..%2F..%2Fcareerlens.db", headers=admin_auth)
        assert res_traversal.status_code in [400, 404]

    finally:
        db.close()
        if os.path.exists(sample_file_path):
            os.remove(sample_file_path)


# ============================================================================
# FIX 6: SECURE UPLOAD FILENAMES AND TYPES (Magic Bytes & Signatures)
# ============================================================================
def test_upload_file_magic_bytes_validation(student_auth):
    # Fake PDF (text file with .pdf extension)
    fake_pdf = io.BytesIO(b"Hello world, I am not a real PDF file!")
    res_fake_pdf = client.post(
        "/api/v1/resume/upload",
        files={"file": ("fake_resume.pdf", fake_pdf, "application/pdf")},
        headers=student_auth
    )
    assert res_fake_pdf.status_code == 400
    assert "not a valid PDF document" in res_fake_pdf.json()["detail"]

    # Valid PDF signature
    valid_pdf = io.BytesIO(b"%PDF-1.4\nCandidate: Valid Candidate\nSkills: Python, FastAPI\n%%EOF")
    res_valid_pdf = client.post(
        "/api/v1/resume/upload",
        files={"file": ("valid_resume.pdf", valid_pdf, "application/pdf")},
        headers=student_auth
    )
    assert res_valid_pdf.status_code == 200

    # Fake image for certificate (plain text with .png extension)
    fake_img = io.BytesIO(b"This is fake PNG image data that should fail PIL verification")
    res_fake_img = client.post(
        "/api/v1/certificates/upload",
        files={"file": ("fake_cert.png", fake_img, "image/png")},
        data={"title": "Fake Certificate", "issuing_org": "Unknown"},
        headers=student_auth
    )
    assert res_fake_img.status_code == 400
    assert "Invalid file format or corrupted image" in res_fake_img.json()["detail"]


# ============================================================================
# FIX 7: ENFORCE MAXIMUM UPLOAD SIZE (HTTP 413)
# ============================================================================
def test_upload_file_size_limit_enforced(student_auth):
    # Create an in-memory buffer > 10MB
    oversized_bytes = b"%PDF-" + (b"A" * (10 * 1024 * 1024 + 100))
    oversized_file = io.BytesIO(oversized_bytes)

    res_large = client.post(
        "/api/v1/resume/upload",
        files={"file": ("huge_resume.pdf", oversized_file, "application/pdf")},
        headers=student_auth
    )
    assert res_large.status_code == 413
    assert "exceeds maximum allowed size" in res_large.json()["detail"]


# ============================================================================
# FIX 8: COLLEGE DATA ISOLATION (Multi-tenant)
# ============================================================================
def test_college_data_isolation():
    db = SessionLocal()
    try:
        col_a_name = f"College_Alpha_{uuid.uuid4().hex[:6]}"
        col_b_name = f"College_Beta_{uuid.uuid4().hex[:6]}"

        # College A Admin & Student
        admin_a = User(
            email=f"admin_a_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Admin Alpha",
            role="college_admin",
            approval_status="APPROVED",
            college_name=col_a_name
        )
        student_a = User(
            email=f"student_a_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Student Alpha",
            role="student",
            approval_status="APPROVED",
            college_name=col_a_name
        )
        db.add_all([admin_a, student_a])
        db.commit()
        db.refresh(admin_a)
        db.refresh(student_a)

        prof_a = StudentProfile(
            user_id=student_a.id,
            placement_readiness_score=90.0,
            department="CSE"
        )
        db.add(prof_a)

        # College B Admin & Student
        admin_b = User(
            email=f"admin_b_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Admin Beta",
            role="college_admin",
            approval_status="APPROVED",
            college_name=col_b_name
        )
        student_b = User(
            email=f"student_b_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Student Beta",
            role="student",
            approval_status="APPROVED",
            college_name=col_b_name
        )
        db.add_all([admin_b, student_b])
        db.commit()
        db.refresh(admin_b)
        db.refresh(student_b)

        prof_b = StudentProfile(
            user_id=student_b.id,
            placement_readiness_score=75.0,
            department="ECE"
        )
        db.add(prof_b)
        db.commit()

        # Admin A calls /students
        token_a = create_access_token(subject=admin_a.id, role="college_admin")
        res_a = client.get("/api/v1/college/students", headers={"Authorization": f"Bearer {token_a}"})
        assert res_a.status_code == 200
        roster_a = res_a.json()
        student_emails_a = [s["email"] for s in roster_a]
        assert student_a.email in student_emails_a
        assert student_b.email not in student_emails_a

        # Admin B calls /students
        token_b = create_access_token(subject=admin_b.id, role="college_admin")
        res_b = client.get("/api/v1/college/students", headers={"Authorization": f"Bearer {token_b}"})
        assert res_b.status_code == 200
        roster_b = res_b.json()
        student_emails_b = [s["email"] for s in roster_b]
        assert student_b.email in student_emails_b
        assert student_a.email not in student_emails_b

        # Analytics isolation
        analytics_a = client.get("/api/v1/college/analytics", headers={"Authorization": f"Bearer {token_a}"}).json()
        assert analytics_a["institution_name"] == col_a_name
        assert analytics_a["total_enrolled_students"] == 1

    finally:
        db.close()


# ============================================================================
# FIX 9: REMOVE STUDENTPROFILE.FIRST() FALLBACKS (Return HTTP 404)
# ============================================================================
def test_no_student_profile_fallback_returns_404():
    db = SessionLocal()
    try:
        orphan_user = User(
            email=f"orphan_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Orphan Student",
            role="student",
            approval_status="APPROVED"
        )
        db.add(orphan_user)
        db.commit()
        db.refresh(orphan_user)

        orphan_token = create_access_token(subject=orphan_user.id, role="student")
        headers = {"Authorization": f"Bearer {orphan_token}"}

        # Profile endpoint must return 404, not demo student's profile
        res_prof = client.get("/api/v1/profile/student", headers=headers)
        assert res_prof.status_code == 404
        assert "not found" in res_prof.json()["detail"].lower()

        # Matching endpoint must return 404, not demo student's match score
        res_match = client.get("/api/v1/matching/job/1", headers=headers)
        assert res_match.status_code == 404

        # Resume upload must return 404
        pdf_bytes = io.BytesIO(b"%PDF-1.4\nTest\n%%EOF")
        res_up = client.post(
            "/api/v1/resume/upload",
            files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
            headers=headers
        )
        assert res_up.status_code == 404

    finally:
        db.close()


# ============================================================================
# FIX 10: PROTECT GET /api/v1/certificates/{cert_id}/audit WITH AUTH & RBAC
# ============================================================================
def test_certificate_audit_rbac_protection(recruiter_auth, admin_auth):
    db = SessionLocal()
    try:
        cert = db.query(Certificate).first()
        assert cert is not None, "At least one seed certificate should exist"
        cert_id = cert.id
        owner_user_id = cert.student.user_id

        # 1. Unauthenticated request -> 401
        res_unauth = client.get(f"/api/v1/certificates/{cert_id}/audit")
        assert res_unauth.status_code == 401

        # 2. Unrelated student -> 403 Forbidden
        other_user = User(
            email=f"unrelated_{uuid.uuid4().hex[:6]}@careerlens.io",
            password_hash=get_password_hash("Password123!"),
            full_name="Unrelated Student",
            role="student",
            approval_status="APPROVED"
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_token = create_access_token(subject=other_user.id, role="student")
        res_other = client.get(
            f"/api/v1/certificates/{cert_id}/audit",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert res_other.status_code == 403
        assert "permission" in res_other.json()["detail"].lower()

        # 3. Owner student -> 200 OK
        owner_token = create_access_token(subject=owner_user_id, role="student")
        res_owner = client.get(
            f"/api/v1/certificates/{cert_id}/audit",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert res_owner.status_code == 200
        assert "certificate" in res_owner.json()

        # 4. Approved Recruiter -> 200 OK
        res_rec = client.get(
            f"/api/v1/certificates/{cert_id}/audit",
            headers=recruiter_auth
        )
        assert res_rec.status_code == 200

        # 5. Platform Admin -> 200 OK
        res_adm = client.get(
            f"/api/v1/certificates/{cert_id}/audit",
            headers=admin_auth
        )
        assert res_adm.status_code == 200

    finally:
        db.close()
