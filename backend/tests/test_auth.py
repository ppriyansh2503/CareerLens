from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "CareerLens"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_demo_switcher():
    # Student switch
    res_student = client.post("/api/v1/auth/demo-switch/student")
    assert res_student.status_code == 200
    assert res_student.json()["role"] == "student"

    # Recruiter switch
    res_recruiter = client.post("/api/v1/auth/demo-switch/recruiter")
    assert res_recruiter.status_code == 200
    assert res_recruiter.json()["role"] == "recruiter"

    # College Admin switch
    res_college = client.post("/api/v1/auth/demo-switch/college_admin")
    assert res_college.status_code == 200
    assert res_college.json()["role"] == "college_admin"

def test_jobs_feed():
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) > 0
    # First job should have match score computed
    assert jobs[0]["match_score"] is not None

def test_bilingual_chat():
    res_hi = client.post("/api/v1/chat/message", json={"content": "Mujhe internship match score boost karna hai"})
    assert res_hi.status_code == 200
    data = res_hi.json()
    assert data["sender"] == "assistant"
    assert len(data["content"]) > 10

def test_student_registration_approval_and_login(admin_credentials):
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_email = f"rohan_{uid}@careerlens.io"
    reg_payload = {
        "email": test_email,
        "password": "Password123!",
        "full_name": "Rohan Das",
        "role": "student",
        "college_name": "Delhi Technological University",
        "department": "Electronics & Communication",
        "graduation_year": 2027,
        "cgpa": 8.85
    }
    # 1. Registration defaults to PENDING
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 200
    token_data = res.json()
    assert token_data["approval_status"] == "PENDING"
    student_id = token_data["user_id"]

    # 2. Login fails before admin approval with 403 Forbidden
    login_fail = client.post("/api/v1/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login_fail.status_code == 403
    assert "pending administrator approval" in login_fail.json()["detail"].lower()

    # 3. Platform Admin logs in and approves student
    admin_login = client.post("/api/v1/auth/login", json=admin_credentials)
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Verify student appears in admin pending students list
    pending_list = client.get("/api/v1/admin/approvals/students", headers=admin_headers)
    assert pending_list.status_code == 200
    assert any(s["id"] == student_id for s in pending_list.json())

    # Approve the student
    approve_res = client.post(
        f"/api/v1/admin/approvals/students/{student_id}",
        headers=admin_headers,
        json={"action": "APPROVE", "reason": "Verified college registration and roll number"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["approval_status"] == "APPROVED"

    # 4. Now approved student can log in successfully
    login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["approval_status"] == "APPROVED"
    assert "access_token" in login_data
    token = login_data["access_token"]

    # 5. Verify /me and student profile
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me = me_res.json()
    assert me["email"] == test_email
    assert me["role"] == "student"

    profile_res = client.get("/api/v1/profile/student", headers=headers)
    assert profile_res.status_code == 200
    prof = profile_res.json()
    assert prof["department"] == "Electronics & Communication"
    assert prof["graduation_year"] == 2027
    assert prof["cgpa"] == 8.85

def test_student_registration_rejection(admin_credentials):
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_email = f"priya_{uid}@careerlens.io"
    reg_payload = {
        "email": test_email,
        "password": "Password123!",
        "full_name": "Priya Test",
        "role": "student"
    }
    # 1. Register student -> PENDING
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 200
    student_id = res.json()["user_id"]

    # 2. Admin rejects student with reason
    admin_login = client.post("/api/v1/auth/login", json=admin_credentials)
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    # Rejection without reason fails (400)
    fail_reject = client.post(
        f"/api/v1/admin/approvals/students/{student_id}",
        headers=admin_headers,
        json={"action": "REJECT", "reason": ""}
    )
    assert fail_reject.status_code == 400

    # Rejection with reason succeeds
    reject_res = client.post(
        f"/api/v1/admin/approvals/students/{student_id}",
        headers=admin_headers,
        json={"action": "REJECT", "reason": "Institutional email verification failed"}
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["approval_status"] == "REJECTED"

    # 3. Login returns 403 Forbidden with rejected notice
    login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login_res.status_code == 403
    assert "account has been rejected" in login_res.json()["detail"].lower()

def test_recruiter_registration(admin_credentials):
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_email = f"recruiter_{uid}@apex.com"
    reg_payload = {
        "email": test_email,
        "password": "Password123!",
        "full_name": "Vikram Sethi",
        "role": "recruiter",
        "company_name": "Apex Innovations"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 200
    assert res.json()["approval_status"] == "PENDING"
    recruiter_id = res.json()["user_id"]

    # Login fails before approval
    login_fail = client.post("/api/v1/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login_fail.status_code == 403

    # Admin approves recruiter
    admin_login = client.post("/api/v1/auth/login", json=admin_credentials)
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    approve_res = client.post(
        f"/api/v1/admin/approvals/recruiters/{recruiter_id}",
        headers=admin_headers,
        json={"action": "APPROVE", "reason": "Verified CIN and corporate records"}
    )
    assert approve_res.status_code == 200

    # Login succeeds after approval
    login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["company_name"] == "Apex Innovations"

def test_cross_role_access_rejection():
    # Use canonical approved student
    student_res = client.post("/api/v1/auth/login", json={"email": "student@careerlens.io", "password": "password123"})
    assert student_res.status_code == 200
    student_token = student_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Recruiter endpoint
    recruiter_res = client.get("/api/v1/recruiter/candidates", headers=student_headers)
    assert recruiter_res.status_code == 403
    assert "recruiter privileges" in recruiter_res.json()["detail"].lower()

    # College analytics endpoint
    college_res = client.get("/api/v1/college/analytics", headers=student_headers)
    assert college_res.status_code == 403
    assert "college" in college_res.json()["detail"].lower()

def test_canonical_accounts_login_and_me(admin_credentials):
    """
    Regression test ensuring all 4 canonical accounts can authenticate,
    receive valid JWTs, and fetch their profile without HTTP 500 errors.
    """
    canonical_accounts = [
        ("student@careerlens.io", "password123", "student"),
        ("recruiter@careerlens.io", "password123", "recruiter"),
        ("college@careerlens.io", "password123", "college_admin"),
        (admin_credentials["email"], admin_credentials["password"], "platform_admin"),
    ]

    for email, password, expected_role in canonical_accounts:
        res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert res.status_code == 200, f"Login failed for {email}: {res.status_code} {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["role"] == expected_role
        assert data["approval_status"] == "APPROVED"
        assert "user_id" in data
        assert len(data["full_name"]) > 0

        # Verify /me endpoint returns user profile
        token = data["access_token"]
        me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200, f"/me failed for {email}: {me_res.status_code} {me_res.text}"
        me_data = me_res.json()
        assert me_data["email"] == email
        assert me_data["role"] == expected_role

def test_login_invalid_credentials_returns_401():
    """
    Ensure invalid password or unknown email returns 401 Unauthorized, never 500.
    """
    # Invalid password for existing user
    res_bad_pwd = client.post("/api/v1/auth/login", json={"email": "student@careerlens.io", "password": "wrongpassword"})
    assert res_bad_pwd.status_code == 401
    assert "incorrect email or password" in res_bad_pwd.json()["detail"].lower()

    # Unknown email
    res_unknown = client.post("/api/v1/auth/login", json={"email": "nonexistent_user@careerlens.io", "password": "password123"})
    assert res_unknown.status_code == 401
    assert "incorrect email or password" in res_unknown.json()["detail"].lower()

    # Old admin email must return 401
    res_old_admin = client.post("/api/v1/auth/login", json={"email": "admin@careerlens.io", "password": "password123"})
    assert res_old_admin.status_code == 401
    assert "incorrect email or password" in res_old_admin.json()["detail"].lower()


