from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, default="technical")  # frontend, backend, ml_ai, database, devops, core
    normalized_name = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    student_skills = relationship("StudentSkill", back_populates="skill")
    job_skills = relationship("JobSkill", back_populates="skill")

class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(String, default="intermediate")  # beginner, intermediate, advanced
    source = Column(String, default="resume")  # resume, certificate, self_reported
    is_verified = Column(Boolean, default=False)
    verified_by_certificate_id = Column(Integer, ForeignKey("certificates.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")
    certificate = relationship("Certificate", back_populates="verified_skills")
