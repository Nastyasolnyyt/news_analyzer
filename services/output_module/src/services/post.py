from src.application.schemas.post import (
    PostFilterDTO,
    PostListResponseDTO,
    PostWithExternalModelsDTO,
    EntityDTO,  # ДОБАВИЛ ИМПОРТ EntityDTO ДЛЯ ВАЛИДАЦИИ
    PostBaseDTO,  # ДОБАВИЛ ИМПОРТ PostBaseDTO
)
from src.application.schemas.post_analysis import PostAnalysisWithExternalModelsDTO
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from src.infrastructure.postgres.repositories.post_analysis import PostAnalysisDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay
from src.infrastructure.postgres.repositories.topic import TopicDBGateWay


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
        post = await self.post_gateway.get_post_by_id(post_id)
        # Получаем единый анализ (из таблицы articles_analysis)
        analysis = await self.post_analysis_gateway.get_post_analysis(post_id)
        
        topic = None
        if analysis and analysis.topic_id:
            topic = await self.topic_gateway.get_topic(analysis.topic_id)

        analysis_with_external = PostAnalysisWithExternalModelsDTO(
            topic=topic,
            id=analysis.id if analysis else None,
            post_id=post_id,
            emotion=analysis.emotion if analysis and analysis.emotion is not None else None,
            tonality=analysis.tonality if analysis and analysis.tonality is not None else None,
            relevance=analysis.relevance if analysis and analysis.relevance is not None else None,
        )

        post_entities = await self.post_entity_gateway.get_ners_by_post(post_id)
        
        # ИСПРАВЛЕНИЕ: Превращаем каждую сущность из БД в EntityDTO
        entities = []
        for e in post_entities:
            ner_obj = await self.ner_gateway.get_named_entity(e.entity_id)
            if ner_obj:
                entities.append(EntityDTO.model_validate(ner_obj))

        return PostWithExternalModelsDTO(
            post=PostBaseDTO.model_validate(post), 
            analysis=analysis_with_external, 
            entities=entities
        )

    async def get_posts(self, filters: PostFilterDTO) -> PostListResponseDTO:
        # Репозиторий возвращает список словарей/Row, так как там есть join или несколько сущностей
        items, total = await self.post_gateway.get_posts_with_filters(filters)
        
        posts_with_external = []
        for item in items:
            try:
                # 1. Извлекаем сам объект SQLAlchemy из словаря
                post_obj = item['post'] 
                
                # 2. Получаем анализ из связей объекта
                analysis = post_obj.analyses[0] if post_obj.analyses else None
                
                topic = None
                if analysis and analysis.topic_id:
                    topic = await self.topic_gateway.get_topic(analysis.topic_id)

                # 3. Создаем DTO анализа
                analysis_dto = PostAnalysisWithExternalModelsDTO(
                    topic=topic,
                    id=analysis.id if analysis else None,
                    post_id=post_obj.id,
                    emotion=analysis.emotion if analysis and analysis.emotion is not None else None,
                    tonality=analysis.tonality if analysis and analysis.tonality is not None else None,
                    relevance=analysis.relevance if analysis and analysis.relevance is not None else None,
                )

                # 4. Сущности (Entities)
                # ИСПРАВЛЕНИЕ: превращаем объекты БД в схемы EntityDTO, чтобы Pydantic не ругался
                db_entities = post_obj.entities if post_obj.entities else []
                entities = [EntityDTO.model_validate(e) for e in db_entities]

                # 5. Собираем итоговый DTO
                posts_with_external.append(
                    PostWithExternalModelsDTO(
                        post=PostBaseDTO.model_validate(post_obj),  # Явная валидация поста
                        analysis=analysis_dto, 
                        entities=entities
                    )
                )
            except Exception as e:
                print(f"Error processing post {item['post'].id if 'post' in item else 'unknown'}: {e}")
                continue

        return PostListResponseDTO(
            items=posts_with_external,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )