from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_input_topic: str = "entities_extracted"
    kafka_group_id: str = "knowledge-graph-sync-group"
    kafka_consumer_retry_interval_sec: float = 3.0
    kafka_consumer_max_retries: int = 0  # 0 = retry forever until connected

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    rest_port: int = 8200
    rest_host: str = "0.0.0.0"

    min_weight_threshold: int = 1
    max_entities_per_article: int = 50


settings = Settings()
