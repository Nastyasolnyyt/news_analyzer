from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс моделей SQLAlchemy."""


class Sentiment(Base):
    """
    ORM-модель таблицы sentiments.

    CREATE TABLE sentiments (
        id SERIAL PRIMARY KEY,
        article_id INTEGER REFERENCES articles(id),
        sentiment_label TEXT NOT NULL,
        confidence_score REAL,
        analyzed_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    __tablename__ = "sentiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("articles.id"),
        nullable=False,
    )
    sentiment_label: Mapped[str] = mapped_column(String, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )



