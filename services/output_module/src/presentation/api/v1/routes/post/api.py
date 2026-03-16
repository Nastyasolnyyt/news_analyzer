from fastapi import APIRouter, Depends
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from src.application.schemas.post import PostFilterDTO, PostListResponseDTO
from src.services.post import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=PostListResponseDTO)
@inject  # Позволяет Dishka прокидывать PostService автоматически
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