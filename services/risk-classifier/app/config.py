from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # База данных
    db_url: str
    
    # API
    openrouter_api_key: str
    
    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_group_id: str = "risk-classifier-group"
    input_topic: str = "text_for_risk"
    output_topic: str = "risk_classified"
    
    # Логирование
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()