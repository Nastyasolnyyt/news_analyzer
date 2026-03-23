from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки сервиса sentiment_analysis, читаемые из переменных окружения."""

    kafka_bootstrap_servers: str = Field(
        "localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_group_id: str = Field(
        "sentiment-analysis-group", env="KAFKA_GROUP_ID"
    )
    kafka_topic: str = Field(
        "text_for_sentiment", env="KAFKA_TOPIC"
    )
    kafka_auto_offset_reset: str = Field(
        "earliest", env="KAFKA_AUTO_OFFSET_RESET"
    )
    kafka_enable_auto_commit: bool = Field(
        False, env="KAFKA_ENABLE_AUTO_COMMIT"
    )

    database_url: str = Field(..., env="DATABASE_URL")

    sentiment_model_name: str = Field(
    "blanchefort/rubert-base-cased-sentiment", env="SENTIMENT_MODEL_NAME"
    )

    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""
    return Settings()