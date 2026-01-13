from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # bỏ qua các field dư trong .env
    )

    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    USER_SERVICE_URL: str = "http://user-service:8000"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/meal_db"

    # Redis Configuration
    REDIS_HOST: str = "redis-caching"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "myredis"

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-broker:9092"


settings = Settings()