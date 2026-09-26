import pytest
import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.core.security import get_password_hash, verify_password
from app.services.email_service import EmailService

client = TestClient(app)

def test_forgot_password_registered_email():
    """1. Forgot password with registered email returns 200 and generic message."""
    EmailService.latest_dev_emails.clear()
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": "student@careerlens.io"})
    assert res.status_code == 200
    assert "If an account exists with these details" in res.json()["message"]
    assert len(EmailService.latest_dev_emails) > 0
    assert EmailService.latest_dev_emails[-1]["to"] == "student@careerlens.io"


def test_forgot_password_registered_phone():
    """
    2. Forgot password with registered phone returns generic message,
    and sends reset link STRICTLY to the account's registered email (NOT SMS/OTP).
    """
    EmailService.latest_dev_emails.clear()
    # student's registered phone is 9876543210
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": "9876543210"})
    assert res.status_code == 200
    assert "If an account exists with these details" in res.json()["message"]
    assert len(EmailService.latest_dev_emails) > 0
    # Must send to the registered email address of the account
    assert EmailService.latest_dev_emails[-1]["to"] == "student@careerlens.io"
    assert "reset-password?token=" in EmailService.latest_dev_emails[-1]["reset_url"]


def test_forgot_password_unknown_email_generic_response():
    """3. Unknown email returns identical generic response (anti-enumeration)."""
    EmailService.latest_dev_emails.clear()
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": "nonexistent_random_user@careerlens.io"})
    assert res.status_code == 200
    assert "If an account exists with these details, a password reset link has been sent to the registered email address." == res.json()["message"]
    # No email should be sent for nonexistent user
    assert len(EmailService.latest_dev_emails) == 0


def test_forgot_password_unknown_phone_generic_response():
    """4. Unknown phone returns identical generic response (anti-enumeration)."""
    EmailService.latest_dev_emails.clear()
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": "9999999999"})
    assert res.status_code == 200
    assert "If an account exists with these details, a password reset link has been sent to the registered email address." == res.json()["message"]
    assert len(EmailService.latest_dev_emails) == 0


def test_reset_token_stored_as_hash():
    """5. Reset token is stored in the database ONLY as a SHA-256 hash."""
    EmailService.latest_dev_emails.clear()
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": "student@careerlens.io"})
    assert res.status_code == 200

    latest_email = EmailService.latest_dev_emails[-1]
    raw_token = latest_email["reset_url"].split("token=")[1]
    expected_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "student@careerlens.io").first()
        record = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.token_hash == expected_hash
        ).first()
        assert record is not None, "Token hash should be found in database"
        assert record.token_hash != raw_token, "Database must store hash, never raw token"
        assert len(record.token_hash) == 64
    finally:
        db.close()


def test_reset_token_expiration():
    """6. Reset token has an expiration timestamp of ~30 minutes."""
    EmailService.latest_dev_emails.clear()
    client.post("/api/v1/auth/forgot-password", json={"identifier": "student@careerlens.io"})
    raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    db = SessionLocal()
    try:
        record = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
        assert record is not None
        delta = record.expires_at - record.created_at
        assert 28 <= delta.total_seconds() / 60 <= 31
    finally:
        db.close()


def test_reset_token_single_use():
    """7. Reset token can only be used once."""
    db = SessionLocal()
    try:
        # Create test user
        uid = secrets.token_hex(4)
        test_email = f"single_use_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("InitialPass123!"),
            full_name=f"Single Use User {uid}",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        # Request reset
        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        # First reset: should succeed
        res1 = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "NewSecurePassword123!",
            "confirm_password": "NewSecurePassword123!"
        })
        assert res1.status_code == 200

        # Second reset with SAME token: must fail
        res2 = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!"
        })
        assert res2.status_code == 400
        assert "already been used" in res2.json()["detail"].lower()
    finally:
        db.close()


