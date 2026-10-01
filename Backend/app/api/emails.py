import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.email import Email
from app.models.user import User
from app.schemas.email import EmailCreate, EmailResponse
from app.services.gmail_service import fetch_recent_emails
from app.services.gemini_service import (
    generate_draft_reply,
    analyze_email_with_ai,
)


router = APIRouter(
    prefix="/api/emails",
    tags=["Emails"],
)


@router.get(
    "/",
    response_model=list[EmailResponse],
)
def get_emails(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get emails belonging to the currently authenticated user.
    """
    return (
        db.query(Email)
        .filter(Email.user_id == user.id)
        .order_by(Email.received_at.desc())
        .all()
    )


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
)
def get_email(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get one email belonging to the authenticated user.
    """
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email


@router.post(
    "/",
    response_model=EmailResponse,
)
def create_email(
    data: EmailCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create an email record scoped to the authenticated user.
    """
    email = Email(
        id=str(uuid.uuid4()),
        user_id=user.id,
        sender_name=data.sender_name,
        sender_email=data.sender_email,
        recipient=data.recipient,
        subject=data.subject,
        body=data.body,
        snippet=data.snippet,
        category=data.category,
        priority=data.priority,
        is_read=data.is_read,
        is_starred=data.is_starred,
        is_archived=data.is_archived,
        has_tasks=data.has_tasks,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return email


@router.post("/sync")
def sync_gmail(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch recent REAL Gmail messages and save/sync them
    into the authenticated user's MailPilot inbox.
    """
    if not user.google_refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Google Gmail authorization is not available for this user",
        )

    try:
        gmail_emails = fetch_recent_emails(
            refresh_token=user.google_refresh_token,
            max_results=80,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch Gmail messages: {exc}",
        )

    print("\n========== GMAIL SYNC ==========")
    print(f"Fetched from Gmail: {len(gmail_emails)}")

    for gmail_email in gmail_emails[:10]:
        print(
           f"{gmail_email['received_at']} | "
           f"{gmail_email['sender_name']} | "
           f"{gmail_email['subject']}"
    )

    print("================================\n")

    inserted = 0
    updated = 0

    for gmail_email in gmail_emails:
        existing = (
            db.query(Email)
            .filter(
                Email.id == gmail_email["id"],
                Email.user_id == user.id,
            )
            .first()
        )

        if existing:
            existing.sender_name = gmail_email["sender_name"]
            existing.sender_email = gmail_email["sender_email"]
            existing.recipient = gmail_email["recipient"]
            existing.subject = gmail_email["subject"]
            existing.body = gmail_email["body"]
            existing.snippet = gmail_email["snippet"]
            existing.is_read = gmail_email["is_read"]
            existing.is_starred = gmail_email["is_starred"]
            existing.is_archived = gmail_email["is_archived"]
            existing.received_at = gmail_email["received_at"]
            updated += 1
        else:
            email = Email(
                id=gmail_email["id"],
                user_id=user.id,
                sender_name=gmail_email["sender_name"],
                sender_email=gmail_email["sender_email"],
                recipient=gmail_email["recipient"],
                subject=gmail_email["subject"],
                body=gmail_email["body"],
                snippet=gmail_email["snippet"],
                category="Inbox",
                priority="medium",
                is_read=gmail_email["is_read"],
                is_starred=gmail_email["is_starred"],
                is_archived=gmail_email["is_archived"],
                has_tasks=False,
                received_at=gmail_email["received_at"],
            )
            db.add(email)
            inserted += 1

    db.commit()

    return {
        "message": "Gmail sync completed successfully",
        "fetched": len(gmail_emails),
        "inserted": inserted,
        "updated": updated,
    }

@router.post("/{email_id}/analyze")
def analyze_email(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze a real email using Gemini AI.
    """

    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    try:
        analysis = analyze_email_with_ai(
            subject=email.subject,
            body=email.body,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini AI analysis failed: {exc}",
        )

    return {
        "email_id": email_id,
        "subject": email.subject,
        "analysis": analysis,
    }


@router.post("/{email_id}/draft-reply")
def create_draft_reply(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an AI draft reply using Gemini AI for an email thread.
    """
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    try:
        reply_text = generate_draft_reply(
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            subject=email.subject,
            body=email.body,
            user_name=user.name,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini AI error: {exc}",
        )

    return {
        "email_id": email_id,
        "draft_reply": reply_text,
    }


@router.patch("/{email_id}/read")
def mark_email_read(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    email.is_read = True
    db.commit()

    return {
        "message": "Email marked as read",
        "id": email_id,
    }


@router.patch("/{email_id}/star")
def toggle_star(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    email.is_starred = not email.is_starred
    db.commit()

    return {
        "message": "Star status updated",
        "is_starred": email.is_starred,
    }


@router.delete("/{email_id}")
def delete_email(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    db.delete(email)
    db.commit()

    return {
        "message": "Email deleted",
    }


@router.patch("/{email_id}/archive")
def archive_email(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user.id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    email.is_archived = True
    db.commit()

    return {
        "message": "Email archived",
        "id": email_id,
    }