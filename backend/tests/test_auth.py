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
