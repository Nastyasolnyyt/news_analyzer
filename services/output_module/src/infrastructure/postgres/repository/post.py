from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.post import PostFilterDTO, PostResponseDTO
from src.infrastructure.postgres.models import Article, Sentiment, Risk, Anomaly, Entity

class PostDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_posts_with_filters(self, filters: PostFilterDTO):
        # 1. Базовый запрос с подгрузкой связанных таблиц!
        # selectinload и joinedload говорят базе сделать JOIN автоматически
        query = select(Article).options(
            joinedload(Article.sentiment),
            joinedload(Article.risk),
            joinedload(Article.anomaly),
            selectinload(Article.entities)
        )

        # 2. Поиск по тексту (из твоего Search.vue)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Article.title.ilike(search_term),
                    Article.content.ilike(search_term)
                )
            )

        # 3. Фильтр по сущности (для EntityProfile.vue)
        if filters.entity_id:
            query = query.where(Article.entities.any(Entity.id == filters.entity_id))

        # 4. Подсчет общего количества
        count_query = select(func.count(Article.id))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # 5. Сортировка и пагинация
        if filters.order == "desc":
            query = query.order_by(Article.created_at.desc())
        else:
            query = query.order_by(Article.created_at.asc())

        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # 6. Выполнение запроса
        result = await self.session.execute(query)
        articles = result.scalars().all()

        # 7. Превращение ORM моделей в наш красивый JSON формат
        response_items = []
        for article in articles:
            # Безопасно достаем аналитику, если ее нет - ставим дефолтные значения
            analysis_dto = {
                "tonality": article.sentiment.tonality if article.sentiment else 0.0,
                "risk_level": article.risk.risk_level if article.risk else "low",
                "is_anomaly": article.anomaly.is_anomaly if article.anomaly else False
            }
            
            response_items.append({
                "post": article,
                "analysis": analysis_dto,
                "entities": article.entities
            })

        return response_items, total