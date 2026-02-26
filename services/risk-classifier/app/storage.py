from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "postgresql://news_db_r386_user:d3RdNiRIt1B1iWzamwc3Tblto5FxDpJz@dpg-d68bevrh46gs73fc7ln0-a.oregon-postgres.render.com/news_db_r386"
    openrouter_api_key: str  # Будет задан через env

    class Config:
        env_file = ".env"

settings = Settings()

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
    risk = Risk(article_id=article_id, risk_type=result.risk_type, confidence=result.confidence)
    db.add(risk)
    db.commit()
    db.close()