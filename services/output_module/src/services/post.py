from src.application.schemas.post import (
    PostFilterDTO,
    PostListResponseDTO,
    PostWithExternalModelsDTO,
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
            emotion=analysis.emotion if analysis else 0.0,
            tonality=analysis.tonality if analysis else 0.0,
            relevance=analysis.relevance if analysis else 0.0,
           
        )

        post_entities = await self.post_entity_gateway.get_ners_by_post(post_id)
        entities = [
            await self.ner_gateway.get_named_entity(e.entity_id)
            for e in post_entities
        ]

        return PostWithExternalModelsDTO(
            post=post, analysis=analysis_with_external, entities=entities
        )

    async def get_posts(self, filters: PostFilterDTO) -> PostListResponseDTO:
        # Репозиторий возвращает список словарей/Row, так как там есть join или несколько сущностей
        items, total = await self.post_gateway.get_posts_with_filters(filters)
        
        posts_with_external = []
        for item in items:
            try:
                # 1. Извлекаем сам объект SQLAlchemy из словаря
                # Если в репозитории select(Article, ...), то ключ будет 'Article' или 'post'
                # Судя по твоему коду, ключ называется 'post'
                post_obj = item['post'] 
                
                # 2. Получаем анализ из связей объекта
                analysis = post_obj.analyses[0] if post_obj.analyses else None
                
                topic = None
                if analysis and analysis.topic_id:
                    topic = await self.topic_gateway.get_topic(analysis.topic_id)

                # 3. Создаем DTO анализа
                # Везде используем post_obj (объект), а не item (словарь)
                analysis_dto = PostAnalysisWithExternalModelsDTO(
                    topic=topic,
                    id=analysis.id if analysis else None,
                    post_id=post_obj.id,  # ИСПРАВЛЕНО: было post.id
                    emotion=analysis.emotion if analysis else 0.0,
                    tonality=analysis.tonality if analysis else 0.0,
                    relevance=analysis.relevance if analysis else 0.0,
                )

                # 4. Сущности (Entities)
                # ИСПРАВЛЕНО: берем из объекта post_obj, а не из словаря item
                entities = post_obj.entities if post_obj.entities else []

                # 5. Собираем итоговый DTO
                posts_with_external.append(
                    PostWithExternalModelsDTO(
                        post=post_obj,  # ИСПРАВЛЕНО: передаем объект для маппинга в PostBaseDTO
                        analysis=analysis_dto, 
                        entities=entities
                    )
                )
            except Exception as e:
                # Теперь здесь будет печататься правильный ID, так как мы берем его из объекта
                print(f"Error processing post {item['post'].id if 'post' in item else 'unknown'}: {e}")
                continue

        return PostListResponseDTO(
            items=posts_with_external,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
