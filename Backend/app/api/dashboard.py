from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.email import Email
from app.models.task import Task
from app.models.user import User


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/")
def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get real dashboard summary metrics and smart advice calculated
    from the authenticated user's real Supabase data.
    """
    # Email stats
    total_emails = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == user.id)
        .scalar()
        or 0
    )

    unread_emails = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == user.id, Email.is_read == False)
        .scalar()
        or 0
    )

    high_priority = (
        db.query(func.count(Email.id))
        .filter(
            Email.user_id == user.id,
            Email.priority.in_(["high", "urgent"]),
        )
        .scalar()
        or 0
    )

    starred_emails = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == user.id, Email.is_starred == True)
        .scalar()
        or 0
    )

    # Task stats
    pending_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.user_id == user.id, Task.status != "completed")
        .scalar()
        or 0
    )

    metrics = [
        {
            "id": "m1",
            "label": "Total Emails",
            "value": total_emails,
            "change": f"{unread_emails} unread",
            "trend": "up",
            "color": "primary",
            "icon": "mail",
        },
        {
            "id": "m2",
            "label": "High Priority",
            "value": high_priority,
            "change": "Requires attention",
            "trend": "up" if high_priority > 0 else "neutral",
            "color": "error",
            "icon": "alert-triangle",
        },
        {
            "id": "m3",
            "label": "Active Tasks",
            "value": pending_tasks,
            "change": "Extracted items",
            "trend": "neutral",
            "color": "tertiary",
            "icon": "clock",
        },
        {
            "id": "m4",
            "label": "Starred Items",
            "value": starred_emails,
            "change": "Saved threads",
            "trend": "up",
            "color": "secondary",
            "icon": "check-square",
        },
    ]

    # Dynamic Smart Advice based on real top email or task
    top_email = (
        db.query(Email)
        .filter(Email.user_id == user.id)
        .order_by(
            (Email.priority == "urgent").desc(),
            (Email.priority == "high").desc(),
            Email.is_read.asc(),
            Email.received_at.desc(),
        )
        .first()
    )

    if top_email:
        smart_advice = {
            "id": f"adv_{top_email.id}",
            "title": f"Action suggested for: {top_email.subject}",
            "description": top_email.snippet or top_email.body[:150],
            "sourceSender": top_email.sender_name,
            "deadline": "Action requested",
            "actionText": "Draft Reply with AI",
            "emailId": top_email.id,
        }
    else:
        smart_advice = {
            "id": "adv_welcome",
            "title": "Welcome to your MailPilot Workspace",
            "description": "Your inbox is connected to Supabase. Click 'Sync Gmail' in your inbox to fetch real emails and auto-generate AI insights.",
            "sourceSender": "MailPilot Assistant",
            "deadline": "",
            "actionText": "Sync Gmail",
            "emailId": "",
        }

    return {
        "metrics": metrics,
        "smartAdvice": smart_advice,
    }
