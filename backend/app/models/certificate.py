from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    issuing_org = Column(String, nullable=False)
    issue_date = Column(String, nullable=True)
    credential_id = Column(String, nullable=True)
    credential_url = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_hash_sha256 = Column(String, index=True, nullable=False)
    
    # Multi-tier verification outcomes
    qr_detected = Column(Boolean, default=False)
    qr_decoded_url = Column(String, nullable=True)
    ocr_extracted_text = Column(Text, nullable=True)
    
    verification_score = Column(Float, default=0.0)  # 0 to 100
    verification_status = Column(String, default="PENDING")  # VERIFIED | FLAGGED | REJECTED | PENDING
    badge_tier = Column(String, default="NONE")  # GOLD | SILVER | BRONZE | NONE
    
    # Tamper & Forensic audit details (stored as JSON)
    tamper_analysis_details = Column(JSON, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("StudentProfile", back_populates="certificates")
    verified_skills = relationship("StudentSkill", back_populates="certificate")
