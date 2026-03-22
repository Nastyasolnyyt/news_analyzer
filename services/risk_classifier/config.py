from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Параметры БД
    db_url: str 
    
    # API Ключ
    openrouter_api_key: Optional[str] = None
    
    # Настройки Kafka (добавляем их сюда)
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "text_for_risk"       # Входной топик
    output_topic: str = "risk_classified"    # Выходной топик
    
    # Настройки логирования
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Если вы используете префиксы в .env (например KAFKA_...), 
        # pydantic сам их сопоставит, если они совпадают с именами полей.

settings = Settings()