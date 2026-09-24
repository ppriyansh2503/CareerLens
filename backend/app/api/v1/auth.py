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
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        college_name=user_in.college_name,
        company_name=user_in.company_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.role == "student":
        profile = StudentProfile(
            user_id=user.id,
            headline="Aspiring Software Engineer",
            department="Computer Science & Engineering",
            graduation_year=2026,
            cgpa=8.4,
            placement_readiness_score=40.0
        )
        db.add(profile)
        db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
    }

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
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
    if role not in ["student", "recruiter", "college_admin"]:
        raise HTTPException(status_code=400, detail="Invalid demo role. Choose student, recruiter, or college_admin.")

    user = db.query(User).filter(User.role == role).first()
    if not user:
        from app.seed.seed_data import seed_database_if_empty
        seed_database_if_empty(db)
        user = db.query(User).filter(User.role == role).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"No sample user found for role {role}. Please run seed script.")

    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
    }
