from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.connection import Base


class PostAnalysis(Base):
    __tablename__ = "post_analysis"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    emotion = Column(Float, nullable=True)
    tonality = Column(Float, nullable=True)
    relevance = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    sentiment_label = Column(String(50), nullable=True)

    # Relationships
    article = relationship("Article", back_populates="analyses")
    topic = relationship("Topic", back_populates="analyses")
