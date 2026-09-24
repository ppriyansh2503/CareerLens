from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, default="Career Guidance Session")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    detected_language = Column(String, default="en")  # en | hi | hinglish
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
