from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.settings import UserSettings
from app.models.user import User


router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
)


class NotificationPreferencesSchema(BaseModel):
    emailAlerts: bool = True
    highPriorityPush: bool = True
    dailyDigest: bool = True
    taskReminderTime: str = "09:00"


class AIModelConfigSchema(BaseModel):
    preferredModel: str = "gemini-3.5-pro"
    creativityLevel: float = 0.7
    autoDraftReplies: bool = True
    extractTasksAutomatically: bool = True


class AccountInfoSchema(BaseModel):
    name: str
    email: str
    timezone: str = "UTC"


class SettingsUpdateSchema(BaseModel):
    theme: str | None = None
    notifications: NotificationPreferencesSchema | None = None
    aiConfig: AIModelConfigSchema | None = None
    account: AccountInfoSchema | None = None


def get_or_create_user_settings(user_id: str, db: Session) -> UserSettings:
    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == user_id)
        .first()
    )

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.get("/")
def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user settings from Supabase PostgreSQL.
    """
    user_settings = get_or_create_user_settings(user.id, db)

    return {
        "theme": user_settings.theme,
        "notifications": {
            "emailAlerts": user_settings.email_alerts,
            "highPriorityPush": user_settings.high_priority_push,
            "dailyDigest": user_settings.daily_digest,
            "taskReminderTime": user_settings.task_reminder_time,
        },
        "aiConfig": {
            "preferredModel": user_settings.preferred_model,
            "creativityLevel": user_settings.creativity_level,
            "autoDraftReplies": user_settings.auto_draft_replies,
            "extractTasksAutomatically": user_settings.extract_tasks_automatically,
        },
        "account": {
            "name": user.name,
            "email": user.email,
            "timezone": user_settings.timezone,
        },
    }


@router.patch("/")
def update_settings(
    data: SettingsUpdateSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user settings and profile name in Supabase PostgreSQL.
    """
    user_settings = get_or_create_user_settings(user.id, db)

    if data.account and data.account.name:
        user.name = data.account.name
        user_settings.timezone = data.account.timezone

    if data.theme:
        user_settings.theme = data.theme

    if data.notifications:
        user_settings.email_alerts = data.notifications.emailAlerts
        user_settings.high_priority_push = data.notifications.highPriorityPush
        user_settings.daily_digest = data.notifications.dailyDigest
        user_settings.task_reminder_time = data.notifications.taskReminderTime

    if data.aiConfig:
        user_settings.preferred_model = data.aiConfig.preferredModel
        user_settings.creativity_level = data.aiConfig.creativityLevel
        user_settings.auto_draft_replies = data.aiConfig.autoDraftReplies
        user_settings.extract_tasks_automatically = data.aiConfig.extractTasksAutomatically

    db.commit()
    db.refresh(user)
    db.refresh(user_settings)

    return {
        "theme": user_settings.theme,
        "notifications": {
            "emailAlerts": user_settings.email_alerts,
            "highPriorityPush": user_settings.high_priority_push,
            "dailyDigest": user_settings.daily_digest,
            "taskReminderTime": user_settings.task_reminder_time,
        },
        "aiConfig": {
            "preferredModel": user_settings.preferred_model,
            "creativityLevel": user_settings.creativity_level,
            "autoDraftReplies": user_settings.auto_draft_replies,
            "extractTasksAutomatically": user_settings.extract_tasks_automatically,
        },
        "account": {
            "name": user.name,
            "email": user.email,
            "timezone": user_settings.timezone,
        },
    }
