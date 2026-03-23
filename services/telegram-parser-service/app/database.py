from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Берем строку подключения из .env (через docker-compose)
# Ожидается формат: postgresql://user:password@db_host:5432/db_name
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем движок подключения
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Проверка живое ли соединение перед использованием
)

# Создаем фабрику сессий (используется в твоем main.py: db = SessionLocal())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ArticleORM(Base):
    """
    Модель таблицы articles. 
    Должна точно совпадать со схемой твоей БД.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # В твоей БД автор NOT NULL. 
    # Так как в ТГ-каналах автор не всегда ясен, ставим заглушку
    author = Column(String(255), nullable=False, default="Telegram_Bot")
    
    title = Column(String(255), nullable=False)
    
    # Твоя БД использует 'content', а в коде парсеров это часто 'text'
    # Мы маппим это на колонку 'content', как в твоем SQL-скрипте
    content = Column(Text, nullable=False)
    
    source = Column(Text, nullable=False)
    
    # Защита от дубликатов по ссылке (используется в on_conflict_do_nothing)
    link = Column(Text, unique=True, nullable=False, index=True)
    
    # Дата публикации из Telegram
    pub_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)

def init_db():
    """Создает таблицу, если она еще не создана"""
    Base.metadata.create_all(bind=engine)
