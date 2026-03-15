import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    
    db_url: str 
    openrouter_api_key: str

    class Config:
        
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()


if not settings.db_url.startswith("postgresql"):
    raise ValueError(f"Ошибка: Некорректный URL базы данных! Получено: {settings.db_url}")

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer)
    risk_type = Column(String)
    confidence = Column(Float)

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_risk_result(article_id: int, result):
    db = SessionLocal()
    try:
        risk = Risk(
            article_id=article_id, 
            risk_type=result.risk_type, 
            confidence=result.confidence
        )
        db.add(risk)
        db.commit()
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        db.rollback()
    finally:
        db.close()