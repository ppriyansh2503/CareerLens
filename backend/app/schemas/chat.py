from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[int] = None
    language: Optional[str] = "auto"  # auto | en | hi | hinglish

class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    sender: str
    content: str
    detected_language: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[ChatMessageOut] = []

    class Config:
        from_attributes = True
