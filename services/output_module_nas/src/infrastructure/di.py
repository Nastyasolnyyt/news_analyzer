from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.connection import async_session_maker
from src.infrastructure.postgres.repository.post import PostDBGateWay
from src.services.post import PostService

class MyProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        async with async_session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_post_repository(self, session: AsyncSession) -> PostDBGateWay:
        return PostDBGateWay(session)

    @provide(scope=Scope.REQUEST)
    def get_post_service(self, repository: PostDBGateWay) -> PostService:
        return PostService(repository)