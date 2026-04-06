from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/issues.db"
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_TYPE: str = "faiss"
    SIMILARITY_THRESHOLD: float = 0.7
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
