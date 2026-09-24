from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class JobSkillOut(BaseModel):
    id: int
    name: str
    category: str
    is_mandatory: bool
    weight: float

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company_name: str
    location: str = "Remote"
    job_type: str = "internship"
    stipend_or_salary: str = "₹25,000 / month"
    description: str
    requirements_summary: Optional[str] = None
    skills: List[str] = []

class JobOut(BaseModel):
    id: int
    recruiter_id: int
    title: str
    company_name: str
    location: str
    job_type: str
    stipend_or_salary: str
    description: str
    requirements_summary: Optional[str] = None
    is_active: bool
    created_at: datetime
    skills: List[JobSkillOut] = []
    
    # Calculated dynamically for the active student
    match_score: Optional[float] = None
    match_tier: Optional[str] = None

    class Config:
        from_attributes = True
