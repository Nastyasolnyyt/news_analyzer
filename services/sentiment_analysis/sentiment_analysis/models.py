from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PostAnalysis(Base):
    __tablename__ = "post_analysis"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    tonality = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)