from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from src.infrastructure.postgres.repositories.post_analysis import PostAnalysisDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay
from src.infrastructure.postgres.repositories.topic import TopicDBGateWay
from src.infrastructure.postgres.repositories.user import UserDBGateWay


class DBProvider(Provider):
    def __init__(self, url: URL):
        super().__init__()
        self.DATABASE_URL = url
        
        # Базовые настройки
        self.SQLALCHEMY_CONNECT_ARGS = {
            "prepared_statement_cache_size": 500,
        }
        
        # ДЛЯ RENDER: если в хосте есть render.com, добавляем ssl=True
        # Это заменяет собой ?sslmode=require, который не понимает asyncpg
        if url.host and "render.com" in url.host:
            self.SQLALCHEMY_CONNECT_ARGS["ssl"] = True

    @provide(scope=Scope.REQUEST)
    async def get_connection(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            self.DATABASE_URL,
            connect_args=self.SQLALCHEMY_CONNECT_ARGS, # Теперь здесь будет ssl=True если надо
            pool_size=30,
            max_overflow=50,
            pool_timeout=10,
            pool_recycle=1800,
            pool_pre_ping=True,
        )
        return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_db_session(
        self, connection: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with connection() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @provide(scope=Scope.REQUEST)
    async def get_post_gateway(self, db_session: AsyncSession) -> PostDBGateWay:
        return PostDBGateWay(db_session)

    @provide(scope=Scope.REQUEST)
    async def get_ner_gateway(self, db_session: AsyncSession) -> NamedEntityDBGateWay:
        return NamedEntityDBGateWay(db_session)

    @provide(scope=Scope.REQUEST)
    async def post_analysis_gateway(self, db_session: AsyncSession) -> PostAnalysisDBGateWay:
        return PostAnalysisDBGateWay(db_session)

    @provide(scope=Scope.REQUEST)
    async def get_topic_gateway(self, db_session: AsyncSession) -> TopicDBGateWay:
        return TopicDBGateWay(db_session)

    @provide(scope=Scope.REQUEST)
    async def get_post_entity_gateway(self, db_session: AsyncSession) -> PostEntityDBGateWay:
        return PostEntityDBGateWay(db_session)

    @provide(scope=Scope.REQUEST)
    async def get_user_gateway(self, db_session: AsyncSession) -> UserDBGateWay:
        return UserDBGateWay(db_session)
