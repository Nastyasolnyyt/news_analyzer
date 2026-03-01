from typing import Any, AsyncGenerator, Dict

from sqlalchemy import inspect
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapper
from src.core.config import env_settings


class Base(DeclarativeBase):
    def as_dict(self) -> Dict[str, Any]:
        """
        Преобразует модель SQLAlchemy в словарь.
        """
        mapper = inspect(self.__class__)
        if not isinstance(mapper, Mapper):
            raise TypeError(f"{self.__class__.__name__} is not a mapped SQLAlchemy model.")
        return {c.key: getattr(self, c.key) for c in mapper.columns}


SQLALCHEMY_CONNECT_ARGS = {
    "prepared_statement_cache_size": 500,
}

DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=env_settings.PG_USERNAME,
    password=env_settings.PG_PASSWORD,
    database=env_settings.PG_DATABASE,
    host=env_settings.PG_HOST,
    port=env_settings.PG_PORT,
)
engine = create_async_engine(
    DATABASE_URL,
    connect_args=SQLALCHEMY_CONNECT_ARGS,
    pool_size=30,  # базовое количество постоянных подключений
    max_overflow=50,  # сколько можно создать сверху
    pool_timeout=10,  # ждать максимум 10 секунд
    pool_recycle=1800,  # пересоздавать подключения каждые 30 минут
    pool_pre_ping=True,  # проверять перед использованием
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
