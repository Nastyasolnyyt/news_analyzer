from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.named_entity import NamedEntityNotFoundException
from src.application.schemas.named_entity import NamedEntityDTO
from src.infrastructure.postgres.models.named_entity import NamedEntity


class NamedEntityDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_named_entity(self, named_entity_id: int) -> NamedEntityDTO:
        result = await self.session.execute(
            select(NamedEntity).where(
                NamedEntity.id == named_entity_id,
            )
        )
        named_entity = result.scalars().first()
        if named_entity is None:
            raise NamedEntityNotFoundException()
        return NamedEntityDTO.model_validate(named_entity.as_dict())
