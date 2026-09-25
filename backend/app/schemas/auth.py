from typing import Optional
from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "student"  # student | recruiter | college_admin
    college_name: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    college_name: Optional[str] = None
    company_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True
