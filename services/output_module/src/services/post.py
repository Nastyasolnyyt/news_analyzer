from typing import List, Optional, Tuple
from sqlalchemy import or_, select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.post import (
    PostFilterDTO,
    PostListResponseDTO,
    PostWithExternalModelsDTO,
    PostBaseDTO,
)
from src.application.schemas.post_analysis import PostAnalysisWithExternalModelsDTO
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from src.infrastructure.postgres.repositories.post_analysis import PostAnalysisDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay
from src.infrastructure.postgres.repositories.topic import TopicDBGateWay
from src.infrastructure.postgres.models.post import Article
from src.infrastructure.postgres.models.risk import Risk


class PostService:
    def __init__(
        self,
        post_gateway: PostDBGateWay,
        ner_gateway: NamedEntityDBGateWay,
        post_analysis_gateway: PostAnalysisDBGateWay,
        topic_gateway: TopicDBGateWay,
        post_entity_gateway: PostEntityDBGateWay,
    ):
        self.post_gateway = post_gateway
        self.ner_gateway = ner_gateway
        self.post_analysis_gateway = post_analysis_gateway
        self.post_entity_gateway = post_entity_gateway
        self.topic_gateway = topic_gateway

    async def get_post(self, post_id: int) -> PostWithExternalModelsDTO:
        """Получить один пост с полной информацией."""
        post = await self.post_gateway.get_post_by_id(post_id)
        
        # Анализ
        try:
            analysis = await self.post_analysis_gateway.get_post_analysis(post_id)
            topic = None
            if analysis and analysis.topic_id:
                topic = await self.topic_gateway.get_topic(analysis.topic_id)
        except:
            analysis = None
            topic = None

        # Сущности
        post_entities = await self.post_entity_gateway.get_ners_by_post(post_id)
        entities = [
            await self.ner_gateway.get_named_entity(e.entity_id)
            for e in post_entities
        ]

        analysis_with_external = PostAnalysisWithExternalModelsDTO(
            topic=topic,
            id=analysis.id if analysis else None,
            post_id=post_id,
            emotion=analysis.emotion if analysis else 0.0,
            tonality=analysis.tonality if analysis else 0.0,
            relevance=analysis.relevance if analysis else 0.0,
            sentiment_label=analysis.sentiment_label if analysis else None,
        )

        return PostWithExternalModelsDTO(
            post=post, 
            analysis=analysis_with_external, 
            entities=entities
        )

    async def get_posts(self, filters: PostFilterDTO) -> PostListResponseDTO:
        """
        Получить список постов с risk_level и risk_type в ответе.
        КРИТИЧЕСКИ ВАЖНО: возвращаем ПЛОСКУЮ структуру для фронтенда!
        """
        # Используем репозиторий для основной фильтрации
        items, total = await self.post_gateway.get_posts_with_filters(filters)
        
        # Обогащаем каждый пост risk_level и risk_type из таблицы risks
        enriched_items = []
        for item_dict in items:
            post_obj = item_dict['post']
            analysis_obj = item_dict.get('analysis')
            risk_obj = item_dict.get('risk')
            entities = item_dict.get('entities', [])

            # Получаем тему если есть
            topic = None
            if analysis_obj and analysis_obj.topic_id:
                try:
                    topic = await self.topic_gateway.get_topic(analysis_obj.topic_id)
                except:
                    pass

            # Создаём DTO анализа
            analysis_dto = PostAnalysisWithExternalModelsDTO(
                topic=topic,
                id=analysis_obj.id if analysis_obj else None,
                post_id=post_obj.id,
                emotion=analysis_obj.emotion if analysis_obj else 0.0,
                tonality=analysis_obj.tonality if analysis_obj else 0.0,
                relevance=analysis_obj.relevance if analysis_obj else 0.0,
                sentiment_label=analysis_obj.sentiment_label if analysis_obj else None,
            )

            # ПЛОСКАЯ структура для фронтенда (БЕЗ вложенных объектов!)
            flattened = {
                # Основная информация о статье
                'id': post_obj.id,
                'title': post_obj.title,
                'text': post_obj.text,
                'source': post_obj.source,
                'link': post_obj.link,
                'pub_date': post_obj.pub_date.isoformat() if post_obj.pub_date else None,
                'created_at': post_obj.created_at.isoformat(),
                'updated_at': post_obj.updated_at.isoformat(),
                
                # Анализ тональности
                'sentiment_label': analysis_dto.sentiment_label or 'neutral',
                'tonality': float(analysis_dto.tonality) if analysis_dto.tonality else 0.0,
                'confidence': float(analysis_dto.confidence) if analysis_dto.confidence else 0.0,
                'emotion': float(analysis_dto.emotion) if analysis_dto.emotion else 0.0,
                'relevance': float(analysis_dto.relevance) if analysis_dto.relevance else 0.0,
                
                # РИСК (эти поля ищет фронтенд!)
                'risk_level': risk_obj.risk_level if risk_obj else 'low',  # 'high' | 'medium' | 'low'
                'risk_type': risk_obj.risk_type if risk_obj else None,    # 'политический' | 'экономический' | 'социальный'
                'risk_confidence': float(risk_obj.confidence) if risk_obj and risk_obj.confidence else 0.0,
                
                # Тема/кластер
                'topic_id': analysis_dto.topic.id if analysis_dto.topic else None,
                'topic_name': analysis_dto.topic.name if analysis_dto.topic else None,
                
                # Сущности
                'entities': [
                    {
                        'id': e.id,
                        'name': e.name,
                        'entity_type': e.entity_type,
                    }
                    for e in entities
                ],
            }

            enriched_items.append(flattened)

        return PostListResponseDTO(
            items=enriched_items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )