from functools import lru_cache

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
    DEBUG: bool = False

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str

    # -----------------------------
    # Cross-origin requests
    # -----------------------------
    CORS_ORIGINS: str = "http://localhost:5173"

    # -----------------------------
    # Security
    # -----------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # -----------------------------
    # Google OAuth
    # -----------------------------
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # -----------------------------
    # Gemini
    # -----------------------------
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()