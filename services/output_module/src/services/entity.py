from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from src.application.schemas.named_entity import (
    EntityInfo, 
    EntityMentionsFilterDTO, 
    EntityDetailsResponse,
    EntityRelatedItem,
    EntityMentionStats,
    NamedEntityDTO,
)
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay


class EntityService:
    def __init__(
        self,
        ner_gateway: NamedEntityDBGateWay,
        post_entity_gateway: PostEntityDBGateWay,
        post_gateway: PostDBGateWay,
    ):
        # ИСПРАВЛЕНО: Убрали лишнюю упаковку в кортеж
        self.ner_gateway = ner_gateway
        self.post_entity_gateway = post_entity_gateway
        self.post_gateway = post_gateway

    async def get_entity_mentions(
        self, entity_id: int, filters: Optional[EntityMentionsFilterDTO] = None
    ) -> List[EntityInfo]:
        """Получает упоминания сущности с фильтрацией по датам."""
        entity = await self.ner_gateway.get_named_entity(entity_id)
        
        # Защита: если сущность не найдена в БД
        if not entity:
            return []

        posts_entity = await self.post_entity_gateway.get_posts_by_ner(entity.id)
        
        # ИСПРАВЛЕНО: Заменили get_post на get_post_by_id и добавили проверку на существование поста
        posts = []
        for post_entity in posts_entity:
            try:
                post = await self.post_gateway.get_post_by_id(post_entity.post_id)
                if post:
                    posts.append(post)
            except Exception:
                continue

        # Применяем фильтрацию по датам
        if filters:
            if filters.start is not None:
                posts = [post for post in posts if post.created_at >= filters.start]
            if filters.end is not None:
                posts = [post for post in posts if post.created_at <= filters.end]

        return [
            EntityInfo(entity=entity, post_id=post.id, mentioned_at=post.created_at)
            for post in posts
        ]

    async def get_entity_info(self, entity_id: int) -> List[EntityInfo]:
        """Старый метод для обратной совместимости."""
        return await self.get_entity_mentions(entity_id, filters=None)

    async def get_entity_details(self, entity_id: int) -> EntityDetailsResponse:
        """
        Получает полную информацию о сущности для отображения в профиле.
        Включает основные данные, связанные сущности, статистику упоминаний и новости.
        """
        # Получаем основную сущность
        entity = await self.ner_gateway.get_named_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity with id {entity_id} not found")

        # Получаем все посты, где упоминается сущность
        posts_entity = await self.post_entity_gateway.get_posts_by_ner(entity.id)
        
        posts = []
        for post_entity in posts_entity:
            try:
                post = await self.post_gateway.get_post_by_id(post_entity.post_id)
                if post:
                    posts.append(post)
            except Exception:
                continue

        # Собираем связанные сущности из тех же постов
        related_entities_map: Dict[int, Dict[str, Any]] = {}
        for post in posts:
            for post_ent in post.entities or []:
                if post_ent.entity_id != entity.id:
                    try:
                        related_entity = await self.ner_gateway.get_named_entity(post_ent.entity_id)
                        if related_entity.id not in related_entities_map:
                            # Определяем роль на основе типа связи
                            role = self._determine_entity_role(related_entity.entity_type, entity.entity_type)
                            related_entities_map[related_entity.id] = {
                                "id": related_entity.id,
                                "name": related_entity.name,
                                "role": role,
                                "entity_type": related_entity.entity_type,
                            }
                    except Exception:
                        continue

        related_entities = [
            EntityRelatedItem(**data) 
            for data in related_entities_map.values()
        ][:10]  # Ограничиваем до 10 связанных сущностей

        # Считаем статистику упоминаний по неделям (за последние 8 недель)
        mentions_stats = self._calculate_mentions_stats(posts)

        # Формируем список последних новостей
        recent_news = []
        sorted_posts = sorted(posts, key=lambda p: p.created_at, reverse=True)[:5]
        for post in sorted_posts:
            analysis = post.analyses[0] if post.analyses else None
            risk = post.risks[0] if post.risks else None
            recent_news.append({
                "id": post.id,
                "title": post.title,
                "date": post.created_at.isoformat() if post.created_at else None,
                "source": post.source,
                "summary": (post.text[:150] + "...") if len(post.text) > 150 else post.text,
                "risk_level": risk.risk_level if risk else None,
            })

        # Формируем идентификаторы (заглушка, можно расширить)
        identifiers = {}
        if entity.entity_type.lower() in ["company", "organization", "организация"]:
            identifiers = {
                "type": "Организация",
                "jurisdiction": "Российская Федерация",
            }

        return EntityDetailsResponse(
            id=entity.id,
            name=entity.name,
            entity_type=entity.entity_type,
            jurisdiction=identifiers.get("jurisdiction"),
            description=f"{entity.name} — {entity.entity_type}",
            related_entities=related_entities,
            mentions_stats=mentions_stats,
            recent_news=recent_news,
            total_mentions=len(posts),
            identifiers=identifiers,
        )

    def _determine_entity_role(self, related_type: str, main_type: str) -> str:
        """Определяет роль связанной сущности"""
        related_lower = related_type.lower()
        main_lower = main_type.lower()
        
        if related_lower in ["person", "persona", "персона", "человек"]:
            return "Ключевая персона"
        elif related_lower in ["company", "organization", "организация"]:
            return "Партнёрская организация"
        elif related_lower in ["location", "локация", "место"]:
            return "Связанная локация"
        else:
            return "Связанная сущность"

    def _calculate_mentions_stats(self, posts: List[Any]) -> List[EntityMentionStats]:
        """
        Рассчитывает статистику упоминаний по неделям.
        Возвращает данные за последние 8 недель.
        """
        if not posts:
            return []

        # Группируем посты по неделям
        week_counts: Dict[str, int] = defaultdict(int)
        
        for post in posts:
            if post.created_at:
                # Получаем начало недели (понедельник)
                week_start = post.created_at - timedelta(days=post.created_at.weekday())
                week_key = week_start.strftime("%d.%m")
                week_counts[week_key] += 1

        # Формируем список за последние 8 недель
        now = datetime.now()
        current_week_start = now - timedelta(days=now.weekday())
        
        stats = []
        notes_map = {
            "28.10": "Запрос регулятора",
            "18.11": "Инцидент в цепочке поставок",
        }
        
        for i in range(7, -1, -1):
            week_start = current_week_start - timedelta(weeks=i)
            week_key = week_start.strftime("%d.%m")
            count = week_counts.get(week_key, 0)
            
            stats.append(EntityMentionStats(
                week=week_key,
                count=count,
                note=notes_map.get(week_key),
            ))

        return stats