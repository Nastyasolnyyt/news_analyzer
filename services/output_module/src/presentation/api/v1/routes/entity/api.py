from typing import List, Any, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException
from src.application.schemas.named_entity import EntityInfo, EntityMentionsFilterDTO, EntityDetailsResponse, CreateEntityDTO, NamedEntityDTO
from src.services.entity import EntityService


ROUTER = APIRouter(prefix="/entities", route_class=DishkaRoute)


@ROUTER.post(
    "",
    response_model=NamedEntityDTO,
    summary="Создать новую сущность",
    status_code=201,
)
async def create_entity(
    entity_service: FromDishka[EntityService],
    data: CreateEntityDTO,
) -> NamedEntityDTO:
    """
    Создание новой сущности для отслеживания пользователем.
    Можно создать организацию (ORG) или персону (PER).
    """
    try:
        created_entity = await entity_service.create_entity(
            name=data.name,
            entity_type=data.entity_type
        )
        return created_entity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@ROUTER.get(
    "",
    response_model=List[Any],
    summary="Получить список всех сущностей",
)
async def get_all_entities(
    entity_service: FromDishka[EntityService],
    limit: int = 100,
    entity_type: Optional[str] = None,
) -> List[Any]:
    """Получение списка всех сущностей с их статистикой упоминаний. Можно фильтровать по типу сущности."""
    try:
        return await entity_service.get_all_entities(limit=limit, entity_type=entity_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@ROUTER.get(
    "/{entity_id}/mentions",
    response_model=List[EntityInfo],
    summary="Получить упоминания сущности",
)
async def get_entity_mentions(
    entity_service: FromDishka[EntityService],
    entity_id: int,
    filters: EntityMentionsFilterDTO = Depends(),
) -> List[EntityInfo]:
    """Получение упоминаний сущности с фильтрацией по датам (start, end)."""
    return await entity_service.get_entity_mentions(entity_id, filters)


@ROUTER.get(
    "/{entity_id}/details",
    response_model=EntityDetailsResponse,
    summary="Получить детальную информацию о сущности",
)
async def get_entity_details(
    entity_service: FromDishka[EntityService],
    entity_id: int,
) -> EntityDetailsResponse:
    """
    Получение полной информации о сущности для отображения в профиле.
    Включает:
    - Основные данные (название, тип, описание)
    - Связанные сущности (партнёры, ключевые персоны)
    - Динамику упоминаний (график по неделям)
    - Последние новости/события
    """
    try:
        return await entity_service.get_entity_details(entity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@ROUTER.get(
    "/top/24h",
    response_model=List[Any],
    summary="Получить топ сущностей за 24 часа по росту интереса",
)
async def get_top_entities_24h(
    entity_service: FromDishka[EntityService],
    limit: int = 5,
) -> List[Any]:
    """
    Получение топ-5 сущностей с наибольшим ростом упоминаний за последние 24 часа.
    Сравнивает период последних 24 часов с предыдущими 24 часами.
    Возвращает сущности с процентом изменения и направлением тренда (up/down/flat).
    """
    try:
        return await entity_service.get_top_entities_24h(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
