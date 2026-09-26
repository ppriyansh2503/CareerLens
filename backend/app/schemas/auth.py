from typing import Optional
from pydantic import BaseModel, field_validator

class UserRegister(BaseModel):
    email: str
    phone_number: Optional[str] = None
    password: str
    full_name: str
    role: str = "student"  # student | recruiter | college_admin | platform_admin
    college_name: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None

    @field_validator("email", mode="before")
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("phone_number", mode="before")
    def normalize_phone(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("full_name", mode="before")
    def normalize_full_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("role", mode="before")
    def normalize_role(cls, v):
        if isinstance(v, str):
            r = v.strip().lower()
            if r in ["student", "recruiter", "college_admin", "platform_admin"]:
                return r
        return v

class UserLogin(BaseModel):
    email: str  # Accepts Email or Phone Number
    password: str

    @field_validator("email", mode="before")
    def normalize_identifier(cls, v):
        if isinstance(v, str):
            val = v.strip()
            if "@" in val:
                return val.lower()
            return val
        return v

class ForgotPasswordRequest(BaseModel):
    identifier: str

    @field_validator("identifier", mode="before")
    def clean_identifier(cls, v):
        if isinstance(v, str):
            val = v.strip()
            if "@" in val:
                return val.lower()
            return val
        return v

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class MessageResponse(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    approval_status: Optional[str] = "APPROVED"
    user_id: int
    full_name: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    phone_number: Optional[str] = None
    full_name: str
    role: str
    approval_status: Optional[str] = "APPROVED"
    college_name: Optional[str] = None
    company_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True
