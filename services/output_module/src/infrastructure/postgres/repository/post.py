from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.post import PostFilterDTO
from src.infrastructure.postgres.models import Article, Entity

class PostDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_posts_with_filters(self, filters: PostFilterDTO):
        query = select(Article).options(
            joinedload(Article.sentiment),
            joinedload(Article.risk),
            joinedload(Article.anomaly),
            selectinload(Article.entities)
        )

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Article.title.ilike(search_term),
                    Article.content.ilike(search_term)
                )
            )

        if filters.entity_id:
            query = query.where(Article.entities.any(Entity.id == filters.entity_id))

        # Подсчет total
        count_query = select(func.count(Article.id))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Сортировка и пагинация
        query = query.order_by(Article.created_at.desc() if filters.order == "desc" else Article.created_at.asc())
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        result = await self.session.execute(query)
        articles = result.scalars().unique().all() # unique() важен при joinedload!

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
        # Добавляем .unique(), так как при джоине сущностей строки могут дублироваться
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
                "is_anomaly": article.anomaly.is_anomaly if article.anomaly else "None"
            },
            "entities": article.entities
        }