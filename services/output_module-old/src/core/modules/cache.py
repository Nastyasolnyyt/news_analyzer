from dishka import Provider, Scope, provide
from redis.asyncio.client import Redis
from src.infrastructure.redis.connection import async_redis_client
from src.infrastructure.redis.storages.base import BaseStorage


class CacheProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_connection(self) -> Redis:
        return async_redis_client

    @provide(scope=Scope.REQUEST)
    def get_base_storage(self, redis: Redis) -> BaseStorage:
        return BaseStorage(redis)
