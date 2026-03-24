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
        posts, total = await self.post_gateway.get_posts_with_filters(filters)
        
        posts_with_external = []
        for post in posts:
            try:
                # Анализ уже загружен через joinedload в гейтвее
                analysis = post.analyses[0] if post.analyses else None
                
                topic = None
                if analysis and analysis.topic_id:
                    topic = await self.topic_gateway.get_topic(analysis.topic_id)

                analysis_dto = PostAnalysisWithExternalModelsDTO(
                    topic=topic,
                    id=analysis.id if analysis else None,
                    post_id=post.id,
                    emotion=analysis.emotion if analysis else 0.0,
                    tonality=analysis.tonality if analysis else 0.0,
                    relevance=analysis.relevance if analysis else 0.0,
                   
                )

                # Сущности уже загружены через selectinload
                entities = post.entities if post.entities else []

                posts_with_external.append(
                    PostWithExternalModelsDTO(post=post, analysis=analysis_dto, entities=entities)
                )
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")
                continue

        return PostListResponseDTO(
            items=posts_with_external,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
