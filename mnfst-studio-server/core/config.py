import os
from typing import Optional

class Config:
    # Database
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_HOST: str = "157.245.0.147"  # Fixed host IP for both environments
    DB_NAME: str = os.getenv("DB_NAME", "mnfst_studio_dev")

    # Environment
    ENV: str = os.getenv("ENV", "development")

    @property
    def DATABASE_URL(self) -> str:
        # For development
        if self.ENV == "development":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5436/{self.DB_NAME}"
        # For production
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5437/{self.DB_NAME}"

config = Config() 