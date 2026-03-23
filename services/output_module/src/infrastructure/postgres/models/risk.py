from sqlalchemy import Column, ForeignKey, Integer, Text, Float, DateTime, func
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    risk_type = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("Article", back_populates="risks")
