from dishka import Provider, Scope, provide
from src.infrastructure.postgres.repositories.named_entity import NamedEntityDBGateWay
from src.infrastructure.postgres.repositories.post import PostDBGateWay
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.post_analysis import PostAnalysisDBGateWay
from src.infrastructure.postgres.repositories.post_entity import PostEntityDBGateWay
from src.infrastructure.postgres.repositories.topic import TopicDBGateWay
from src.infrastructure.postgres.repositories.user import UserDBGateWay
from src.services.auth import AuthService
from src.services.entity import EntityService
from src.services.notification import NotificationService
from src.services.post import PostService
from src.services.user_service import UserService



class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def notification_service(self, session: AsyncSession) -> NotificationService:
        return NotificationService(session)

    @provide(scope=Scope.REQUEST)
    def post_service(
        self,
        post_gateway: PostDBGateWay,
        ner_gateway: NamedEntityDBGateWay,
        post_analysis_gateway: PostAnalysisDBGateWay,
        topic_gateway: TopicDBGateWay,
        post_entity_gateway: PostEntityDBGateWay,
    ) -> PostService:
        return PostService(
            post_gateway, ner_gateway, post_analysis_gateway, topic_gateway, post_entity_gateway
        )

    @provide(scope=Scope.REQUEST)
    def entity_service(
        self,
        ner_gateway: NamedEntityDBGateWay,
        post_entity_gateway: PostEntityDBGateWay,
        post_gateway: PostDBGateWay,
    ) -> EntityService:
        return EntityService(ner_gateway, post_entity_gateway, post_gateway)

    @provide(scope=Scope.REQUEST)
    def auth_service(self, user_gateway: UserDBGateWay) -> AuthService:
        return AuthService(user_gateway)

    @provide(scope=Scope.REQUEST)
    def user_service(self, user_gateway: UserDBGateWay, auth_service: AuthService) -> UserService:
        return UserService(user_gateway, auth_service)
