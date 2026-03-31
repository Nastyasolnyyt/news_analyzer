# src/infrastructure/postgres/models/risk.py
from sqlalchemy import Column, ForeignKey, Integer, Text, Float, DateTime, func, String
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    
    # Тип риска: политический / экономический / социальный
    risk_type = Column(Text, nullable=False)
    
    #  Уровень риска (high / medium / low)
    risk_level = Column(String(20), nullable=True)
    
    # Уверенность классификатора
    confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("Article", back_populates="risks")