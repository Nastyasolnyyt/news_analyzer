from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    
    openrouter_api_key: Optional[str] = None
    
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "risk_types_done"
    output_topic: str = "risk_final_ready"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()