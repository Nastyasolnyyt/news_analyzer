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
        # 1. Получаем данные из гейтвея
        result = await self.post_gateway.get_post_by_id(post_id)
        
        if not result:
            return None # Или выброси 404 Exception

        # 2. ИЗВЛЕКАЕМ ОБЪЕКТ (если гейтвей вернул словарь/Row)
        # Если в гейтвее просто Article, то post_obj = result
        # Но судя по твоей ошибке, там словарь:
        post_obj = result['post'] if isinstance(result, dict) or not hasattr(result, 'id') else result

        # 3. Получаем единый анализ
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

        # 4. Сущности
        post_entities = await self.post_entity_gateway.get_ners_by_post(post_id)
        entities = [
            await self.ner_gateway.get_named_entity(e.entity_id)
            for e in post_entities
        ]

        # 5. Возвращаем DTO, передавая чистый объект post_obj
        return PostWithExternalModelsDTO(
            post=post_obj, # ТЕПЕРЬ ТУТ ОБЪЕКТ, А НЕ СЛОВАРЬ
            analysis=analysis_with_external, 
            entities=entities
        )