def test_valid_token_resets_password():
    """8. Valid token successfully resets password."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"valid_token_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("OldPassword123!"),
            full_name="Valid Token User",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        res = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "BrandNewPassword123!",
            "confirm_password": "BrandNewPassword123!"
        })
        assert res.status_code == 200
        assert "successfully" in res.json()["message"]

        db.refresh(user)
        assert verify_password("BrandNewPassword123!", user.password_hash)
        assert not verify_password("OldPassword123!", user.password_hash)
    finally:
        db.close()


def test_wrong_token_rejected():
    """9. Non-existent / fabricated token is rejected."""
    res = client.post("/api/v1/auth/reset-password", json={
        "token": "completely-invalid-bogus-token-12345",
        "new_password": "BrandNewPassword123!",
        "confirm_password": "BrandNewPassword123!"
    })
    assert res.status_code == 400
    assert "invalid or expired" in res.json()["detail"].lower()


def test_expired_token_rejected():
    """10. Expired token is rejected."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"expired_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("OldPassword123!"),
            full_name="Expired User",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        # Fabricate an expired token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expired_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() - timedelta(minutes=5),
            created_at=datetime.utcnow() - timedelta(minutes=35)
        )
        db.add(expired_record)
        db.commit()

        res = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "BrandNewPassword123!",
            "confirm_password": "BrandNewPassword123!"
        })
        assert res.status_code == 400
        assert "expired" in res.json()["detail"].lower()
    finally:
        db.close()


def test_password_mismatch_rejected():
    """11. Mismatch between new_password and confirm_password is rejected."""
    res = client.post("/api/v1/auth/reset-password", json={
        "token": "dummy-token",
        "new_password": "PasswordOne123!",
        "confirm_password": "PasswordDifferent123!"
    })
    assert res.status_code == 400
    assert "passwords do not match" in res.json()["detail"].lower()


def test_new_password_can_login_and_old_cannot():
    """12 & 13. New password can log in, and old password cannot log in."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"login_test_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("OriginalPass123!"),
            full_name="Login Test User",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        # Verify old password works
        res_old = client.post("/api/v1/auth/login", json={"email": test_email, "password": "OriginalPass123!"})
        assert res_old.status_code == 200

        # Request reset & apply new password
        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        res_reset = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "UpdatedPassword456!",
            "confirm_password": "UpdatedPassword456!"
        })
        assert res_reset.status_code == 200

        # 13. Old password CANNOT log in
        res_fail = client.post("/api/v1/auth/login", json={"email": test_email, "password": "OriginalPass123!"})
        assert res_fail.status_code == 401

        # 12. New password CAN log in
        res_success = client.post("/api/v1/auth/login", json={"email": test_email, "password": "UpdatedPassword456!"})
        assert res_success.status_code == 200
        assert res_success.json()["access_token"] is not None
    finally:
        db.close()


def test_reset_does_not_change_approval_status_or_role():
    """14 & 15. Password reset does not alter approval_status or role."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"role_status_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("SecretPass123!"),
            full_name="Role Status User",
            role="recruiter",
            approval_status="PENDING"
        )
        db.add(user)
        db.commit()

        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        res = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "NewSecretPass789!",
            "confirm_password": "NewSecretPass789!"
        })
        assert res.status_code == 200

        db.refresh(user)
        assert user.role == "recruiter", "Role must remain recruiter"
        assert user.approval_status == "PENDING", "Approval status must remain PENDING"
    finally:
        db.close()


def test_reset_token_and_password_not_leaked_in_api():
    """16. Reset tokens, hashes, and passwords are never returned in normal API responses."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"leak_test_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("InitialPass123!"),
            full_name="Leak Test User",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        EmailService.latest_dev_emails.clear()
        res_forgot = client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        body_forgot = res_forgot.text
        assert "token" not in body_forgot.lower()
        assert "hash" not in body_forgot.lower()
        assert "password" not in body_forgot.lower() or "password reset" in body_forgot.lower()

        # Reset response
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]
        res_reset = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "PasswordTest123!",
            "confirm_password": "PasswordTest123!"
        })
        body_reset = res_reset.text
        assert "token" not in body_reset.lower()
        assert "hash" not in body_reset.lower()
        assert "PasswordTest123!" not in body_reset
    finally:
        db.close()


def test_pending_account_remains_blocked_after_reset():
    """17. A PENDING account remains blocked from login after resetting password."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"pending_block_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("InitialPass123!"),
            full_name="Pending Block User",
            role="student",
            approval_status="PENDING"
        )
        db.add(user)
        db.commit()

        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        res_reset = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "NewPendingPass123!",
            "confirm_password": "NewPendingPass123!"
        })
        assert res_reset.status_code == 200

        # Login attempt must be 403 Forbidden because status is still PENDING
        res_login = client.post("/api/v1/auth/login", json={"email": test_email, "password": "NewPendingPass123!"})
        assert res_login.status_code == 403
        assert "pending" in res_login.json()["detail"].lower()
    finally:
        db.close()


