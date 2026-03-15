from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    db_url: str 
    
 
    openrouter_api_key: Optional[str] = None
    
    kafka_bootstrap_servers: str = "kafka:9092"
    
    log_level: str = "INFO"
    
    class Config:
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        env_prefix = "" 


settings = Settings()