from src.application.schemas.post import PostFilterDTO, PostListResponseDTO, PostResponseDTO
from src.infrastructure.postgres.repository.post import PostDBGateWay

class PostService:
    def __init__(self, repository: PostDBGateWay):
        self.repository = repository

    async def get_posts(self, filters: PostFilterDTO) -> tuple[list[PostResponseDTO], int]:
        # Вызываем репозиторий, который делает красивые JOIN-ы
        items, total = await self.repository.get_posts_with_filters(filters)
        
        # Здесь можно добавить бизнес-логику (например, фильтрацию запрещенных слов)
        return items, total