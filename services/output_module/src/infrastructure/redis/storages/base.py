import json
from typing import Any, Optional, cast

from loguru import logger
from redis import RedisError
from redis.asyncio import Redis


class BaseStorage:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        try:
            serialized = json.dumps(
                (
                    value.model_dump()
                    if hasattr(value, "model_dump")
                    else (
                        [item.model_dump() for item in value]
                        if isinstance(value, list)
                        and hasattr(next(iter(value), None), "model_dump")
                        else value
                    )
                ),
                default=str,
            )
            await self.redis.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, *keys: str) -> int:
        try:
            result = await self.redis.delete(*keys)
            return cast(int, result)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def scan_keys(self, pattern: str, count: int = 100) -> list[str]:
        try:
            cursor = 0
            all_keys: list[str] = []

            while True:
                scan_result = await self.redis.scan(cursor=cursor, match=pattern, count=count)
                new_cursor, keys = scan_result
                keys = [str(k) for k in keys] if keys else []
                all_keys.extend(keys)
                if new_cursor == 0:
                    break
                cursor = new_cursor

            return all_keys
        except RedisError as e:
            logger.error(f"Redis SCAN error for pattern '{pattern}', {e}")
            return []
