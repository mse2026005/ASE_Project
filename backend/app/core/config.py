from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "SHG Credit Manager"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shg_credit_manager"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/shg_credit_manager"

    # Security
    JWT_SECRET_KEY: str = "change_me_super_secret_key_for_development_jwt_auth_1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOGIN_MAX_FAILED_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Scheduler
    ENABLE_IN_PROCESS_SCHEDULER: bool = False


settings = Settings()

