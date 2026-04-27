from __future__ import annotations

import logging
from itertools import combinations
from typing import Any, cast

from app.config import settings
from app.redis_storage import RedisGraphStorage

logger = logging.getLogger(__name__)


def _dedupe_entities(entities: list[Any]) -> list[dict[str, Any]]:
    by_id: dict[int, dict[str, Any]] = {}
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        eid = entity.get("id")
        if eid is None:
            continue
        if not isinstance(eid, int):
            try:
                eid = int(eid)
            except (TypeError, ValueError):
                logger.debug("Skip entity without int id: %s", entity)
                continue
        by_id[eid] = entity
    return list(by_id.values())


class KnowledgeGraphBuilder:
    @staticmethod
    async def process_article_entities(
        storage: RedisGraphStorage,
        article_id: int,
        entities: Any,
    ) -> None:
        if not isinstance(entities, list):
            logger.debug("Article %s: entities is not a list, skip", article_id)
            return

        entity_list = cast(list[Any], entities)
        if len(entity_list) < 2:
            logger.debug("Article %s: fewer than 2 entities, skip", article_id)
            return

        unique_entities = _dedupe_entities(entity_list)
        if settings.max_entities_per_article > 0:
            unique_entities = unique_entities[: settings.max_entities_per_article]
        if len(unique_entities) < 2:
            logger.debug("Article %s: fewer than 2 entities after dedupe/trim, skip", article_id)
            return

        logger.info("Article %s: processing %s entities", article_id, len(unique_entities))

        for entity in unique_entities:
            await storage.store_entity_metadata(
                entity_id=int(entity["id"]),
                name=str(entity.get("text", entity.get("name", ""))),
                entity_type=str(entity.get("type", "UNKNOWN")),
            )

        for entity_1, entity_2 in combinations(unique_entities, 2):
            eid1 = int(entity_1["id"])
            eid2 = int(entity_2["id"])
            name1 = str(entity_1.get("text", entity_1.get("name", "")))
            name2 = str(entity_2.get("text", entity_2.get("name", "")))
            await storage.add_relation(
                entity_id_1=eid1,
                entity_id_2=eid2,
                entity_name_1=name1,
                entity_name_2=name2,
                article_id=article_id,
            )
            logger.debug("Edge: %s <-> %s", name1, name2)
