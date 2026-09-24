from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel

class CertificateOut(BaseModel):
    id: int
    student_id: int
    title: str
    issuing_org: str
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    file_path: str
    file_hash_sha256: str
    qr_detected: bool
    qr_decoded_url: Optional[str] = None
    verification_score: float
    verification_status: str
    badge_tier: str
    verified_at: datetime

    class Config:
        from_attributes = True

class TamperAnalysis(BaseModel):
    is_tampered: bool
    ela_anomaly_detected: bool
    ela_score: float
    metadata_inconsistency_detected: bool
    suspicious_software: Optional[str] = None
    creation_vs_mod_anomaly: bool
    explanation: str

class VerificationAuditDetail(BaseModel):
    certificate: CertificateOut
    hash_verification: Dict[str, Any]
    qr_verification: Dict[str, Any]
    ocr_verification: Dict[str, Any]
    tamper_analysis: Dict[str, Any]
    verified_skills_awarded: List[str]
    verdict: str
    audit_timestamp: datetime
