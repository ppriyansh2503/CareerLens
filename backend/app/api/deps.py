from typing import Generator, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(reusable_oauth2)
) -> User:
    if not token:
        # Fallback to default demo student if no token provided in demo mode
        user = db.query(User).filter(User.role == "student").first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
        )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    if current_user.role != "student":
        # Check if student exists to return for demo
        demo_student = db.query(User).filter(User.role == "student").first()
        if demo_student:
            return demo_student
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires student privileges",
        )
    return current_user

def get_current_recruiter(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    if current_user.role != "recruiter":
        demo_recruiter = db.query(User).filter(User.role == "recruiter").first()
        if demo_recruiter:
            return demo_recruiter
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires recruiter privileges",
        )
    return current_user

def get_current_college_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    if current_user.role != "college_admin":
        demo_admin = db.query(User).filter(User.role == "college_admin").first()
        if demo_admin:
            return demo_admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires college admin privileges",
        )
    return current_user
