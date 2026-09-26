import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.models.student import StudentProfile
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse
)
from app.services.email_service import EmailService

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    phone = user_in.phone_number.strip() if user_in.phone_number else None
    if phone:
        existing_phone = db.query(User).filter(User.phone_number == phone).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    role = user_in.role.strip().lower()
    if role not in ["student", "recruiter", "college_admin", "platform_admin"]:
        role = "student"

    # All newly registered users start in PENDING status until approved by platform admin
    approval_status = "PENDING"

    user = User(
        email=email,
        phone_number=phone,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name.strip(),
        role=role,
        approval_status=approval_status,
        college_name=user_in.college_name.strip() if user_in.college_name else None,
        company_name=user_in.company_name.strip() if user_in.company_name else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.role == "student":
        profile = StudentProfile(
            user_id=user.id,
            headline=f"Student at {user.college_name}" if user.college_name else "Aspiring Software Engineer",
            department=user_in.department.strip() if user_in.department else "Computer Science & Engineering",
            graduation_year=user_in.graduation_year or 2026,
            cgpa=user_in.cgpa or 8.0,
            placement_readiness_score=35.0
        )
        db.add(profile)
        db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "approval_status": user.approval_status,
        "user_id": user.id,
        "full_name": user.full_name
    }

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    identifier = login_in.email.strip()
    user = db.query(User).filter(
        (User.email == identifier.lower()) | (User.phone_number == identifier)
    ).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Platform Admin is permanently APPROVED. Non-admin accounts require admin approval.
    if user.role != "platform_admin":
        curr_status = getattr(user, "approval_status", "APPROVED") or "APPROVED"
        if curr_status == "REJECTED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been rejected. Contact the administrator."
            )
        elif curr_status == "PENDING":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending administrator approval."
            )

    role = user.role or "student"
    full_name = user.full_name or user.email.split("@")[0].capitalize()
    approval_status = getattr(user, "approval_status", "APPROVED") or "APPROVED"
    token = create_access_token(subject=user.id, role=role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "approval_status": approval_status,
        "user_id": user.id,
        "full_name": full_name
    }

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Forgot Password request.
    Accepts registered Email OR Phone Number.
    Strict Security:
    - Never reveals account existence (anti-enumeration).
    - If user exists, reset link is sent ONLY to their registered email address.
    - Token is single-use, cryptographically random, and stored only as a SHA-256 hash.
    - Expiration is 30 minutes.
    """
    identifier = req.identifier.strip()
    generic_msg = (
        "If an account exists with these details, a password reset link has been "
        "sent to the registered email address."
    )

    user = db.query(User).filter(
        (User.email == identifier.lower()) | (User.phone_number == identifier)
    ).first()

    if user:
        now = datetime.utcnow()

        # Invalidate any prior unused reset tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at == None
        ).update({"used_at": now})
        db.commit()

        # Generate cryptographically secure random token and SHA-256 hash
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = now + timedelta(minutes=30)

        # Store only the SHA-256 hash in database
        reset_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=now
        )
        db.add(reset_record)
        db.commit()

        # Dispatch reset link strictly to the user's registered email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        EmailService.send_password_reset_email(to_email=user.email, reset_url=reset_url)

    return {"message": generic_msg}

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset Password using secure single-use token.
    Validations:
    - Token validity, expiration, and single-use state.
    - Minimum 6 characters and password matching.
    - Preserves user role and approval_status without modification.
    """
    raw_token = req.token.strip() if req.token else ""
    new_pwd = req.new_password
    confirm_pwd = req.confirm_password

    if not raw_token:
        raise HTTPException(status_code=400, detail="Reset token is required.")

    if new_pwd != confirm_pwd:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    if len(new_pwd) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset link.")

    if reset_record.used_at is not None:
        raise HTTPException(status_code=400, detail="This password reset link has already been used.")

    if reset_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This password reset link has expired.")

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User account associated with this token not found.")

    # Update password hash only. Do NOT touch approval_status or role!
    user.password_hash = get_password_hash(new_pwd)
    reset_record.used_at = datetime.utcnow()
    db.commit()

    return {"message": "Password reset successfully. Please log in with your new password."}

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/demo-switch/{role}", response_model=Token)
def demo_switch_account(role: str, db: Session = Depends(get_db)):
    """
    Hackathon Demo Switcher: Instantly logs in as sample Student, Recruiter, or College Admin.
    """
    role = role.lower()
    if role not in ["student", "recruiter", "college_admin", "platform_admin"]:
        raise HTTPException(status_code=400, detail="Invalid demo role. Choose student, recruiter, college_admin, or platform_admin.")

    user = db.query(User).filter(User.role == role).first()
    if not user:
        from app.seed.seed_data import seed_database_if_empty
        seed_database_if_empty(db)
        user = db.query(User).filter(User.role == role).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"No sample user found for role {role}. Please run seed script.")

    role_val = user.role or role
    full_name = user.full_name or f"Demo {role.capitalize()}"
    approval_status = getattr(user, "approval_status", "APPROVED") or "APPROVED"
    token = create_access_token(subject=user.id, role=role_val)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role_val,
        "approval_status": approval_status,
        "user_id": user.id,
        "full_name": full_name
    }
