import os
import mimetypes
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate

router = APIRouter()

def _check_resume_access(current_user: User, student: StudentProfile) -> bool:
    if current_user.role == "platform_admin":
        return True
    if current_user.role == "recruiter" and getattr(current_user, "approval_status", "APPROVED") == "APPROVED":
        return True
    if (
        current_user.role == "college_admin"
        and getattr(current_user, "approval_status", "APPROVED") == "APPROVED"
        and student.user
        and student.user.college_name == current_user.college_name
    ):
        return True
    if current_user.role == "student" and student.user_id == current_user.id:
        return True
    return False

def _check_certificate_access(current_user: User, cert: Certificate) -> bool:
    if current_user.role == "platform_admin":
        return True
    if current_user.role == "recruiter" and getattr(current_user, "approval_status", "APPROVED") == "APPROVED":
        return True
    if (
        current_user.role == "college_admin"
        and getattr(current_user, "approval_status", "APPROVED") == "APPROVED"
        and cert.student
        and cert.student.user
        and cert.student.user.college_name == current_user.college_name
    ):
        return True
    if current_user.role == "student" and cert.student and cert.student.user_id == current_user.id:
        return True
    return False

@router.get("/files/{category}/{filename}")
@router.get("/uploads/{category}/{filename}")
def get_uploaded_file(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authenticated and authorized access to uploaded resumes and certificates.
    Protects against directory traversal and unauthorized document viewing.
    """
    if category not in ["resumes", "certificates"]:
        raise HTTPException(status_code=404, detail="Invalid file category")

    # Strict path traversal check
    clean_filename = os.path.basename(filename)
    if not clean_filename or clean_filename != filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid file path")

    category_dir = os.path.abspath(os.path.join(settings.UPLOAD_DIR, category))
    file_path = os.path.abspath(os.path.join(category_dir, clean_filename))

    # Ensure resolved path is strictly within category_dir
    if not file_path.startswith(category_dir):
        raise HTTPException(status_code=400, detail="Path traversal detected")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested file not found")

    # Authorize based on category and ownership
    if category == "resumes":
        # Find student profile referencing this file
        student = db.query(StudentProfile).filter(
            (StudentProfile.resume_file_url.like(f"%{clean_filename}"))
        ).first()

        if not student and current_user.role != "platform_admin":
            raise HTTPException(status_code=404, detail="Resume record not found")

        if student and not _check_resume_access(current_user, student):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view or download this resume."
            )

    elif category == "certificates":
        cert = db.query(Certificate).filter(
            Certificate.file_path.like(f"%{clean_filename}")
        ).first()

        if not cert and current_user.role != "platform_admin":
            raise HTTPException(status_code=404, detail="Certificate record not found")

        if cert and not _check_certificate_access(current_user, cert):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view or download this certificate."
            )

    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=media_type or "application/octet-stream", filename=clean_filename)

@router.get("/student/resume/download/{student_id}")
def download_student_resume(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student or not student.resume_file_url:
        raise HTTPException(status_code=404, detail="Student resume not found")

    if not _check_resume_access(current_user, student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download this resume."
        )

    clean_filename = os.path.basename(student.resume_file_url)
    file_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, "resumes", clean_filename))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server")

    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=media_type or "application/pdf", filename=clean_filename)

@router.get("/certificates/{cert_id}/download")
def download_certificate_file(
    cert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert or not cert.file_path:
        raise HTTPException(status_code=404, detail="Certificate not found")

    if not _check_certificate_access(current_user, cert):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download this certificate."
        )

    clean_filename = os.path.basename(cert.file_path)
    file_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, "certificates", clean_filename))
    if not os.path.exists(file_path):
        # Fallback to direct file_path if stored as full path
        if os.path.exists(cert.file_path):
            file_path = cert.file_path
        else:
            raise HTTPException(status_code=404, detail="Certificate file not found on server")

    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=media_type or "application/octet-stream", filename=clean_filename)