def test_rejected_account_remains_blocked_after_reset():
    """18. A REJECTED account remains blocked from login after resetting password."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"rejected_block_{uid}@careerlens.io"
        user = User(
            email=test_email,
            password_hash=get_password_hash("InitialPass123!"),
            full_name="Rejected Block User",
            role="recruiter",
            approval_status="REJECTED"
        )
        db.add(user)
        db.commit()

        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_email})
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        res_reset = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "NewRejectedPass123!",
            "confirm_password": "NewRejectedPass123!"
        })
        assert res_reset.status_code == 200

        # Login attempt must be 403 Forbidden because status is still REJECTED
        res_login = client.post("/api/v1/auth/login", json={"email": test_email, "password": "NewRejectedPass123!"})
        assert res_login.status_code == 403
        assert "rejected" in res_login.json()["detail"].lower()
    finally:
        db.close()


def test_email_login_and_phone_login_after_reset():
    """19. Both email login AND phone login work with the new password after reset."""
    db = SessionLocal()
    try:
        uid = secrets.token_hex(4)
        test_email = f"dual_login_{uid}@careerlens.io"
        test_phone = f"98{secrets.randbelow(90000000) + 10000000}"

        user = User(
            email=test_email,
            phone_number=test_phone,
            password_hash=get_password_hash("StartingPass123!"),
            full_name="Dual Login User",
            role="student",
            approval_status="APPROVED"
        )
        db.add(user)
        db.commit()

        # Reset using phone number lookup
        EmailService.latest_dev_emails.clear()
        client.post("/api/v1/auth/forgot-password", json={"identifier": test_phone})
        # Dispatched to email
        assert EmailService.latest_dev_emails[-1]["to"] == test_email
        raw_token = EmailService.latest_dev_emails[-1]["reset_url"].split("token=")[1]

        # Reset password
        res_reset = client.post("/api/v1/auth/reset-password", json={
            "token": raw_token,
            "new_password": "FinalNewPassword123!",
            "confirm_password": "FinalNewPassword123!"
        })
        assert res_reset.status_code == 200

        # 1. Login with EMAIL + NEW PASSWORD
        res_email = client.post("/api/v1/auth/login", json={"email": test_email, "password": "FinalNewPassword123!"})
        assert res_email.status_code == 200
        assert res_email.json()["access_token"] is not None

        # 2. Login with PHONE + NEW PASSWORD
        res_phone = client.post("/api/v1/auth/login", json={"email": test_phone, "password": "FinalNewPassword123!"})
        assert res_phone.status_code == 200
        assert res_phone.json()["access_token"] is not None

        # 3. Old password fails with both
        assert client.post("/api/v1/auth/login", json={"email": test_email, "password": "StartingPass123!"}).status_code == 401
        assert client.post("/api/v1/auth/login", json={"email": test_phone, "password": "StartingPass123!"}).status_code == 401
    finally:
        db.close()


def test_platform_admin_reset_flow(admin_credentials):
    """Platform Admin can also use the forgot password flow."""
    admin_email = admin_credentials["email"]
    EmailService.latest_dev_emails.clear()
    res = client.post("/api/v1/auth/forgot-password", json={"identifier": admin_email})
    assert res.status_code == 200
    assert len(EmailService.latest_dev_emails) > 0
    assert EmailService.latest_dev_emails[-1]["to"] == admin_email
