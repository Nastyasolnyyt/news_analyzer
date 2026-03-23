from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PostAnalysis(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True, name="article_id")
    tonality = Column(Float, nullable=False, default=0.0, name="confidence")
    label = Column(String, nullable=True, name="sentiment_label")