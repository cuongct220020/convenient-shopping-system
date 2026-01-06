from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/shopping_storage_db"

    # Redis Configuration
    REDIS_HOST: str = "redis-caching"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "myredis"

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-broker:9092"

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()