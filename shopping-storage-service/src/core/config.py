from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-broker:9092"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

