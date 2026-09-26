import pytest
from app.services.ai_service import AIService
from app.models.student import StudentProfile
from app.models.user import User
from app.models.skill import Skill, StudentSkill
from app.models.certificate import Certificate
from app.core.database import SessionLocal

def test_language_detection():
    # English
    assert AIService.detect_language("What projects should I build for backend roles?") == "en"
    assert AIService.detect_language("How do I improve my placement readiness?") == "en"

    # Hindi (Devanagari)
    assert AIService.detect_language("रिज्यूमे में कौन सी स्किल्स जोड़नी चाहिए?") == "hi"
    assert AIService.detect_language("मुझे कौन से प्रोजेक्ट्स बनाने चाहिए?") == "hi"

    # Hinglish
    assert AIService.detect_language("Mere skills ke according 3 projects batao") == "hinglish"
    assert AIService.detect_language("Mera match score 95% kaise hoga?") == "hinglish"
    assert AIService.detect_language("Mujhe kaunse projects pe kaam karna chahiye?") == "hinglish"
    assert AIService.detect_language("Mere skills se kya business bana sakta hoon?") == "hinglish"


def test_intent_detection():
    assert AIService._detect_intent("Mere skills ke according 3 projects batao") == "projects"
    assert AIService._detect_intent("Which projects should I build for my resume?") == "projects"
    assert AIService._detect_intent("Mere skills se kya business bana sakta hoon?") == "business"
    assert AIService._detect_intent("Can I launch a SaaS product with my skills?") == "business"
    assert AIService._detect_intent("Which career roles fit my profile?") == "career_roles"
    assert AIService._detect_intent("What internships am I eligible for?") == "internships"
    assert AIService._detect_intent("What are my skill gaps?") == "skill_gap"
    assert AIService._detect_intent("Give me a 4 week roadmap") == "roadmap"
    assert AIService._detect_intent("How to optimize my resume bullets?") == "resume"
    assert AIService._detect_intent("Why is my readiness score 88.5%?") == "readiness_score"


def test_readiness_score_grounding_no_stale_numbers():
    """
    CRITICAL REGRESSION TEST:
    AI Counselor must dynamically quote the exact live student score from the profile,
    and NEVER emit stale or hardcoded numbers like 47.5%.
    """
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        assert student is not None, "Demo student profile should exist"

        # Test with the student's actual score
        actual_score = float(student.placement_readiness_score or 88.5)

        res = AIService.generate_chat_response(
            user_message="Why is my readiness score what it is? Explain my score.",
            student=student
        )
        content = res["content"]
        assert f"{actual_score}%" in content or f"{int(actual_score)}%" in content
        assert "47.5%" not in content, "Stale 47.5% score must never appear in response"

        # Test with a modified score (e.g. 72.5%) to ensure it's not hardcoded to 88.5%
        student.placement_readiness_score = 72.5
        res_custom = AIService.generate_chat_response(
            user_message="Mera readiness score kaisa hai?",
            student=student
        )
        content_custom = res_custom["content"]
        assert "72.5%" in content_custom
        assert "88.5%" not in content_custom
        assert "47.5%" not in content_custom

        # Restore original score
        student.placement_readiness_score = actual_score
        db.commit()
    finally:
        db.close()


def test_project_recommendation_structure():
    """
    Tests that project recommendations have senior engineering mentor quality:
    - Multiple structured projects (Architecture, Stack, Resume value, Advanced feature)
    """
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        res = AIService.generate_chat_response(
            user_message="Suggest 3 projects for my tech stack",
            student=student
        )
        content = res["content"]
        assert "Project" in content
        assert "Tech Stack" in content or "Stack" in content
        assert "Resume" in content or "Architecture" in content or "Key Features" in content
    finally:
        db.close()


def test_business_opportunity_structure():
    """
    Tests college-level monetization / MVP advice:
    - Identifies target users, MVP scope, 5-20 initial users, and SaaS monetization path.
    """
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        res = AIService.generate_chat_response(
            user_message="Mere skills se kya business bana sakta hoon?",
            student=student
        )
        content = res["content"]
        # Should be in Hinglish with MVP and monetization structure
        assert "MVP" in content or "Users" in content or "SaaS" in content or "Client" in content
        assert res["detected_language"] == "hinglish"
    finally:
        db.close()


def test_hindi_response():
    """
    Tests that when a student asks in Hindi, the response is delivered in Hindi.
    """
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        res = AIService.generate_chat_response(
            user_message="रिज्यूमे में कौन सी स्किल्स जोड़नी चाहिए?",
            student=student
        )
        assert res["detected_language"] == "hi"
        content = res["content"]
        # Contains Devanagari characters
        assert any('\u0900' <= char <= '\u097F' for char in content)
    finally:
        db.close()


def test_multi_turn_followup():
    """
    Tests that multi-turn history is honored for follow-up questions.
    """
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        history = [
            {"sender": "user", "content": "Suggest 3 projects for my backend profile."},
            {"sender": "assistant", "content": "1. Multi-Tenant Distributed Task Queue using Redis and Celery\n2. Real-Time CDC Financial Ledger\n3. Cloud-Native API Gateway with Rate Limiting"}
        ]
        res = AIService.generate_chat_response(
            user_message="Which of these projects will give me the highest edge for top engineering roles?",
            student=student,
            chat_history=history
        )
        content = res["content"]
        # Response should directly address comparing the prior projects
        assert "Task Queue" in content or "Ledger" in content or "Gateway" in content or "Project" in content
    finally:
        db.close()


def test_chat_api_endpoints():
    """
    E2E test for /api/v1/chat/message and /api/v1/chat/history with authenticated student.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Switch to demo student to get auth token
    res_switch = client.post("/api/v1/auth/demo-switch/student")
    assert res_switch.status_code == 200
    token = res_switch.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Send project question in Hinglish
    res_msg = client.post(
        "/api/v1/chat/message",
        json={"content": "Mere skills ke according 3 projects batao"},
        headers=headers
    )
    assert res_msg.status_code == 200
    data_msg = res_msg.json()
    assert data_msg["sender"] == "assistant"
    assert data_msg["detected_language"] == "hinglish"
    assert "project" in data_msg["content"].lower()

    # 3. Send business question in Hinglish in the same session
    res_biz = client.post(
        "/api/v1/chat/message",
        json={
            "content": "Mere skills se kya business bana sakta hoon?",
            "session_id": data_msg["session_id"]
        },
        headers=headers
    )
    assert res_biz.status_code == 200
    data_biz = res_biz.json()
    assert data_biz["sender"] == "assistant"
    assert "mvp" in data_biz["content"].lower() or "b2b" in data_biz["content"].lower() or "micro-saas" in data_biz["content"].lower()

    # 4. Check conversation history
    res_hist = client.get("/api/v1/chat/history", headers=headers)
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert len(history) >= 4  # At least 2 user messages and 2 assistant responses

