from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis
from redis.exceptions import WatchError

from app.config import settings

_ADD_RELATION_MAX_ATTEMPTS = 32


class RedisGraphStorage:
    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        kw: dict[str, Any] = {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "decode_responses": True,
        }
        if settings.redis_password:
            kw["password"] = settings.redis_password
        self._client = redis.Redis(**kw)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def ping(self) -> bool:
        client = self._require_client()
        return bool(await client.ping())

    def _require_client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not connected")
        return self._client

    @staticmethod
    def _pair_key(entity_id_1: int, entity_id_2: int) -> tuple[int, int]:
        if entity_id_1 < entity_id_2:
            return entity_id_1, entity_id_2
        return entity_id_2, entity_id_1

    @staticmethod
    def _relation_redis_key(e1: int, e2: int) -> str:
        return f"relation:{e1}:{e2}"

    async def add_relation(
        self,
        entity_id_1: int,
        entity_id_2: int,
        entity_name_1: str,
        entity_name_2: str,
        article_id: int,
    ) -> None:
        if entity_id_1 == entity_id_2:
            return
        e1, e2 = self._pair_key(entity_id_1, entity_id_2)
        relation_key = self._relation_redis_key(e1, e2)

        name_for_e1 = entity_name_1 if e1 == entity_id_1 else entity_name_2
        name_for_e2 = entity_name_2 if e2 == entity_id_2 else entity_name_1

        client = self._require_client()
        sadd_e1 = f"entity_relations:{e1}"
        sadd_e2 = f"entity_relations:{e2}"

        for _ in range(_ADD_RELATION_MAX_ATTEMPTS):
            try:
                async with client.pipeline(transaction=True) as pipe:
                    await pipe.watch(relation_key)
                    raw = await pipe.get(relation_key)
                    if raw:
                        data_prev = json.loads(raw)
                        article_ids = data_prev.get("article_ids", [])
                        if not isinstance(article_ids, list):
                            article_ids = []
                        if article_id in article_ids:
                            return
                        article_ids = [*article_ids, article_id]
                        payload = {
                            "entity_id_1": e1,
                            "entity_id_2": e2,
                            "entity_name_1": name_for_e1,
                            "entity_name_2": name_for_e2,
                            "weight": len(article_ids),
                            "article_ids": article_ids,
                        }
                    else:
                        payload = {
                            "entity_id_1": e1,
                            "entity_id_2": e2,
                            "entity_name_1": name_for_e1,
                            "entity_name_2": name_for_e2,
                            "weight": 1,
                            "article_ids": [article_id],
                        }
                    encoded = json.dumps(payload)
                    pipe.multi()
                    pipe.set(relation_key, encoded)
                    pipe.sadd(sadd_e1, relation_key)
                    pipe.sadd(sadd_e2, relation_key)
                    await pipe.execute()
                return
            except WatchError:
                continue
        msg = f"add_relation: too many concurrent updates for {relation_key}"
        raise RuntimeError(msg)

    async def get_entity_relations(self, entity_id: int) -> list[dict[str, Any]]:
        client = self._require_client()
        relation_keys = await client.smembers(f"entity_relations:{entity_id}")
        relations: list[dict[str, Any]] = []
        for key in relation_keys:
            raw = await client.get(key)
            if not raw:
                continue
            data = json.loads(raw)
            weight = int(data.get("weight", 0))
            if weight < settings.min_weight_threshold:
                continue
            id1 = data.get("entity_id_1")
            id2 = data.get("entity_id_2")
            if id1 is None or id2 is None:
                continue
            if id1 == entity_id:
                other_id = id2
                other_name = data.get("entity_name_2")
            elif id2 == entity_id:
                other_id = id1
                other_name = data.get("entity_name_1")
            else:
                continue
            if other_name is None:
                continue
            article_ids = data.get("article_ids", [])
            if not isinstance(article_ids, list):
                article_ids = []
            relations.append(
                {
                    "entity_id": other_id,
                    "entity_name": other_name,
                    "weight": weight,
                    "co_articles": len(article_ids),
                }
            )
        relations.sort(key=lambda x: x["weight"], reverse=True)
        return relations

    async def get_related_entities(self, entity_id: int, limit: int = 10) -> list[dict[str, Any]]:
        return (await self.get_entity_relations(entity_id))[:limit]

    async def store_entity_metadata(self, entity_id: int, name: str, entity_type: str) -> None:
        client = self._require_client()
        pipe = client.pipeline()
        pipe.set(f"entity:{entity_id}:name", name)
        pipe.set(f"entity:{entity_id}:type", entity_type)
        pipe.sadd(f"entities:by_type:{entity_type}", str(entity_id))
        await pipe.execute()

    async def get_entity_name_type(self, entity_id: int) -> tuple[str | None, str | None]:
        client = self._require_client()
        pipe = client.pipeline()
        pipe.get(f"entity:{entity_id}:name")
        pipe.get(f"entity:{entity_id}:type")
        name_raw, type_raw = await pipe.execute()
        return name_raw, type_raw
