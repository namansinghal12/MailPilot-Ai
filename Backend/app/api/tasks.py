import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all tasks belonging to the authenticated user.
    """
    return (
        db.query(Task)
        .filter(Task.user_id == user.id)
        .order_by(Task.created_at.desc())
        .all()
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific task for the authenticated user.
    """
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.post(
    "/",
    response_model=TaskResponse,
)
def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task scoped to the authenticated user.
    """
    task_data = data.model_dump()
    task_data["user_id"] = user.id

    task = Task(
        id=str(uuid.uuid4()),
        **task_data,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: str,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a task belonging to the authenticated user.
    """
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a task belonging to the authenticated user.
    """
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted",
    }