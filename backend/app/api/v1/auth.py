from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.models.student import StudentProfile
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = user_in.role.strip().lower()
    if role not in ["student", "recruiter", "college_admin", "platform_admin"]:
        role = "student"

    # All newly registered users start in PENDING status until approved by platform admin
    approval_status = "PENDING"

    user = User(
        email=email,
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
    email = login_in.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
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
    full_name = user.full_name or email.split("@")[0].capitalize()
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
