import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.certificate import Certificate
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def tokens():
    # Login as student, recruiter, college_admin, admin
    student_res = client.post("/api/v1/auth/login", json={"email": "student@careerlens.io", "password": "password123"})
    recruiter_res = client.post("/api/v1/auth/login", json={"email": "recruiter@careerlens.io", "password": "password123"})
    college_res = client.post("/api/v1/auth/login", json={"email": "college@careerlens.io", "password": "password123"})
    admin_res = client.post("/api/v1/auth/login", json={"email": "admin@careerlens.io", "password": "password123"})

    return {
        "student": student_res.json()["access_token"],
        "recruiter": recruiter_res.json()["access_token"],
        "college": college_res.json()["access_token"],
        "admin": admin_res.json()["access_token"],
    }

def test_admin_rbac_forbidden_for_non_admins(tokens):
    # Non-admins should receive 403 Forbidden
    for role in ["student", "recruiter", "college"]:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        res = client.get("/api/v1/admin/stats", headers=headers)
        assert res.status_code == 403, f"{role} should be forbidden from admin stats: {res.text}"

        res_certs = client.get("/api/v1/admin/certificates/pending", headers=headers)
        assert res_certs.status_code == 403

        res_recs = client.get("/api/v1/admin/approvals/recruiters", headers=headers)
        assert res_recs.status_code == 403

def test_admin_stats(tokens):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    res = client.get("/api/v1/admin/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "pending_certificates_count" in data
    assert "verified_certificates_count" in data
    assert "flagged_certificates_count" in data
    assert data["total_users"] > 0

def test_admin_certificate_review_flow(tokens):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    res = client.get("/api/v1/admin/certificates/pending", headers=headers)
    assert res.status_code == 200
    certs = res.json()
    assert len(certs) > 0
    target_cert = certs[0]

    # Test rejection without reason fails (400)
    reject_fail = client.post(
        f"/api/v1/admin/certificates/{target_cert['id']}/review",
        headers=headers,
        json={"action": "REJECT", "reason": ""}
    )
    assert reject_fail.status_code == 400

    # Test approval
    approve_res = client.post(
        f"/api/v1/admin/certificates/{target_cert['id']}/review",
        headers=headers,
        json={"action": "APPROVE", "reason": "Inspected institutional signature and confirmed authentic"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["verification_status"] == "VERIFIED"
    assert approve_res.json()["admin_review_status"] == "APPROVED"

def test_recruiter_and_college_approval_flow(tokens):
    import uuid
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    
    # 1. Register a new pending recruiter
    unique_email = f"pending_recruiter_{uuid.uuid4().hex[:8]}@test.com"
    reg_rec = client.post("/api/v1/auth/register", json={
        "full_name": "Pending Recruiter Test",
        "email": unique_email,
        "password": "password123",
        "role": "recruiter",
        "company_name": "Pending HR Ltd"
    })
    assert reg_rec.status_code == 200
    rec_token = reg_rec.json()["access_token"]
    rec_user_id = reg_rec.json()["user_id"]
    assert reg_rec.json()["approval_status"] == "PENDING"

    # Pending recruiter attempts to post job -> gets 403 Forbidden!
    job_post_fail = client.post("/api/v1/jobs/", headers={"Authorization": f"Bearer {rec_token}"}, json={
        "title": "Backend Intern",
        "company_name": "Pending HR Ltd",
        "location": "Remote",
        "job_type": "internship",
        "stipend_or_salary": "₹30,000",
        "description": "Building APIs",
        "skills": ["Python"]
    })
    assert job_post_fail.status_code == 403
    assert "pending platform admin approval" in job_post_fail.json()["detail"]

    # Admin approves the recruiter
    approve_rec = client.post(
        f"/api/v1/admin/approvals/recruiters/{rec_user_id}",
        headers=headers,
        json={"action": "APPROVE", "reason": "Verified GST and corporate domain"}
    )
    assert approve_rec.status_code == 200
    assert approve_rec.json()["approval_status"] == "APPROVED"

    # Now approved recruiter can post job!
    job_post_ok = client.post("/api/v1/jobs/", headers={"Authorization": f"Bearer {rec_token}"}, json={
        "title": "Backend Intern",
        "company_name": "Pending HR Ltd",
        "location": "Remote",
        "job_type": "internship",
        "stipend_or_salary": "₹30,000",
        "description": "Building APIs",
        "skills": ["Python"]
    })
    assert job_post_ok.status_code == 200

def test_audit_logs_retrieval(tokens):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    res = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert any(log["action"] in ["APPROVE_CERTIFICATE", "APPROVE_RECRUITER", "SYSTEM_INIT"] for log in logs)
