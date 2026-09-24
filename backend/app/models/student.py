from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    resume_file_url = Column(String, nullable=True)
    resume_raw_text = Column(Text, nullable=True)
    graduation_year = Column(Integer, default=2026)
    department = Column(String, default="Computer Science & Engineering")
    cgpa = Column(Float, default=8.5)
    placement_readiness_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
