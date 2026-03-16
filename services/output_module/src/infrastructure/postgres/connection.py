import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Получаем URL из .env (в Docker-сети обращаемся к сервису 'postgres')
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://news_db_r386_user:password@postgres:5432/news_db_r386"
)

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс, который ищут твои модели
class Base(DeclarativeBase):
    pass