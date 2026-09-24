from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, default=0.0)
    match_breakdown = Column(JSON, nullable=True)
    status = Column(String, default="applied")  # applied | shortlisted | rejected | offered
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")
    student = relationship("StudentProfile", back_populates="applications")
