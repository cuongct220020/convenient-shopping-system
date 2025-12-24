from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    # Database Configuration
    DB_HOST: str = "software20251db.c3e0884ou51k.ap-southeast-2.rds.amazonaws.com"
    DB_PORT: int = 5432
    DB_USER: str = "thanh"
    DB_PASSWORD: str = "software20251"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

