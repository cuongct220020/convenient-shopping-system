from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # bỏ qua các field dư trong .env
    )

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/shopping_storage_db"

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-broker:9092"

settings = Settings()