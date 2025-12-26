from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    # Database Configuration
    DB_HOST: str = "software20251db.c3e0884ou51k.ap-southeast-2.rds.amazonaws.com"
    DB_PORT: int = 5432
    DB_USER: str = "thanh"
    DB_PASSWORD: str = "software20251"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/recipe_db"

    # Elasticsearch Configuration
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_USERNAME: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

