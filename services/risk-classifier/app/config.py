# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    db_url: str = "postgresql://news_db_r386_user:d3RdNiRIt1B1iWzamwc3Tblto5FxDpJz@dpg-d68bevrh46gs73fc7ln0-a.oregon-postgres.render.com/news_db_r386"
    
    # API Keys
    openrouter_api_key: Optional[str] = None
    
    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    
    # Application
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Создаем глобальный объект настроек
settings = Settings()