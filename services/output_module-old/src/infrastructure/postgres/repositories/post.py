from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.post import PostNotFoundException
from src.application.schemas.post import PostDTO, PostFilterDTO
from src.infrastructure.postgres.models.post import Post
from src.infrastructure.postgres.models.post_analysis import PostAnalysis
from src.infrastructure.postgres.models.post_entity import PostEntity


class PostDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post(self, post_id: int) -> PostDTO:
        result = await self.session.execute(
            select(Post).where(
                Post.id == post_id,
            )
        )
        post = result.scalars().first()
        if post is None:
            raise PostNotFoundException()
        return PostDTO.model_validate(post.as_dict())

    async def get_posts_with_filters(self, filters: PostFilterDTO) -> tuple[list[PostDTO], int]:
        """Получает посты с фильтрацией, сортировкой и пагинацией."""
        # Базовый запрос с join для фильтрации по analysis
        query = (
            select(Post)
            .join(PostAnalysis, Post.id == PostAnalysis.post_id, isouter=True)
            .distinct()
        )

        # Применяем фильтры
        if filters.topic_id is not None:
            query = query.where(PostAnalysis.topic_id == filters.topic_id)
        if filters.emotion is not None:
            query = query.where(PostAnalysis.emotion == filters.emotion)
        if filters.tonality is not None:
            query = query.where(PostAnalysis.tonality == filters.tonality)
        if filters.relevance is not None:
            query = query.where(PostAnalysis.relevance == filters.relevance)
        if filters.entity_id is not None:
            # Фильтр по entity_id требует join с post_entities
            subquery = select(PostEntity.post_id).where(PostEntity.entity_id == filters.entity_id)
            query = query.where(Post.id.in_(subquery))

        # Получаем общее количество записей
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Применяем сортировку
        if filters.sort:
            sort_field = filters.sort.lower()
            order = filters.order.lower() if filters.order else "asc"

            if sort_field == "id":
                order_by_field = Post.id
            elif sort_field == "created_at":
                order_by_field = Post.created_at
            elif sort_field == "emotion":
                order_by_field = PostAnalysis.emotion
            elif sort_field == "tonality":
                order_by_field = PostAnalysis.tonality
            elif sort_field == "relevance":
                order_by_field = PostAnalysis.relevance
            else:
                order_by_field = Post.id  # По умолчанию

            if order == "desc":
                query = query.order_by(order_by_field.desc())
            else:
                query = query.order_by(order_by_field.asc())
        else:
            # По умолчанию сортируем по id
            query = query.order_by(Post.id.desc())

        # Применяем пагинацию
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        result = await self.session.execute(query)
        posts = result.scalars().all()
        return [PostDTO.model_validate(post.as_dict()) for post in posts], total
