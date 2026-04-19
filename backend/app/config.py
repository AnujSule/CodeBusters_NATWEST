import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "DataDialogue"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = "datadialogue-secret-key-change-in-production-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost"

    # Database — SQLite for local dev (no Docker needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./datadialogue.db"

    # Redis (optional — not used in local mode)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage — local filesystem instead of MinIO
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "datadialogue_minio"
    MINIO_SECRET_KEY: str = "changeme123"
    MINIO_BUCKET_NAME: str = "datadialogue-files"
    MINIO_USE_SSL: bool = False

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    MAX_FILE_SIZE_MB: int = 50
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
