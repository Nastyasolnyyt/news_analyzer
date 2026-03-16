from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class NamedEntity(Base):
    __tablename__ = "named_entities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    posts = relationship("PostEntity", back_populates="entity")
