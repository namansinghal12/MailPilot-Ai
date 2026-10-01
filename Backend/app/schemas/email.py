from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EmailCreate(BaseModel):
    user_id: str
    sender_name: str
    sender_email: str
    recipient: str

    subject: str
    body: str

    snippet: Optional[str] = None

    category: str = "Inbox"
    priority: str = "medium"

    is_read: bool = False
    is_starred: bool = False
    is_archived: bool = False
    has_tasks: bool = False


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    sender_name: str
    sender_email: str
    recipient: str

    subject: str
    body: str
    snippet: Optional[str]

    category: str
    priority: str

    is_read: bool
    is_starred: bool
    is_archived: bool
    has_tasks: bool

    received_at: datetime
    created_at: datetime