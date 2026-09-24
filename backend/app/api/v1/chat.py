from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatMessageOut, ChatSessionOut
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/message", response_model=ChatMessageOut)
def send_chat_message(
    msg_in: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        student = db.query(StudentProfile).first()

    # Get or create active session
    session = None
    if msg_in.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == msg_in.session_id,
            ChatSession.user_id == current_user.id
        ).first()

    if not session:
        session = ChatSession(
            user_id=current_user.id,
            title="Career & Placement Guidance"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_lang = AIService.detect_language(msg_in.content)
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        content=msg_in.content,
        detected_language=user_lang
    )
    db.add(user_msg)
    db.commit()

    # Generate AI response
    ai_result = AIService.generate_chat_response(
        user_message=msg_in.content,
        student=student
    )

    # Save assistant message
    ai_msg = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_result["content"],
        detected_language=ai_result["detected_language"]
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg

@router.get("/history", response_model=List[ChatMessageOut])
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.id.desc()).first()
    if not session:
        return []
    return session.messages
