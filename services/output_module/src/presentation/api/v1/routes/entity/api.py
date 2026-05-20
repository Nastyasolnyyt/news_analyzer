"""
ИСПРАВЛЕНО:
1. POST /entities — корректно регистрируется и работает через DI (dishka)
2. Добавлена валидация типа сущности с понятными сообщениями
3. Исправлен маршрут /top/24h — не конфликтует с /{entity_id}
"""
from typing import List, Any, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException, status

from src.application.schemas.named_entity import (
    EntityInfo,
    EntityMentionsFilterDTO,
    EntityDetailsResponse,
    CreateEntityDTO,
    NamedEntityDTO,
)
from src.services.entity import EntityService

import logging
logger = logging.getLogger(__name__)

ROUTER = APIRouter(prefix="/entities", route_class=DishkaRoute)

# ВАЖНО: маршруты без параметров должны быть ДО маршрутов с {entity_id}
# иначе /top/24h будет перехвачен как entity_id="top"

@ROUTER.get(
    "/top/24h",
    response_model=List[Any],
    summary="Топ сущностей за 24 часа",
)
async def get_top_entities_24h(
    entity_service: FromDishka[EntityService],
    limit: int = 5,
) -> List[Any]:
    """Топ-5 сущностей с наибольшим ростом упоминаний за последние 24 часа."""
    try:
        return await entity_service.get_top_entities_24h(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_top_entities_24h: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@ROUTER.get(
    "",
    response_model=List[Any],
    summary="Список всех сущностей",
)
async def get_all_entities(
    entity_service: FromDishka[EntityService],
    limit: int = 100,
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Any]:
    """Получение списка всех сущностей с их статистикой упоминаний.
    
    Query Parameters:
    - limit: максимальное количество сущностей (по умолчанию 100)
    - entity_type: фильтр по типу (ORG, PER, LOC и т.д.)
    - search: поиск по названию (case-insensitive)
    """
    try:
        return await entity_service.get_all_entities(limit=limit, entity_type=entity_type, search=search)
    except Exception as e:
        logger.error(f"Error in get_all_entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@ROUTER.post(
    "",
    response_model=NamedEntityDTO,
    summary="Создать новую сущность для отслеживания",
    status_code=status.HTTP_201_CREATED,
)
async def create_entity(
    data: CreateEntityDTO,
    entity_service: FromDishka[EntityService],
) -> NamedEntityDTO:
    """
    Создание новой сущности (организация или персона) для отслеживания.

    Параметры:
    - **name**: Название сущности (например: "Газпром", "Путин В.В.")
    - **entity_type**: Тип — `ORG` (организация) или `PER` (персона)

    После создания сущность начнёт автоматически отслеживаться в новых статьях.
    """
    # Нормализуем тип сущности
    entity_type_normalized = data.entity_type.upper().strip()

    # Маппинг допустимых типов
    type_aliases = {
        "ORG": "ORG",
        "ORGANIZATION": "ORG",
        "ОРГАНИЗАЦИЯ": "ORG",
        "PER": "PER",
        "PERSON": "PER",
        "ПЕРСОНА": "PER",
        "ЧЕЛОВЕК": "PER",
        "LOC": "LOC",
        "LOCATION": "LOC",
        "ЛОКАЦИЯ": "LOC",
    }

    normalized_type = type_aliases.get(entity_type_normalized)
    if not normalized_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Недопустимый тип сущности: '{data.entity_type}'. "
                f"Допустимые значения: ORG (организация), PER (персона), LOC (место)"
            ),
        )

    try:
        created = await entity_service.create_entity(
            name=data.name.strip(),
            entity_type=normalized_type,
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating entity '{data.name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании сущности: {str(e)}",
        )


@ROUTER.get(
    "/{entity_id}/mentions",
    response_model=List[EntityInfo],
    summary="Упоминания сущности",
)
async def get_entity_mentions(
    entity_service: FromDishka[EntityService],
    entity_id: int,
    filters: EntityMentionsFilterDTO = Depends(),
) -> List[EntityInfo]:
    """Упоминания сущности с фильтрацией по датам (start, end)."""
    return await entity_service.get_entity_mentions(entity_id, filters)


@ROUTER.get(
    "/{entity_id}/details",
    response_model=EntityDetailsResponse,
    summary="Детальная информация о сущности",
)
async def get_entity_details(
    entity_service: FromDishka[EntityService],
    entity_id: int,
) -> EntityDetailsResponse:
    """Полная информация о сущности: связи, статистика упоминаний, последние новости."""
    try:
        return await entity_service.get_entity_details(entity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_entity_details for {entity_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")