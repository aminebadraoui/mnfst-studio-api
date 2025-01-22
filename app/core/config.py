from pydantic_settings import BaseSettings
from functools import lru_cache
from datetime import timedelta

class Settings(BaseSettings):
    PROJECT_NAME: str = "mnfst-studio"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    ENVIRONMENT: str = "development"

    # JWT Settings
    SECRET_KEY: str = "/TfxcJ6CEvYt3/gRAS3Pq2YQMPJZUjBj7bntSrI40wo="  # In production, use a secure secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env.development"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
