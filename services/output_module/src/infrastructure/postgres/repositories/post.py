from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.post import PostFilterDTO
from src.infrastructure.postgres.models import Article, Entity

class PostDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_posts_with_filters(self, filters: PostFilterDTO):
        # Загружаем статью вместе со всеми связанными данными одним махом
        query = select(Article).options(
            joinedload(Article.sentiment),
            joinedload(Article.risk),
            joinedload(Article.anomaly),
            selectinload(Article.entities)
        )

        # Поиск по заголовку или контенту
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Article.title.ilike(search_term),
                    Article.content.ilike(search_term)
                )
            )

        # Считаем общее количество для пагинации
        count_query = select(func.count(Article.id))
        if filters.search:
            search_term = f"%{filters.search}%"
            count_query = count_query.where(
                or_(Article.title.ilike(search_term), Article.content.ilike(search_term))
            )
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Сортировка и пагинация
        if filters.order == "desc":
            query = query.order_by(Article.created_at.desc())
        else:
            query = query.order_by(Article.created_at.asc())

        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        result = await self.session.execute(query)
        articles = result.scalars().unique().all()

        # Формируем список для DTO
        response_items = []
        for article in articles:
            response_items.append({
                "post": article,
                "analysis": {
                    "tonality": article.sentiment.tonality if article.sentiment else 0.0,
                    "risk_level": article.risk.risk_level if article.risk else "low",
                    "is_anomaly": article.anomaly.is_anomaly if article.anomaly else False
                },
                "entities": article.entities
            })

        return response_items, total

    async def get_post_by_id(self, post_id: int):
        query = select(Article).options(
            joinedload(Article.sentiment),
            joinedload(Article.risk),
            joinedload(Article.anomaly),
            selectinload(Article.entities)
        ).where(Article.id == post_id)

        result = await self.session.execute(query)
        article = result.scalars().unique().one_or_none()

        if not article:
            return None

        return {
            "post": article,
            "analysis": {
                "tonality": article.sentiment.tonality if article.sentiment else 0.0,
                "risk_level": article.risk.risk_level if article.risk else "low",
                "is_anomaly": article.anomaly.is_anomaly if article.anomaly else False
            },
            "entities": article.entities
        }
