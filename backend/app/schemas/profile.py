from typing import List, Optional
from pydantic import BaseModel

class SkillBase(BaseModel):
    name: str
    category: str = "technical"

class StudentSkillOut(BaseModel):
    id: int
    skill_id: int
    name: str
    category: str
    proficiency: str
    source: str
    is_verified: bool
    verified_by_certificate_id: Optional[int] = None

    class Config:
        from_attributes = True

class StudentProfileUpdate(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    graduation_year: Optional[int] = None
    department: Optional[str] = None
    cgpa: Optional[float] = None

class CertificateSummary(BaseModel):
    id: int
    title: str
    issuing_org: str
    verification_status: str
    badge_tier: str
    verification_score: float

    class Config:
        from_attributes = True

class StudentProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    college_name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_file_url: Optional[str] = None
    graduation_year: int
    department: str
    cgpa: float
    placement_readiness_score: float
    skills: List[StudentSkillOut] = []
    certificates: List[CertificateSummary] = []

    class Config:
        from_attributes = True

class ReadinessMetric(BaseModel):
    label: str
    score: float
    max_score: float
    description: str

class ReadinessScoreOut(BaseModel):
    overall_score: float
    rating: str  # Ready to Place | Near Ready | Developing
    metrics: List[ReadinessMetric]
    key_strengths: List[str]
    critical_gaps: List[str]
    suggested_action: str
