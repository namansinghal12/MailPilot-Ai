from datetime import datetime
import uuid

from sqlalchemy import String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        default="dark",
        nullable=False,
    )

    email_alerts: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    high_priority_push: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    daily_digest: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    task_reminder_time: Mapped[str] = mapped_column(
        String(10),
        default="09:00",
        nullable=False,
    )

    preferred_model: Mapped[str] = mapped_column(
        String(50),
        default="gemini-3.5-pro",
        nullable=False,
    )

    creativity_level: Mapped[float] = mapped_column(
        Float,
        default=0.7,
        nullable=False,
    )

    auto_draft_replies: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    extract_tasks_automatically: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="UTC",
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        backref="settings",
    )
