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

    async def get_all_entities(self, limit: int = 100, page: int = 1, entity_type: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить список всех сущностей с их статистикой упоминаний и поддержкой пагинации.
        Возвращает объект с полями: items, total, limit, page, total_pages.
        
        Параметры:
        - limit: максимальное количество сущностей на странице (по умолчанию 100)
        - page: номер страницы (по умолчанию 1)
        - entity_type: фильтр по типу сущности
        - search: поиск по названию
        """
        from sqlalchemy import select, func
        from src.infrastructure.postgres.models.named_entity import NamedEntity
        
        # Сначала получаем общее количество сущностей
        count_query = select(func.count(NamedEntity.id))
        if entity_type:
            count_query = count_query.where(NamedEntity.entity_type == entity_type)
        if search:
            count_query = count_query.where(NamedEntity.name.ilike(f"%{search}%"))
        
        total_result = await self.ner_gateway.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Вычисляем offset
        offset = (page - 1) * limit
        total_pages = (total + limit - 1) // limit  # Округляем вверх
        
        # Получаем сущности для текущей страницы
        query = select(NamedEntity)
        if entity_type:
            query = query.where(NamedEntity.entity_type == entity_type)
        if search:
            query = query.where(NamedEntity.name.ilike(f"%{search}%"))
        query = query.order_by(NamedEntity.created_at.desc()).offset(offset).limit(limit)
        result = await self.ner_gateway.session.execute(query)
        entities = result.scalars().all()
        
        if not entities:
            return {
                "items": [],
                "total": total,
                "limit": limit,
                "page": page,
                "total_pages": total_pages,
            }
        
        # Для каждой сущности считаем статистику
        result_list = []
        for entity in entities:
            # Получаем посты где упоминается сущность
            posts_entity = await self.post_entity_gateway.get_posts_by_ner(entity.id)
            
            # Считаем упоминания за последнюю неделю и предыдущую
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            recent_mentions = 0
            previous_mentions = 0
            
            for pe in posts_entity:
                try:
                    post = await self.post_gateway.get_post_by_id(pe.post_id)
                    if post and post.created_at:
                        if post.created_at >= week_ago:
                            recent_mentions += 1
                        elif post.created_at >= two_weeks_ago:
                            previous_mentions += 1
                except:
                    continue
            
            # Считаем количество уникальных тем
            topic_ids = set()
            for pe in posts_entity:
                try:
                    post = await self.post_gateway.get_post_by_id(pe.post_id)
                    if post and post.analyses:
                        for analysis in post.analyses:
                            if analysis.topic_id:
                                topic_ids.add(analysis.topic_id)
                except:
                    continue
            
            result_list.append({
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type,
                "description": f"{entity.name} — {entity.entity_type}",
                "recentMentions": recent_mentions,
                "previousMentions": previous_mentions,
                "topicCount": len(topic_ids),
            })
        
        return {
            "items": result_list,
            "total": total,
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
        }

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

        # Считаем статистику упоминаний по дням за последнюю неделю
        mentions_stats = self._calculate_mentions_stats(posts, period="week")

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

    async def get_top_entities_24h(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получить топ сущностей за 24 часа по росту интереса.
        Сравнивает количество упоминаний за последние 24 часа с предыдущими 24 часами.
        Возвращает сущности с percent_change и направлением тренда.
        """
        from sqlalchemy import select, func
        from src.infrastructure.postgres.models.named_entity import NamedEntity
        from src.infrastructure.postgres.models.post_entity import PostEntity
        from src.infrastructure.postgres.models.post import Article
        
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        previous_24h = now - timedelta(hours=48)
        
        # Получаем все сущности
        query = select(NamedEntity).order_by(NamedEntity.created_at.desc())
        result = await self.ner_gateway.session.execute(query)
        entities = result.scalars().all()
        
        if not entities:
            return []
        
        result_list = []
        for entity in entities:
            # Получаем посты где упоминается сущность
            posts_entity = await self.post_entity_gateway.get_posts_by_ner(entity.id)
            
            recent_mentions = 0
            previous_mentions = 0
            
            for pe in posts_entity:
                try:
                    post = await self.post_gateway.get_post_by_id(pe.post_id)
                    if post and post.created_at:
                        if post.created_at >= last_24h:
                            recent_mentions += 1
                        elif post.created_at >= previous_24h:
                            previous_mentions += 1
                except:
                    continue
            
            # Вычисляем процент изменения
            if previous_mentions > 0:
                change_percent = round(((recent_mentions - previous_mentions) / previous_mentions) * 100)
            elif recent_mentions > 0:
                # Если раньше не упоминалась, а теперь упоминается - большой рост
                change_percent = recent_mentions * 100
            else:
                change_percent = 0
            
            # Определяем направление тренда
            if change_percent > 0:
                direction = 'up'
            elif change_percent < 0:
                direction = 'down'
            else:
                direction = 'flat'
            
            # Пропускаем сущности без упоминаний за последние 48 часов
            if recent_mentions == 0 and previous_mentions == 0:
                continue
            
            result_list.append({
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type,
                "change_percent": abs(change_percent),
                "direction": direction,
                "recent_mentions": recent_mentions,
                "previous_mentions": previous_mentions,
            })
        
        # Сортируем по абсолютному значению изменения и берем топ
        result_list.sort(key=lambda x: (-x['change_percent'] if x['direction'] == 'up' else x['change_percent'], -x['recent_mentions']))
        
        return result_list[:limit]

    def _calculate_mentions_stats(self, posts: List[Any], period: str = "week") -> List[EntityMentionStats]:
        """
        Рассчитывает статистику упоминаний.
        period: 'week' - по дням за неделю, 'month' - по неделям за 2 месяца
        """
        if not posts:
            # Возвращаем пустую структуру, если постов нет
            if period == "week":
                return [
                    EntityMentionStats(week=datetime.now().strftime("%d.%m"), count=0, note=None)
                    for _ in range(7)
                ]
            return []

        now = datetime.now()
        stats = []
        
        if period == "week":
            # Группируем по дням за последнюю неделю
            day_counts: Dict[str, int] = defaultdict(int)
            for post in posts:
                if post.created_at:
                    day_key = post.created_at.strftime("%d.%m")
                    day_counts[day_key] += 1
            
            # Генерируем данные за последние 7 дней
            for i in range(6, -1, -1):
                day_date = now - timedelta(days=i)
                day_key = day_date.strftime("%d.%m")
                count = day_counts.get(day_key, 0)
                
                # Добавляем заметки для демонстрации (можно убрать)
                note = None
                if count > 5:
                    note = "Пик упоминаний"
                
                stats.append(EntityMentionStats(
                    week=day_key,  # Используем поле week для даты
                    count=count,
                    note=note,
                ))
        else:
            # Группируем по неделям (старая логика)
            week_counts: Dict[str, int] = defaultdict(int)
            for post in posts:
                if post.created_at:
                    week_start = post.created_at - timedelta(days=post.created_at.weekday())
                    week_key = week_start.strftime("%d.%m")
                    week_counts[week_key] += 1

            current_week_start = now - timedelta(days=now.weekday())
            
            for i in range(7, -1, -1):
                week_start = current_week_start - timedelta(weeks=i)
                week_key = week_start.strftime("%d.%m")
                count = week_counts.get(week_key, 0)
                
                notes_map = {
                    "28.10": "Запрос регулятора",
                    "18.11": "Инцидент в цепочке поставок",
                }
                
                stats.append(EntityMentionStats(
                    week=week_key,
                    count=count,
                    note=notes_map.get(week_key),
                ))

        return stats

    async def create_entity(self, name: str, entity_type: str) -> NamedEntityDTO:
        """
        Создает новую сущность, которую пользователь хочет отслеживать.
        Возвращает созданную сущность с её ID.
        """
        # Валидация типа сущности
        valid_types = ["ORG", "PER", "LOC", "Organization", "Person", "Location"]
        if entity_type not in valid_types:
            # Если приходит неизвестный тип, используем ORG по умолчанию
            entity_type = "ORG"
        
        # Создаем сущность через репозиторий
        created_entity = await self.ner_gateway.create_named_entity(name, entity_type)
        return created_entity