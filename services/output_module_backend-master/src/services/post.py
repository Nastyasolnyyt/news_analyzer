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
        post = await self.post_gateway.get_post(post_id)
        analysis = await self.post_analysis_gateway.get_post_analysis(post_id)
        topic = None
        if analysis.topic_id:
            topic = await self.topic_gateway.get_topic(analysis.topic_id)
        analysis_with_external = PostAnalysisWithExternalModelsDTO(
            topic=topic,
            id=analysis.id,
            post_id=analysis.post_id,
            emotion=analysis.emotion,
            tonality=analysis.tonality,
            relevance=analysis.relevance,
        )
        post_entities = await self.post_entity_gateway.get_ners_by_post(post_id)
        entities = [
            await self.ner_gateway.get_named_entity(entity.entity_id) for entity in post_entities
        ]
        post_with_external_models_dto = PostWithExternalModelsDTO(
            post=post, analysis=analysis_with_external, entities=entities
        )
        return post_with_external_models_dto

    async def get_posts(self, filters: PostFilterDTO) -> PostListResponseDTO:
        """Получает список постов с фильтрацией, сортировкой и пагинацией."""
        posts, total = await self.post_gateway.get_posts_with_filters(filters)

        # Для каждого поста получаем полную информацию (analysis, entities)
        posts_with_external = []
        for post in posts:
            try:
                analysis = await self.post_analysis_gateway.get_post_analysis(post.id)
                topic = None
                if analysis.topic_id:
                    topic = await self.topic_gateway.get_topic(analysis.topic_id)
                analysis_with_external = PostAnalysisWithExternalModelsDTO(
                    topic=topic,
                    id=analysis.id,
                    post_id=analysis.post_id,
                    emotion=analysis.emotion,
                    tonality=analysis.tonality,
                    relevance=analysis.relevance,
                )
                post_entities = await self.post_entity_gateway.get_ners_by_post(post.id)
                entities = [
                    await self.ner_gateway.get_named_entity(entity.entity_id)
                    for entity in post_entities
                ]
                post_with_external_models_dto = PostWithExternalModelsDTO(
                    post=post, analysis=analysis_with_external, entities=entities
                )
                posts_with_external.append(post_with_external_models_dto)
            except Exception:
                # Если нет analysis для поста, пропускаем его
                continue

        return PostListResponseDTO(
            items=posts_with_external,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
