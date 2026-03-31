from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    link = Column(Text, nullable=True)
    source = Column(Text, nullable=False)
    pub_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    analyses = relationship("PostAnalysis", back_populates="article")
    entities = relationship("PostEntity", back_populates="article")
    risks = relationship("Risk", back_populates="article", uselist=False)
