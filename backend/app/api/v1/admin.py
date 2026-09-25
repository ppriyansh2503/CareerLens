from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.student import StudentProfile
from app.models.certificate import Certificate
from app.models.skill import Skill, StudentSkill
from app.models.audit_log import AuditLog
from app.schemas.admin import (
    PlatformStats,
    CertificateReviewItem,
    CertificateReviewAction,
    UserApprovalItem,
    UserApprovalAction,
    AuditLogOut
)
from app.services.skill_service import get_or_create_skill
from app.services.certificate_verifier import CertificateVerifier

router = APIRouter()

@router.get("/stats", response_model=PlatformStats)
def get_platform_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns authentic database counts for the Platform Admin dashboard.
    No mock or fake counters.
    """
    total_users = db.query(User).count()
    students_count = db.query(User).filter(User.role == "student").count()
    recruiters_count = db.query(User).filter(User.role == "recruiter").count()
    colleges_count = db.query(User).filter(User.role == "college_admin").count()
    admins_count = db.query(User).filter(User.role == "platform_admin").count()

    pending_certs = db.query(Certificate).filter(
        or_(
            Certificate.admin_review_status == "PENDING_REVIEW",
            Certificate.verification_status == "FLAGGED"
        )
    ).count()

    verified_certs = db.query(Certificate).filter(Certificate.verification_status == "VERIFIED").count()
    flagged_certs = db.query(Certificate).filter(Certificate.verification_status == "FLAGGED").count()

    pending_students = db.query(User).filter(
        User.role == "student",
        User.approval_status == "PENDING"
    ).count()

    pending_recruiters = db.query(User).filter(
        User.role == "recruiter",
        User.approval_status == "PENDING"
    ).count()

    pending_colleges = db.query(User).filter(
        User.role == "college_admin",
        User.approval_status == "PENDING"
    ).count()

    audit_logs_count = db.query(AuditLog).count()

    return {
        "total_users": total_users,
        "students_count": students_count,
        "recruiters_count": recruiters_count,
        "colleges_count": colleges_count,
        "admins_count": admins_count,
        "pending_certificates_count": pending_certs,
        "verified_certificates_count": verified_certs,
        "flagged_certificates_count": flagged_certs,
        "pending_students_count": pending_students,
        "pending_recruiters_count": pending_recruiters,
        "pending_colleges_count": pending_colleges,
        "audit_logs_count": audit_logs_count
    }

@router.get("/certificates/pending", response_model=List[CertificateReviewItem])
def list_certificates_for_review(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Lists certificates awaiting administrative review or flagged by the 4-tier verification engine.
    """
    certs = db.query(Certificate).filter(
        or_(
            Certificate.admin_review_status.in_(["PENDING_REVIEW", "APPROVED", "REJECTED"]),
            Certificate.verification_status == "FLAGGED"
        )
    ).order_by(desc(Certificate.id)).all()

    items = []
    for cert in certs:
        student_profile = cert.student
        student_user = student_profile.user if student_profile else None
        items.append(CertificateReviewItem(
            id=cert.id,
            student_id=cert.student_id,
            student_name=student_user.full_name if student_user else "Student",
            student_email=student_user.email if student_user else "",
            college_name=student_user.college_name if student_user else (student_profile.college_name if student_profile else None),
            title=cert.title,
            issuing_org=cert.issuing_org,
            file_path=cert.file_path,
            file_hash_sha256=cert.file_hash_sha256,
            qr_detected=cert.qr_detected,
            qr_decoded_url=cert.qr_decoded_url,
            ocr_extracted_text=cert.ocr_extracted_text,
            verification_score=cert.verification_score,
            verification_status=cert.verification_status,
            badge_tier=cert.badge_tier or "NONE",
            admin_review_status=cert.admin_review_status or "NONE",
            admin_review_reason=cert.admin_review_reason,
            admin_reviewed_at=cert.admin_reviewed_at,
            tamper_analysis_details=cert.tamper_analysis_details
        ))

    return items

