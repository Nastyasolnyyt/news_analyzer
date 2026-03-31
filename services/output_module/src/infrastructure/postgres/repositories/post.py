"""
Исправленный репозиторий для получения постов.
КРИТИЧЕСКИ ВАЖНО: загружает данные из таблицы risks!
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload, outerjoin
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.post import PostNotFoundException
from src.application.schemas.post import PostFilterDTO, PostBaseDTO
from src.infrastructure.postgres.models.post import Article
from src.infrastructure.postgres.models.risk import Risk


class PostDBGateWay:
    """Репозиторий для работы с постами + risks."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_by_id(self, post_id: int) -> Article:
        """
        Получить пост по ID.
        Гарантированно загружает все связанные данные.
        """
        query = select(Article).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
            selectinload(Article.entities),
        ).where(Article.id == post_id)
        
        result = await self.session.execute(query)
        article = result.scalars().unique().one_or_none()
        
        if not article:
            raise PostNotFoundException()
        
        return article

    async def get_posts_with_filters(
        self, filters: PostFilterDTO
    ) -> Tuple[List[dict], int]:
        """
        Получить список постов с фильтрацией.
        ВАЖНО: подключаем таблицу risks через outerjoin!
        """
        
        # Основной запрос: Article + анализ + сущности + РИСК
        query = select(Article).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
            selectinload(Article.entities),
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
        
        # Подсчет общего количества
        count_query = select(func.count(Article.id)).select_from(Article)
        if filters.search:
            search_term = f"%{filters.search}%"
            count_query = count_query.where(
                or_(
                    Article.title.ilike(search_term),
                    Article.text.ilike(search_term)
                )
            )
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Сортировка
        if filters.order == "desc":
            query = query.order_by(Article.created_at.desc())
        else:
            query = query.order_by(Article.created_at.asc())
        
        # Пагинация
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        # Выполнение запроса
        result = await self.session.execute(query)
        articles = result.scalars().unique().all()
        
        # Формирование ответа: обогащаем каждый пост данными из risks
        response_items = []
        for article in articles:
            analysis = article.analyses[0] if article.analyses else None
            risk = None
            if hasattr(article, 'risk') and article.risk:
                risk = article.risk  # one-to-one
            elif hasattr(article, 'risks') and article.risks and len(article.risks) > 0:
                risk = article.risks[0]  # one-to-many
            
            response_items.append({
                "post": article,
                "analysis": analysis,
                "risk": risk,  # ЭТО КРИТИЧНО: загружаем risk из article.risks!
                "entities": article.entities or []
            })
        
        return response_items, total

    async def get_posts_by_topic_id(self, topic_id: int, limit: int = 10):
        """Получить посты по теме."""
        from src.infrastructure.postgres.models.post_analysis import PostAnalysis
        
        query = select(Article).join(PostAnalysis).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
            selectinload(Article.entities),
        ).where(PostAnalysis.topic_id == topic_id).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def search_posts(
        self, query_text: str, limit: int = 20
    ) -> List[Article]:
        """Полнотекстовый поиск по постам."""
        search_term = f"%{query_text}%"
        query = select(Article).where(
            or_(
                Article.title.ilike(search_term),
                Article.text.ilike(search_term),
            )
        ).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def get_recent_posts(self, limit: int = 10) -> List[Article]:
        """Получить последние посты."""
        query = select(Article).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
            selectinload(Article.entities),
        ).order_by(Article.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def get_high_risk_posts(self, limit: int = 10) -> List[Article]:
        """Получить посты с высоким риском."""
        from src.infrastructure.postgres.models.risk import Risk
        
        query = select(Article).join(Risk).options(
            joinedload(Article.analyses),
            joinedload(Article.risks),
        ).where(Risk.risk_level == "high").order_by(
            Article.created_at.desc()
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def get_posts_count(self) -> int:
        """Получить общее количество постов."""
        result = await self.session.execute(select(func.count(Article.id)))
        return result.scalar() or 0