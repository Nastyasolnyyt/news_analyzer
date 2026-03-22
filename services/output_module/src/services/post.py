from typing import Any
from src.application.schemas.post import PostFilterDTO, PostResponseDTO
from src.infrastructure.postgres.repository.post import PostDBGateWay

class PostService:
    def __init__(self, repository: PostDBGateWay):
        self.repository = repository

    async def get_posts(self, filters: PostFilterDTO):
        # Просто пробрасываем вызов в репозиторий
        return await self.repository.get_posts_with_filters(filters)

    async def get_post_by_id(self, post_id: int) -> Any:
        # Просто вызываем метод репозитория, который мы написали выше
        return await self.repository.get_post_by_id(post_id)