@router.post("/certificates/{cert_id}/review")
def review_certificate(
    cert_id: int,
    action_in: CertificateReviewAction,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Platform Admin manual override for a certificate:
    - APPROVE: Overrides flag, sets status to VERIFIED, awards verified skills, and logs audit.
    - REJECT: Sets status to REJECTED with mandatory reason, removes awarded skills, and logs audit.
    """
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    action = action_in.action.upper().strip()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    now = datetime.utcnow()
    student = cert.student

    if action == "APPROVE":
        reason = (action_in.reason or "").strip() or "Approved by platform administrator upon inspection"
        cert.verification_status = "VERIFIED"
        cert.admin_review_status = "APPROVED"
        cert.admin_review_reason = reason
        cert.admin_reviewed_at = now
        cert.admin_reviewed_by_id = current_admin.id
        if not cert.badge_tier or cert.badge_tier == "NONE":
            cert.badge_tier = "GOLD"
        if cert.verification_score < 70.0:
            cert.verification_score = 90.0

        # Award verified skills from certificate
        awarded_skills = []
        if cert.tamper_analysis_details and "awarded_skills" in cert.tamper_analysis_details:
            awarded_skills = cert.tamper_analysis_details.get("awarded_skills") or []
        
        # If no skills in tamper details, infer from title
        if not awarded_skills:
            title_lower = (cert.title + " " + cert.issuing_org).lower()
            for key, skills in CertificateVerifier.SKILL_MAPPINGS.items():
                if key in title_lower:
                    for s in skills:
                        if s not in awarded_skills:
                            awarded_skills.append(s)

        if student:
            for skill_name in awarded_skills:
                CertificateVerifier._grant_verified_skill(db, student.id, skill_name)
            CertificateVerifier._recalculate_readiness_score(db, student)

        db.commit()

        # Audit log
        db.add(AuditLog(
            admin_id=current_admin.id,
            action="APPROVE_CERTIFICATE",
            target_type="certificate",
            target_id=cert.id,
            target_name=f"{cert.title} ({cert.issuing_org})",
            details=f"Admin override approval granted. Reason: {reason}"
        ))
        db.commit()

        return {
            "message": "Certificate approved successfully",
            "certificate_id": cert.id,
            "verification_status": cert.verification_status,
            "badge_tier": cert.badge_tier,
            "admin_review_status": cert.admin_review_status,
            "admin_review_reason": cert.admin_review_reason
        }

    else:
        # REJECT
        reason = (action_in.reason or "").strip()
        if not reason:
            raise HTTPException(status_code=400, detail="Mandatory review reason is required when rejecting a certificate")

        cert.verification_status = "REJECTED"
        cert.admin_review_status = "REJECTED"
        cert.admin_review_reason = reason
        cert.admin_reviewed_at = now
        cert.admin_reviewed_by_id = current_admin.id
        cert.badge_tier = "NONE"

        # Detach any verified skills tied specifically to this certificate
        if student:
            db.query(StudentSkill).filter(
                StudentSkill.student_id == student.id,
                StudentSkill.verified_by_certificate_id == cert.id
            ).delete()
            CertificateVerifier._recalculate_readiness_score(db, student)

        db.commit()

        # Audit log
        db.add(AuditLog(
            admin_id=current_admin.id,
            action="REJECT_CERTIFICATE",
            target_type="certificate",
            target_id=cert.id,
            target_name=f"{cert.title} ({cert.issuing_org})",
            details=f"Certificate rejected by admin. Reason: {reason}"
        ))
        db.commit()

        return {
            "message": "Certificate rejected successfully",
            "certificate_id": cert.id,
            "verification_status": cert.verification_status,
            "admin_review_status": cert.admin_review_status,
            "admin_review_reason": cert.admin_review_reason
        }

@router.get("/approvals/students", response_model=List[UserApprovalItem])
def list_students_for_approval(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Lists students and their approval statuses.
    """
    students = db.query(User).filter(User.role == "student").order_by(desc(User.created_at)).all()
    results = []
    for u in students:
        prof = u.student_profile
        results.append(UserApprovalItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            approval_status=u.approval_status or "PENDING",
            college_name=u.college_name,
            department=prof.department if prof else None,
            graduation_year=prof.graduation_year if prof else None,
            cgpa=prof.cgpa if prof else None,
            created_at=u.created_at
        ))
    return results

