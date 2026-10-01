from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    user_id: str
    email_id: Optional[str] = None

    title: str
    description: Optional[str] = None

    priority: str = "medium"
    status: str = "todo"

    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    email_id: Optional[str]

    title: str
    description: Optional[str]

    priority: str
    status: str

    deadline: Optional[datetime]

    completed: bool
    created_at: datetime