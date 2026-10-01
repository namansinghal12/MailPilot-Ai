from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base
from app.database.database import engine

import app.models

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.emails import router as emails_router
from app.api.tasks import router as tasks_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.settings import router as settings_router
from app.api.ai import router as ai_router

from app.core.config import settings


# Create database tables in Supabase
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Powered Email Summarizer Backend",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(emails_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(settings_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to MailPilot AI Backend 🚀",
        "status": "running",
    }