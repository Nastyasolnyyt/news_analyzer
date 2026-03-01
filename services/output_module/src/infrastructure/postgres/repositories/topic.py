from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.topic import TopicNotFoundException
from src.application.schemas.topic import TopicDTO
from src.infrastructure.postgres.models.topic import Topic


class TopicDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_topic(self, topic_id: int) -> TopicDTO:
        result = await self.session.execute(
            select(Topic).where(
                Topic.id == topic_id,
            )
        )
        topic = result.scalars().first()
        if topic is None:
            raise TopicNotFoundException()
        return TopicDTO.model_validate(topic.as_dict())
