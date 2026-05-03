"""
Исправленный репозиторий для получения постов.
Решает проблему "Статья не найдена".
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.post import PostNotFoundException
from src.application.schemas.post import PostFilterDTO, PostBaseDTO
from src.infrastructure.postgres.models.post import Article


class PostDBGateWay:
    """Исправленный gateway для работы с постами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_by_id(self, post_id: int) -> Article:
        """
        Получить пост по ID.
        Гарантированно загружает все связанные данные.
        """
        query = select(Article).options(
            # Eager loading всех связей
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
        Возвращает список словарей для удобства в service слое.
        """
        """
        Получить список постов с фильтрацией.
        Возвращает список словарей для удобства в service слое.
        Использует eager loading для предотвращения проблемы N+1.
        """
        from src.infrastructure.postgres.models.risk import Risk
        from src.infrastructure.postgres.models.post_analysis import PostAnalysis
        from src.infrastructure.postgres.models.topic import Topic
        from src.infrastructure.postgres.models.post_entity import PostEntity
        from src.infrastructure.postgres.models.named_entity import NamedEntity

        # Основной запрос с eager loading всех связанных данных
        query = select(Article).options(
            joinedload(Article.analyses).joinedload(PostAnalysis.topic),
            joinedload(Article.risks),
            selectinload(Article.entities).joinedload(PostEntity.entity),
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
        
        # Фильтрация по уровню риска
        if filters.risk_level:
            query = query.join(Risk).where(Risk.risk_level == filters.risk_level.lower())
        
        # Фильтрация по типу риска
        if filters.risk_type:
            if not filters.risk_level:  # Если еще не сделали JOIN
                query = query.join(Risk)
            query = query.where(Risk.risk_type == filters.risk_type.lower())
        
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
        if filters.risk_level or filters.risk_type:
            count_query = count_query.select_from(Article).join(Risk)
            if filters.risk_level:
                count_query = count_query.where(Risk.risk_level == filters.risk_level.lower())
            if filters.risk_type:
                count_query = count_query.where(Risk.risk_type == filters.risk_type.lower())
        
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
        
        # Формирование ответа
        response_items = []
        for article in articles:
            # Безопасно извлекаем данные
            analysis = article.analyses[0] if article.analyses else None
            risk = article.risks[0] if article.risks else None
            
            response_items.append({
                "post": article,
                "analysis": analysis,
                "risk": risk,
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
        ).where(Risk.risk_type == "high").order_by(
            Article.created_at.desc()
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def get_posts_count(self) -> int:
        """Получить общее количество постов."""
        result = await self.session.execute(select(func.count(Article.id)))
        return result.scalar() or 0