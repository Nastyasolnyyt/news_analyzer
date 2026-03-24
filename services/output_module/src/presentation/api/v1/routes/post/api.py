from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from src.application.schemas.post import (
    PostFilterDTO,
    PostListResponseDTO,
    PostWithExternalModelsDTO,
)
from src.services.post import PostService


ROUTER = APIRouter(prefix="/posts", route_class=DishkaRoute)


@ROUTER.get("", response_model=PostListResponseDTO, summary="Список постов")
async def get_posts(
    post_service: FromDishka[PostService],
    filters: PostFilterDTO = Depends(),
) -> PostListResponseDTO:
    """Получение списка постов с фильтрацией, сортировкой и пагинацией."""
    return await post_service.get_posts(filters)


@ROUTER.get("/{post_id}", response_model=PostWithExternalModelsDTO, summary="Получить пост")
async def get_post(
    post_id: int,
    post_service: FromDishka[PostService],
) -> PostWithExternalModelsDTO:
    """Получение поста по ID с полной информацией."""
    result = await post_service.get_post(post_id)
    return result
