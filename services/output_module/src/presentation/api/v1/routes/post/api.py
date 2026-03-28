from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
# Добавь эту строку в импорты:
from src.infrastructure.postgres.repositories.post_analysis import PostAnalysisDBGateWay
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
@ROUTER.get("/{post_id}/analysis", response_model=dict, summary="Получить анализ поста")
async def get_post_analysis(
    post_id: int,
    post_service: FromDishka[PostService],
    analysis_gateway: FromDishka[PostAnalysisDBGateWay],
    topic_gateway: FromDishka[TopicDBGateWay],
) -> dict:
    """
    Получает полный анализ поста: 
    - тональность (sentiment)
    - тему/кластер
    - эмоции и релевантность
    """
    try:
        # 1. Проверяем что пост существует
        post = await post_service.get_post(post_id)
        
        # 2. Получаем анализ
        try:
            analysis = await analysis_gateway.get_post_analysis(post_id)
        except:
            analysis = None
        
        # 3. Получаем тему
        topic = None
        if analysis and analysis.topic_id:
            try:
                topic = await topic_gateway.get_topic(analysis.topic_id)
            except:
                topic = None
        
        return {
            "success": True,
            "post_id": post_id,
            "post": {
                "title": post.title,
                "text": post.text[:500],  # первые 500 символов
                "source": post.source,
                "pub_date": post.pub_date.isoformat() if post.pub_date else None,
            },
            "analysis": {
                "sentiment": analysis.sentiment_label or "neutral" if analysis else "neutral",
                "tonality": float(analysis.tonality) if analysis and analysis.tonality is not None else 0.0,
                "confidence": float(analysis.confidence) if analysis and analysis.confidence is not None else 0.0,
                "emotion": float(analysis.emotion) if analysis and analysis.emotion is not None else 0.0,
                "relevance": float(analysis.relevance) if analysis and analysis.relevance is not None else 0.0,
            },
            "topic": {
                "id": topic.id,
                "name": topic.name,
            } if topic else None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "post_id": post_id,
        }