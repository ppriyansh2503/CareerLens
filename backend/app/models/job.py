from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, index=True, nullable=False)
    company_name = Column(String, index=True, nullable=False)
    location = Column(String, default="Remote")
    job_type = Column(String, default="internship")  # internship | full_time
    stipend_or_salary = Column(String, default="₹25,000 / month")
    description = Column(Text, nullable=False)
    requirements_summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)

    # Relationships
    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="job_skills")
