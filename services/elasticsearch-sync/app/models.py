from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey,  JSON, ARRAY, Integer, Text
from datetime import datetime
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class NamedEntity(Base):
    __tablename__ = "named_entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    entities: Mapped[List["PostEntity"]] = relationship("PostEntity", back_populates="entity")


class PostEntity(Base):
    __tablename__ = "post_entities"
    post_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("named_entities.id"), primary_key=True)
    
    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="entities")
    entity: Mapped["NamedEntity"] = relationship("NamedEntity", back_populates="entities")


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(Text)
    pub_date: Mapped[Optional[datetime]]
    source: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    # Relationships
    risks: Mapped[List["Risk"]] = relationship("Risk", back_populates="article")
    entities: Mapped[List["PostEntity"]] = relationship("PostEntity", back_populates="article")


class Risk(Base):
    __tablename__ = "risks"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    risk_type: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[float]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="risks")


class Entity(Base):
     __tablename__ = "entities"
     id: Mapped[int] = mapped_column(primary_key=True)
     article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
     text: Mapped[str] = mapped_column(Text, nullable=False)
     type: Mapped[str] = mapped_column(Text, nullable=False)
     start_pos: Mapped[Optional[int]]
     end_pos: Mapped[Optional[int]]
     details: Mapped[Optional[dict]] = mapped_column(JSON)

class Cluster(Base):
    __tablename__ = "clusters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    article_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer))
    created_at: Mapped[datetime]