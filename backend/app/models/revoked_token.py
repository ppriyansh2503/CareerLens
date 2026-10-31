from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
