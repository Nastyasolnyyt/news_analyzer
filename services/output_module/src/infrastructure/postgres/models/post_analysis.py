from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class PostAnalysis(Base):
    __tablename__ = "post_analysis"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    emotion = Column(Float, nullable=False)
    tonality = Column(Float, nullable=False)
    relevance = Column(Float, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="analyses")
    topic = relationship("Topic", back_populates="analyses")
