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

    res_prior_pwd = client.post("/api/v1/auth/login", json={"email": admin_credentials["email"], "password": "CareerLens#SuperAdmin2026!"})
    assert res_prior_pwd.status_code == 401, "Prior admin password must fail"

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

def test_admin_change_password_rbac(tokens, admin_credentials):
    # 1. Unauthenticated request must return 401
    res_unauth = client.post("/api/v1/admin/change-password", json={
        "current_password": "any",
        "new_password": "anypassword123",
        "confirm_password": "anypassword123"
    })
    assert res_unauth.status_code == 401

    # 2. Non-admin roles (student, recruiter, college) must return 403 Forbidden
    for role in ["student", "recruiter", "college"]:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        res_forbidden = client.post("/api/v1/admin/change-password", headers=headers, json={
            "current_password": "password123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        })
        assert res_forbidden.status_code == 403, f"{role} should receive 403 Forbidden"

def test_admin_change_password_validation_errors(tokens, admin_credentials):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    curr_pwd = admin_credentials["password"]

    # 1. Wrong current password -> 401
    res_wrong_curr = client.post("/api/v1/admin/change-password", headers=headers, json={
        "current_password": "WrongCurrentPassword123!",
        "new_password": "ValidNewPassword123!",
        "confirm_password": "ValidNewPassword123!"
    })
    assert res_wrong_curr.status_code == 401
    assert "incorrect" in res_wrong_curr.json()["detail"].lower()

    # 2. Password mismatch -> 400
    res_mismatch = client.post("/api/v1/admin/change-password", headers=headers, json={
        "current_password": curr_pwd,
        "new_password": "ValidNewPassword123!",
        "confirm_password": "MismatchPassword123!"
    })
    assert res_mismatch.status_code == 400
    assert "match" in res_mismatch.json()["detail"].lower()

    # 3. Short password (< 6 chars) -> 400
    res_short = client.post("/api/v1/admin/change-password", headers=headers, json={
        "current_password": curr_pwd,
        "new_password": "123",
        "confirm_password": "123"
    })
    assert res_short.status_code == 400
    assert "6 characters" in res_short.json()["detail"]

    # 4. Same as current password -> 400
    res_same = client.post("/api/v1/admin/change-password", headers=headers, json={
        "current_password": curr_pwd,
        "new_password": curr_pwd,
        "confirm_password": curr_pwd
    })
    assert res_same.status_code == 400
    assert "identical" in res_same.json()["detail"].lower()

def test_admin_change_password_success_and_audit(tokens, admin_credentials):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    curr_pwd = admin_credentials["password"]
    admin_email = admin_credentials["email"]
    temp_pwd = "TempRotated#AdminPass99"

    try:
        # 1. Successful password change
        res_change = client.post("/api/v1/admin/change-password", headers=headers, json={
            "current_password": curr_pwd,
            "new_password": temp_pwd,
            "confirm_password": temp_pwd
        })
        assert res_change.status_code == 200
        assert res_change.json()["status"] == "success"
        assert "changed successfully" in res_change.json()["message"]

        # 2. Old password must fail
        res_old_login = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": curr_pwd
        })
        assert res_old_login.status_code == 401

        # 3. New password must succeed
        res_new_login = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": temp_pwd
        })
        assert res_new_login.status_code == 200
        new_token = res_new_login.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # 4. Audit log entry recorded and verified
        res_audit = client.get("/api/v1/admin/audit-logs", headers=new_headers)
        assert res_audit.status_code == 200
        logs = res_audit.json()
        pwd_change_logs = [l for l in logs if l["action"] == "ADMIN_PASSWORD_CHANGED"]
        assert len(pwd_change_logs) > 0
        latest_pwd_log = pwd_change_logs[0]
        assert latest_pwd_log["target_type"] == "platform_admin"
        assert curr_pwd not in (latest_pwd_log["details"] or "")
        assert temp_pwd not in (latest_pwd_log["details"] or "")

    finally:
        # 5. Restore original password so test suite and demo logins remain consistent
        # Log in with temp_pwd if needed to get active token
        res_active_login = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": temp_pwd
        })
        if res_active_login.status_code == 200:
            active_token = res_active_login.json()["access_token"]
            res_restore = client.post("/api/v1/admin/change-password", headers={"Authorization": f"Bearer {active_token}"}, json={
                "current_password": temp_pwd,
                "new_password": curr_pwd,
                "confirm_password": curr_pwd
            })
            assert res_restore.status_code == 200

