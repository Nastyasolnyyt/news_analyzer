from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, text, Text, REAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.postgres.connection import Base

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, name="text")
    source: Mapped[str] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)
    pub_date: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    sentiment: Mapped["Sentiment"] = relationship(back_populates="article", uselist=False)
    risk: Mapped["Risk"] = relationship(back_populates="article", uselist=False)
    anomaly: Mapped["Anomaly"] = relationship(back_populates="article", uselist=False)
    entities: Mapped[List["Entity"]] = relationship(back_populates="article")

class Sentiment(Base):
    __tablename__ = "sentiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), name="article_id")
    tonality: Mapped[float] = mapped_column(REAL, name="confidence")
    label: Mapped[str] = mapped_column(Text, name="sentiment_label")

    article: Mapped["Article"] = relationship(back_populates="sentiment")

class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), name="article_id")
    risk_level: Mapped[str] = mapped_column(Text, name="risk_type")
    # Колонку description убрали, так как её нет в psql

    article: Mapped["Article"] = relationship(back_populates="risk")

class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), name="article_id")
    # В БД это anomaly_type, отображаем в переменную is_anomaly
    is_anomaly: Mapped[str] = mapped_column(Text, name="anomaly_type")

    article: Mapped["Article"] = relationship(back_populates="anomaly")

class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), name="article_id")
    name: Mapped[str] = mapped_column(Text, name="text")
    type: Mapped[str] = mapped_column(Text)

    article: Mapped["Article"] = relationship(back_populates="entities")