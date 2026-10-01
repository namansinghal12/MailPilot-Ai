from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    """

    # -----------------------------
    # Application
    # -----------------------------
    APP_NAME: str = "MailPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # -----------------------------
    # Database
    # -----------------------------
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DATABASE_URL: str

    # -----------------------------
    # Security
    # -----------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # -----------------------------
    # Google OAuth
    # -----------------------------
        # -----------------------------
    # Google OAuth
    # -----------------------------
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str 
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:5173"
    # -----------------------------
    # Gemini
    # -----------------------------
    GEMINI_API_KEY: str = ""

    @field_validator(
        "DB_HOST",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DATABASE_URL",
        "SECRET_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI",
        "FRONTEND_URL",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

@lru_cache
def get_settings():
    return Settings()


settings = get_settings()