from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)  # APPROVE_CERTIFICATE | REJECT_CERTIFICATE | APPROVE_RECRUITER | REJECT_RECRUITER | APPROVE_COLLEGE | REJECT_COLLEGE
    target_type = Column(String, nullable=False)  # certificate | recruiter | college
    target_id = Column(Integer, nullable=False)
    target_name = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
