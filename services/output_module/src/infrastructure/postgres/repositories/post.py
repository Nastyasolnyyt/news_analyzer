from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.post import PostFilterDTO
from src.infrastructure.postgres.models import Article, NamedEntity

class PostDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post(self, filters: PostFilterDTO):
        # Загружаем статью вместе со всеми связанными данными одним махом
        query = select(Article).options(
            joinedload(Article.risks),
            joinedload(Article.analyses),
            selectinload(Article.entities)
        )

        # Поиск по заголовку или контенту
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Article.title.ilike(search_term),
                    Article.text.ilike(search_term)
                )
            )

        # Считаем общее количество для пагинации
        count_query = select(func.count(Article.id))
        if filters.search:
            search_term = f"%{filters.search}%"
            count_query = count_query.where(
                or_(Article.title.ilike(search_term), Article.text.ilike(search_term))
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
            # Получаем анализ (первый, если есть)
            analysis = article.analyses[0] if article.analyses else None
            # Получаем риск (первый, если есть)
            risk = article.risks[0] if article.risks else None
            
            response_items.append({
                "post": article,
                "analysis": {
                    "tonality": analysis.tonality if analysis else 0.0,
                    "confidence": analysis.confidence if analysis else None,
                    "sentiment_label": analysis.sentiment_label if analysis else "neutral"
                },
                "risk": {
                    "risk_type": risk.risk_type if risk else "unknown",
                    "confidence": risk.confidence if risk else None
                },
                "entities": article.entities
            })

        return response_items, total

    async def get_post_by_id(self, post_id: int):
        query = select(Article).options(
            joinedload(Article.risks),
            joinedload(Article.analyses),
            selectinload(Article.entities)
        ).where(Article.id == post_id)

        result = await self.session.execute(query)
        article = result.scalars().unique().one_or_none()

        if not article:
            return None

        # Получаем анализ (первый, если есть)
        analysis = article.analyses[0] if article.analyses else None
        # Получаем риск (первый, если есть)
        risk = article.risks[0] if article.risks else None

        return {
            "post": article,
            "analysis": {
                "tonality": analysis.tonality if analysis else 0.0,
                "confidence": analysis.confidence if analysis else None,
                "sentiment_label": analysis.sentiment_label if analysis else "neutral"
            },
            "risk": {
                "risk_type": risk.risk_type if risk else "unknown",
                "confidence": risk.confidence if risk else None
            },
            "entities": article.entities
        }
