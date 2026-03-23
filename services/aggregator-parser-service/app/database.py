from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Получаем строку подключения из окружения
# В docker-compose это должно быть: DATABASE_URL=postgresql://user:password@db_host:5432/db_name
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем движок (engine). 
# pool_pre_ping=True помогает избежать ошибок при обрыве соединения с БД
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

# Создаем фабрику сессий для использования в main.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ArticleORM(Base):
    """
    Класс-модель, полностью соответствующий твоей таблице 'articles'.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # author помечен как NOT NULL в твоей БД
    author = Column(String(255), nullable=False, default="System") 
    
    title = Column(String(255), nullable=False)
    
    # В твоей БД колонка называется 'content', а в моделях парсера 'text'.
    # Мы маппим её здесь как 'content'.
    content = Column(Text, nullable=False)
    
    source = Column(Text, nullable=False)
    
    # link UNIQUE и NOT NULL — это твой ключ для on_conflict_do_nothing
    link = Column(Text, unique=True, nullable=False, index=True)
    
    # Используем TIMESTAMPTZ, как в твоем SQL-скрипте
    pub_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
# Функция для инициализации таблиц (если их еще нет)
def init_db():
    Base.metadata.create_all(bind=engine)
