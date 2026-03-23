from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class PostEntity(Base):
    __tablename__ = "post_entities"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    entity_id = Column(
        Integer, ForeignKey("named_entities.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    post = relationship("Post", back_populates="entities")
    entity = relationship("NamedEntity", back_populates="posts")
