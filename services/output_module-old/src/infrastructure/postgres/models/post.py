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


class Post(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(Text, nullable=False)

    # Relationships
    ##analyses = relationship("PostAnalysis", back_populates="post")
    ##entities = relationship("PostEntity", back_populates="post")
