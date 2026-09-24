import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateOut, VerificationAuditDetail
from app.services.certificate_verifier import CertificateVerifier

router = APIRouter()

@router.post("/upload")
async def upload_certificate(
    file: UploadFile = File(...),
    title: str = Form(...),
    issuing_org: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Supported formats: PDF, PNG, JPG, WEBP")

    file_bytes = await file.read()
    file_name = f"cert_{profile.id}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, "certificates", file_name)

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Run Multi-Tier Verification
    result = CertificateVerifier.verify_certificate(
        db=db,
        student=profile,
        file_path=save_path,
        file_bytes=file_bytes,
        title=title,
        claimed_issuer=issuing_org
    )

    cert = result["certificate"]

    return {
        "certificate_id": cert.id,
        "title": cert.title,
        "issuing_org": cert.issuing_org,
        "verification_score": cert.verification_score,
        "verification_status": cert.verification_status,
        "badge_tier": cert.badge_tier,
        "qr_detected": cert.qr_detected,
        "qr_decoded_url": cert.qr_decoded_url,
        "audit_verdict": result["audit_verdict"],
        "awarded_skills": result["awarded_skills"],
        "tamper_analysis": result["tamper_analysis"]
    }

@router.get("/", response_model=List[CertificateOut])
def list_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = db.query(StudentProfile).first()
        if not profile:
            return []
    return profile.certificates

@router.get("/{cert_id}/audit", response_model=VerificationAuditDetail)
def get_certificate_audit(
    cert_id: int,
    db: Session = Depends(get_db)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    details = cert.tamper_analysis_details or {}

    verdict_text = "Verified and authenticated credential."
    if cert.verification_status == "FLAGGED":
        verdict_text = "FLAGGED: Digital anomalies detected in Error Level Analysis or metadata consistency checks."
    elif cert.badge_tier == "GOLD":
        verdict_text = "GOLD BADGE: Cryptographically & QR validated against recognized issuing authority."

    return {
        "certificate": cert,
        "hash_verification": details.get("hash_analysis", {}),
        "qr_verification": details.get("qr_analysis", {}),
        "ocr_verification": details.get("ocr_analysis", {}),
        "tamper_analysis": details.get("forensic_analysis", {}),
        "verified_skills_awarded": details.get("awarded_skills", []),
        "verdict": verdict_text,
        "audit_timestamp": cert.verified_at
    }
