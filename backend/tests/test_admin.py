import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.certificate import Certificate
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def tokens(admin_credentials):
    # Login as student, recruiter, college_admin, admin
    student_res = client.post("/api/v1/auth/login", json={"email": "student@careerlens.io", "password": "password123"})
    recruiter_res = client.post("/api/v1/auth/login", json={"email": "recruiter@careerlens.io", "password": "password123"})
    college_res = client.post("/api/v1/auth/login", json={"email": "college@careerlens.io", "password": "password123"})
    admin_res = client.post("/api/v1/auth/login", json=admin_credentials)

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
    assert "pending_students_count" in data
    assert "pending_recruiters_count" in data
    assert "pending_colleges_count" in data
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

    # 2. Register a new pending college
    col_email = f"pending_college_{uuid.uuid4().hex[:8]}@test.edu"
    reg_col = client.post("/api/v1/auth/register", json={
        "full_name": "Dean Placement",
        "email": col_email,
        "password": "password123",
        "role": "college_admin",
        "college_name": "National Engineering Institute"
    })
    assert reg_col.status_code == 200
    col_user_id = reg_col.json()["user_id"]
    assert reg_col.json()["approval_status"] == "PENDING"

    # Pending college cannot login
    col_login_fail = client.post("/api/v1/auth/login", json={"email": col_email, "password": "password123"})
    assert col_login_fail.status_code == 403

    # Admin approves college
    approve_col = client.post(
        f"/api/v1/admin/approvals/colleges/{col_user_id}",
        headers=headers,
        json={"action": "APPROVE", "reason": "Institutional affiliation and UGC accreditation verified"}
    )
    assert approve_col.status_code == 200
    assert approve_col.json()["approval_status"] == "APPROVED"

    # College can now log in
    col_login_ok = client.post("/api/v1/auth/login", json={"email": col_email, "password": "password123"})
    assert col_login_ok.status_code == 200
    assert col_login_ok.json()["approval_status"] == "APPROVED"

def test_audit_logs_retrieval(tokens):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    res = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert any(log["action"] in ["APPROVE_CERTIFICATE", "APPROVE_RECRUITER", "APPROVE_COLLEGE", "SYSTEM_INIT"] for log in logs)

def test_admin_credential_rotation(admin_credentials):
    # 1. Old admin credentials must fail
    res_old = client.post("/api/v1/auth/login", json={"email": "admin@careerlens.io", "password": "password123"})
    assert res_old.status_code == 401, "Old admin email must not work"

    res_old_mix = client.post("/api/v1/auth/login", json={"email": "admin@careerlens.io", "password": admin_credentials["password"]})
    assert res_old_mix.status_code == 401

    res_new_bad_pwd = client.post("/api/v1/auth/login", json={"email": admin_credentials["email"], "password": "password123"})
    assert res_new_bad_pwd.status_code == 401

    # 2. New credentials must succeed
    res_new = client.post("/api/v1/auth/login", json=admin_credentials)
    assert res_new.status_code == 200
    new_data = res_new.json()
    assert new_data["role"] == "platform_admin"
    assert new_data["approval_status"] == "APPROVED"
    assert "access_token" in new_data
    token = new_data["access_token"]

    # 3. New token can access admin protected endpoints
    res_stats = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res_stats.status_code == 200
    assert "total_users" in res_stats.json()

    # 4. Demo switcher for platform_admin works
    res_demo = client.post("/api/v1/auth/demo-switch/platform_admin")
    assert res_demo.status_code == 200
    assert res_demo.json()["role"] == "platform_admin"
