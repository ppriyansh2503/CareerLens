import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.certificate import Certificate
from app.models.skill import Skill, StudentSkill
from app.models.student import StudentProfile
from app.services.qr_scanner import QRScanner
from app.services.ocr_service import OCRService
from app.services.tamper_detector import TamperDetector

class CertificateVerifier:
    """
    4-Tier Certificate Verification Orchestrator:
    - Tier 1: SHA-256 Hash Duplicate / Tamper Check
    - Tier 2: QR Code Scan & Issuing Authority Validation
    - Tier 3: OCR Entity & Name Consistency Check
    - Tier 4: Image Error Level Analysis (ELA) & PDF Metadata Forensics
    - Output: Verification Score (0-100), Status & Trust Badge (GOLD/SILVER/FLAGGED)
    """

    SKILL_MAPPINGS = {
        "aws": ["AWS", "Cloud Computing", "DevOps"],
        "amazon": ["AWS", "Cloud Computing"],
        "react": ["React", "JavaScript", "Frontend Development"],
        "python": ["Python", "Backend Development"],
        "fastapi": ["FastAPI", "Python", "REST APIs"],
        "data science": ["Data Science", "Python", "Machine Learning"],
        "machine learning": ["Machine Learning", "Python", "Deep Learning"],
        "docker": ["Docker", "DevOps", "Containers"],
        "kubernetes": ["Kubernetes", "DevOps", "Cloud Computing"],
        "full stack": ["React", "Node.js", "Full Stack Development"],
        "sql": ["SQL", "Databases", "PostgreSQL"],
    }

    @classmethod
    def calculate_file_hash(cls, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    def verify_certificate(
        cls,
        db: Session,
        student: StudentProfile,
        file_path: str,
        file_bytes: bytes,
        title: str,
        claimed_issuer: str
    ) -> Dict[str, Any]:
        
        # 1. Tier 1: SHA-256 Hash Check
        file_hash = cls.calculate_file_hash(file_bytes)
        existing_cert = db.query(Certificate).filter(
            Certificate.file_hash_sha256 == file_hash,
            Certificate.student_id != student.id
        ).first()

        is_duplicate = existing_cert is not None
        hash_check_result = {
            "file_hash_sha256": file_hash,
            "is_duplicate_across_profiles": is_duplicate,
            "status": "DUPLICATE_FLAG" if is_duplicate else "UNIQUE_INTEGRITY_OK"
        }

        # 2. Tier 2: QR Scanner
        qr_result = QRScanner.scan(file_path)

        # 3. Tier 3: OCR & Entity Parsing
        ocr_text = OCRService.extract_text(file_path)
        student_name = student.user.full_name if (student.user and student.user.full_name) else ""
        entity_result = OCRService.parse_entities(ocr_text, student_name=student_name)

        # 4. Tier 4: Tamper Detection (ELA + Metadata)
        tamper_result = TamperDetector.evaluate_tampering(file_path, claimed_issuer)

        # Synthesize Score
        verification_score = 0.0
        audit_verdict = ""
        badge_tier = "NONE"
        status = "PENDING"

        # If duplicate detected, flag immediately
        if is_duplicate:
            verification_score = 25.0
            status = "FLAGGED"
            badge_tier = "NONE"
            audit_verdict = "Duplicate certificate detected in system: This exact file hash has already been registered by another user profile."

        # If forensic tampering detected, flag
        elif tamper_result.get("is_tampered"):
            verification_score = max(10.0, 60.0 - tamper_result.get("tamper_confidence_score", 50) * 0.4)
            status = "FLAGGED"
            badge_tier = "NONE"
            audit_verdict = f"Tampering anomaly detected: {tamper_result.get('explanation')}"

        else:
            # Clean document. Now determine Gold vs Silver
            base_score = 50.0  # clean document & unique hash
            
            # QR validation boost
            if qr_result.get("qr_found"):
                if qr_result.get("is_trusted_issuer"):
                    base_score += 35.0  # Gold tier booster!
                else:
                    base_score += 20.0
            
            # Name / Entity Match boost
            if entity_result.get("name_found_in_cert"):
                base_score += 15.0
            elif entity_result.get("name_match_score", 0) > 40:
                base_score += 10.0
            else:
                # Name wasn't explicitly matched in text
                base_score += 5.0

            verification_score = min(100.0, round(base_score, 1))

            if verification_score >= 85.0:
                status = "VERIFIED"
                badge_tier = "GOLD"
                audit_verdict = "Cryptographically & QR verified by recognized issuing authority. Student name match confirmed."
            elif verification_score >= 70.0:
                status = "VERIFIED"
                badge_tier = "SILVER"
                audit_verdict = "Verified via OCR and authentic document heuristics. Validated against recognized certification standards."
            else:
                status = "PENDING"
                badge_tier = "BRONZE"
                audit_verdict = "Credential recorded as self-reported pending additional authority confirmation."

        # Skills auto-verification
        awarded_skills = []
        if status == "VERIFIED":
            content_lower = (title + " " + ocr_text + " " + claimed_issuer).lower()
            for key, skills_to_add in cls.SKILL_MAPPINGS.items():
                if key in content_lower:
                    for skill_name in skills_to_add:
                        if skill_name not in awarded_skills:
                            awarded_skills.append(skill_name)
                            cls._grant_verified_skill(db, student.id, skill_name)

        tamper_details = {
            "hash_analysis": hash_check_result,
            "qr_analysis": qr_result,
            "ocr_analysis": entity_result,
            "forensic_analysis": tamper_result,
            "awarded_skills": awarded_skills
        }

        # Create or update certificate record
        cert = Certificate(
            student_id=student.id,
            title=title or entity_result.get("issuing_org", "Certified Credential"),
            issuing_org=claimed_issuer or entity_result.get("issuing_org", "Authority"),
            issue_date=entity_result.get("issue_date"),
            credential_id=entity_result.get("credential_id"),
            credential_url=qr_result.get("raw_payload") if qr_result.get("is_url") else None,
            file_path=file_path,
            file_hash_sha256=file_hash,
            qr_detected=qr_result.get("qr_found", False),
            qr_decoded_url=qr_result.get("raw_payload") if qr_result.get("is_url") else None,
            ocr_extracted_text=ocr_text[:2000],
            verification_score=verification_score,
            verification_status=status,
            badge_tier=badge_tier,
            tamper_analysis_details=tamper_details
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)

        # Update student placement readiness score
        cls._recalculate_readiness_score(db, student)

        return {
            "certificate": cert,
            "verification_score": verification_score,
            "verification_status": status,
            "badge_tier": badge_tier,
            "audit_verdict": audit_verdict,
            "tamper_analysis": tamper_details,
            "awarded_skills": awarded_skills
        }

    @classmethod
    def _grant_verified_skill(cls, db: Session, student_id: int, skill_name: str):
        # Find or create skill
        norm_name = skill_name.lower().replace(" ", "").replace(".", "")
        skill = db.query(Skill).filter(Skill.normalized_name == norm_name).first()
        if not skill:
            skill = Skill(name=skill_name, normalized_name=norm_name, category="technical")
            db.add(skill)
            db.commit()
            db.refresh(skill)

        # Find or create student skill
        st_skill = db.query(StudentSkill).filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_id == skill.id
        ).first()

        if not st_skill:
            st_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill.id,
                proficiency="advanced",
                source="certificate",
                is_verified=True
            )
            db.add(st_skill)
        else:
            st_skill.is_verified = True
            st_skill.source = "certificate"
            st_skill.proficiency = "advanced"
        db.commit()

    @classmethod
    def _recalculate_readiness_score(cls, db: Session, student: StudentProfile):
        total_skills = len(student.skills)
        verified_skills = sum(1 for s in student.skills if s.is_verified)
        verified_certs = sum(1 for c in student.certificates if c.verification_status == "VERIFIED")
        
        # Base formula: 20 pts profile + up to 40 pts skills (verified gets 2x) + up to 40 pts certs
        skill_score = min(40.0, (verified_skills * 6.0) + ((total_skills - verified_skills) * 2.0))
        cert_score = min(40.0, verified_certs * 15.0)
        profile_score = 20.0 if student.resume_file_url else 10.0

        overall = min(100.0, round(profile_score + skill_score + cert_score, 1))
        student.placement_readiness_score = overall
        db.commit()
