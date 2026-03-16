from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from src.application.schemas.named_entity import EntityInfo, EntityMentionsFilterDTO
from src.application.schemas.user import UserDTO
from src.presentation.api.v1.routes.auth_dependencies import get_current_user
from src.services.entity import EntityService


ROUTER = APIRouter(prefix="/entities", route_class=DishkaRoute)


@ROUTER.get(
    "/{entity_id}/mentions",
    response_model=List[EntityInfo],
    summary="Получить упоминания сущности",
)
async def get_entity_mentions(
    entity_service: FromDishka[EntityService],
    entity_id: int,
    filters: EntityMentionsFilterDTO = Depends(),
    user: UserDTO = Depends(get_current_user),
) -> List[EntityInfo]:
    """Получение упоминаний сущности с фильтрацией по датам (start, end)."""
    return await entity_service.get_entity_mentions(entity_id, filters)
