from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://lms_user:lms_password@localhost:5432/lms_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90

    # App
    APP_NAME: str = "LMS Backend"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
