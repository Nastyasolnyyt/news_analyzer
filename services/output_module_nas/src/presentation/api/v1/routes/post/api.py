from typing import Any  # Добавили импорт для корректной типизации
from fastapi import APIRouter, Depends
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from src.application.schemas.post import PostFilterDTO, PostListResponseDTO
from src.services.post import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=PostListResponseDTO)
@inject
async def get_all_posts(
    service: FromDishka[PostService],
    filters: PostFilterDTO = Depends(),
) -> PostListResponseDTO:
    items, total = await service.get_posts(filters)
    
    return PostListResponseDTO(
        items=items,
        total=total,
        page=filters.page,
        page_size=filters.page_size
    )

# Исправлено: any (функция) заменена на Any (тип данных)
@router.get("/{post_id}")
@inject
async def get_post_by_id(
    post_id: int,
    service: FromDishka[PostService],
) -> Any: # Используй Any для теста
    try:
        post_data = await service.get_post_by_id(post_id)
        if not post_data:
            raise HTTPException(status_code=404, detail="Новость не найдена")
        return post_data
    except Exception as e:
        # Это выведет реальную причину 500 ошибки в консоль бэкенда!
        print(f"ОШИБКА БЭКЕНДА: {e}")
        raise HTTPException(status_code=500, detail=str(e))