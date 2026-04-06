from typing import List, Optional

from src.application.schemas.named_entity import EntityInfo, EntityMentionsFilterDTO
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay


class EntityService:
    def __init__(
        self,
        ner_gateway: NamedEntityDBGateWay,
        post_entity_gateway: PostEntityDBGateWay,
        post_gateway: PostDBGateWay,
    ):
        # ИСПРАВЛЕНО: Убрали лишнюю упаковку в кортеж
        self.ner_gateway = ner_gateway
        self.post_entity_gateway = post_entity_gateway
        self.post_gateway = post_gateway

    async def get_entity_mentions(
        self, entity_id: int, filters: Optional[EntityMentionsFilterDTO] = None
    ) -> List[EntityInfo]:
        """Получает упоминания сущности с фильтрацией по датам."""
        entity = await self.ner_gateway.get_named_entity(entity_id)
        
        # Защита: если сущность не найдена в БД
        if not entity:
            return []

        posts_entity = await self.post_entity_gateway.get_posts_by_ner(entity.id)
        
        # ИСПРАВЛЕНО: Заменили get_post на get_post_by_id и добавили проверку на существование поста
        posts = []
        for post_entity in posts_entity:
            post = await self.post_gateway.get_post_by_id(post_entity.post_id)
            if post:
                posts.append(post)

        # Применяем фильтрацию по датам
        if filters:
            if filters.start is not None:
                posts = [post for post in posts if post.created_at >= filters.start]
            if filters.end is not None:
                posts = [post for post in posts if post.created_at <= filters.end]

        return [
            EntityInfo(entity=entity, post_id=post.id, mentioned_at=post.created_at)
            for post in posts
        ]

    async def get_entity_info(self, entity_id: int) -> List[EntityInfo]:
        """Старый метод для обратной совместимости."""
        return await self.get_entity_mentions(entity_id, filters=None)