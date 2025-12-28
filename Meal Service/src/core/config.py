import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "software20251db.c3e0884ou51k.ap-southeast-2.rds.amazonaws.com")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "thanh")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "software20251")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/meal_db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

