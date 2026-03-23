from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    analyses = relationship("PostAnalysis", back_populates="topic")
