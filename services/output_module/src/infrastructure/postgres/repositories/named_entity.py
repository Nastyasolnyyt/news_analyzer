from sqlalchemy import select, and_
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

    async def get_named_entity_by_name_and_type(self, name: str, entity_type: str) -> NamedEntityDTO | None:
        """Получить сущность по названию и типу (для проверки дублирования)"""
        result = await self.session.execute(
            select(NamedEntity).where(
                and_(
                    NamedEntity.name.ilike(name),  # Case-insensitive поиск
                    NamedEntity.entity_type == entity_type,
                )
            )
        )
        entity = result.scalars().first()
        return NamedEntityDTO.model_validate(entity.as_dict()) if entity else None

    async def create_named_entity(self, name: str, entity_type: str) -> NamedEntityDTO:
        """Создать новую сущность в БД с проверкой на дублирование"""
        # Проверяем, существует ли уже такая сущность
        existing = await self.get_named_entity_by_name_and_type(name, entity_type)
        if existing:
            raise ValueError(
                f"❌ Сущность '{name}' типа '{entity_type}' уже существует в системе (ID: {existing.id}). "
                f"Добавьте другую сущность или используйте существующую."
            )
        
        new_entity = NamedEntity(name=name, entity_type=entity_type)
        self.session.add(new_entity)
        await self.session.flush()  # Получаем ID без коммита
        return NamedEntityDTO.model_validate(new_entity.as_dict())
