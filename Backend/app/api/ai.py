from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.email import Email
from app.models.user import User
from app.services.gemini_service import ask_gemini


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Assistant"],
)


class ChatRequest(BaseModel):
    prompt: str


@router.post("/chat")
def chat_with_ai(
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Chat with real Google Gemini AI, providing authenticated user context and inbox threads.
    """
    if not data.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt text cannot be empty",
        )

    # Gather context from user's recent emails
    recent_emails = (
        db.query(Email)
        .filter(Email.user_id == user.id)
        .order_by(Email.received_at.desc())
        .limit(5)
        .all()
    )

    context_lines = []
    for em in recent_emails:
        context_lines.append(
            f"- From {em.sender_name} ({em.sender_email}): Subject: '{em.subject}', Category: {em.category}, Priority: {em.priority}, Read: {em.is_read}"
        )

    inbox_context = "\n".join(context_lines) if context_lines else "No emails currently in inbox."

    system_instruction = f"""
You are MailPilot AI, a powerful, intelligent email assistant.
You are assisting {user.name} (email: {user.email}).

The user's recent inbox threads:
{inbox_context}

Respond directly, concisely, and helpfully to the user's request. Format output in clean Markdown.
""".strip()

    try:
        response_text = ask_gemini(
            prompt=data.prompt,
            system_instruction=system_instruction,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini AI service error: {exc}",
        )

    return {
        "id": f"msg_{uuid.uuid4()}",
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
