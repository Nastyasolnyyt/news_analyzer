from typing import List, Any

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException
from src.application.schemas.named_entity import EntityInfo, EntityMentionsFilterDTO, EntityDetailsResponse
from src.services.entity import EntityService


ROUTER = APIRouter(prefix="/entities", route_class=DishkaRoute)


@ROUTER.get(
    "",
    response_model=List[Any],
    summary="Получить список всех сущностей",
)
async def get_all_entities(
    entity_service: FromDishka[EntityService],
    limit: int = 100,
) -> List[Any]:
    """Получение списка всех сущностей с их статистикой упоминаний."""
    try:
        return await entity_service.get_all_entities(limit=limit)
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
