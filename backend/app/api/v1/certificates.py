import os
import io
import uuid
from typing import List
from PIL import Image
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.limiter import limiter
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateOut, VerificationAuditDetail
from app.services.certificate_verifier import CertificateVerifier
from app.services.storage import storage_backend

router = APIRouter()

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_certificate(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    issuing_org: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Supported formats: PDF, PNG, JPG, WEBP")

    # Read file with size limit (HTTP 413)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    file_bytes = bytearray()
    chunk_size = 64 * 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_bytes.extend(chunk)
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
            )

    raw_bytes = bytes(file_bytes)

    # Magic byte and content signature validation
    if ext == ".pdf":
        if not raw_bytes.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Uploaded file is not a valid PDF document."
            )
    else:
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            img.verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format or corrupted image file."
            )

    # Generate secure UUID filename using modular storage backend
    file_name = f"cert_{profile.id}_{uuid.uuid4().hex}{ext}"
    save_path = storage_backend.save("certificates", file_name, raw_bytes)

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
        return []
    return profile.certificates

@router.get("/{cert_id}/audit", response_model=VerificationAuditDetail)
def get_certificate_audit(
    cert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    is_owner = (cert.student and cert.student.user_id == current_user.id)
    is_recruiter = (current_user.role == "recruiter" and getattr(current_user, "approval_status", "APPROVED") == "APPROVED")
    is_college_admin = (
        current_user.role == "college_admin"
        and getattr(current_user, "approval_status", "APPROVED") == "APPROVED"
        and cert.student
        and cert.student.user
        and cert.student.user.college_name == current_user.college_name
    )
    is_admin = (current_user.role == "platform_admin")
    if not (is_owner or is_recruiter or is_college_admin or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this certificate audit."
        )

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