@router.post("/approvals/students/{user_id}")
def review_student(
    user_id: int,
    action_in: UserApprovalAction,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approves or rejects a student account.
    """
    student = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    action = action_in.action.upper().strip()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    reason = (action_in.reason or "").strip()
    if action == "REJECT" and not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    new_status = "APPROVED" if action == "APPROVE" else "REJECTED"
    student.approval_status = new_status
    db.commit()

    db.add(AuditLog(
        admin_id=current_admin.id,
        action=f"{action}_STUDENT",
        target_type="student",
        target_id=student.id,
        target_name=student.full_name,
        details=reason or f"Student account {action.lower()}ed by platform admin."
    ))
    db.commit()

    return {
        "message": f"Student {action.lower()}ed successfully",
        "user_id": student.id,
        "approval_status": student.approval_status
    }

@router.get("/approvals/recruiters", response_model=List[UserApprovalItem])
def list_recruiters_for_approval(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Lists recruiters and their approval statuses.
    """
    recruiters = db.query(User).filter(User.role == "recruiter").order_by(desc(User.created_at)).all()
    return [
        UserApprovalItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            approval_status=u.approval_status or "PENDING",
            company_name=u.company_name,
            created_at=u.created_at
        )
        for u in recruiters
    ]

@router.post("/approvals/recruiters/{user_id}")
def review_recruiter(
    user_id: int,
    action_in: UserApprovalAction,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approves or rejects a recruiter account.
    """
    recruiter = db.query(User).filter(User.id == user_id, User.role == "recruiter").first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    action = action_in.action.upper().strip()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    reason = (action_in.reason or "").strip()
    if action == "REJECT" and not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    new_status = "APPROVED" if action == "APPROVE" else "REJECTED"
    recruiter.approval_status = new_status
    db.commit()

    db.add(AuditLog(
        admin_id=current_admin.id,
        action=f"{action}_RECRUITER",
        target_type="recruiter",
        target_id=recruiter.id,
        target_name=recruiter.company_name or recruiter.full_name,
        details=reason or f"Recruiter {action.lower()}ed by platform admin."
    ))
    db.commit()

    return {
        "message": f"Recruiter {action.lower()}ed successfully",
        "user_id": recruiter.id,
        "approval_status": recruiter.approval_status
    }

@router.get("/approvals/colleges", response_model=List[UserApprovalItem])
def list_colleges_for_approval(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Lists college administrators and their approval statuses.
    """
    colleges = db.query(User).filter(User.role == "college_admin").order_by(desc(User.created_at)).all()
    return [
        UserApprovalItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            approval_status=u.approval_status or "PENDING",
            college_name=u.college_name,
            created_at=u.created_at
        )
        for u in colleges
    ]

@router.post("/approvals/colleges/{user_id}")
def review_college(
    user_id: int,
    action_in: UserApprovalAction,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approves or rejects a college administrator account.
    """
    college = db.query(User).filter(User.id == user_id, User.role == "college_admin").first()
    if not college:
        raise HTTPException(status_code=404, detail="College administrator not found")

    action = action_in.action.upper().strip()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    reason = (action_in.reason or "").strip()
    if action == "REJECT" and not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    new_status = "APPROVED" if action == "APPROVE" else "REJECTED"
    college.approval_status = new_status
    db.commit()

    db.add(AuditLog(
        admin_id=current_admin.id,
        action=f"{action}_COLLEGE",
        target_type="college",
        target_id=college.id,
        target_name=college.college_name or college.full_name,
        details=reason or f"College {action.lower()}ed by platform admin."
    ))
    db.commit()

    return {
        "message": f"College administrator {action.lower()}ed successfully",
        "user_id": college.id,
        "approval_status": college.approval_status
    }

@router.get("/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retrieves chronological audit trail of administrative actions.
    """
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(100).all()
    results = []
    for log in logs:
        admin_user = log.admin
        results.append(AuditLogOut(
            id=log.id,
            admin_name=admin_user.full_name if admin_user else "System Admin",
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            target_name=log.target_name,
            details=log.details,
            created_at=log.created_at
        ))
    return results
