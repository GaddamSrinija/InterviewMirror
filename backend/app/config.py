from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interview_mirror"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    GITHUB_TOKEN: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_CHAT_MODEL: str = "google/gemini-2.5-flash"
    OPENROUTER_EMBEDDING_MODEL: str = "openai/text-embedding-3-small"
    STORAGE_DIR: str = "storage"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()