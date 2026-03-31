# services/ner-service/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    
    kafka_bootstrap_servers: str = "kafka:9092"
    input_topic: str = "text_for_ner"
    output_topic: str = "entities_extracted"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()