from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PlatformStats(BaseModel):
    total_users: int
    students_count: int
    recruiters_count: int
    colleges_count: int
    admins_count: int
    pending_certificates_count: int
    verified_certificates_count: int
    flagged_certificates_count: int
    pending_students_count: int = 0
    pending_recruiters_count: int
    pending_colleges_count: int
    audit_logs_count: int

class CertificateReviewItem(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_email: str
    college_name: Optional[str] = None
    title: str
    issuing_org: str
    file_path: str
    file_hash_sha256: str
    qr_detected: bool
    qr_decoded_url: Optional[str] = None
    ocr_extracted_text: Optional[str] = None
    verification_score: float
    verification_status: str
    badge_tier: str
    admin_review_status: str
    admin_review_reason: Optional[str] = None
    admin_reviewed_at: Optional[datetime] = None
    tamper_analysis_details: Optional[Dict[str, Any]] = None

class CertificateReviewAction(BaseModel):
    action: str  # APPROVE | REJECT
    reason: Optional[str] = None

class UserApprovalItem(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    approval_status: str
    college_name: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    created_at: datetime

class UserApprovalAction(BaseModel):
    action: str  # APPROVE | REJECT
    reason: Optional[str] = None

class AuditLogOut(BaseModel):
    id: int
    admin_name: Optional[str] = None
    action: str
    target_type: str
    target_id: int
    target_name: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
