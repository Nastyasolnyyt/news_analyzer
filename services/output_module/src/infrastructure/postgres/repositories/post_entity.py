from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.post_entity import PostEntityDTO
from src.infrastructure.postgres.models.post_entity import PostEntity


class PostEntityDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ners_by_post(self, post_id: int) -> List[PostEntityDTO]:
        result = await self.session.execute(
            select(PostEntity).where(
                PostEntity.post_id == post_id,
            )
        )
        post_ners = result.scalars().all()
        return [PostEntityDTO.model_validate(post_ner.as_dict()) for post_ner in post_ners]

    async def get_posts_by_ner(self, ner_id: int) -> List[PostEntityDTO]:
        result = await self.session.execute(
            select(PostEntity).where(
                PostEntity.entity_id == ner_id,
            )
        )
        ner_posts = result.scalars().all()
        return [PostEntityDTO.model_validate(post_ner.as_dict()) for post_ner in ner_posts]
