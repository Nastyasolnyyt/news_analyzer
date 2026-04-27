"""Local verification with fakeredis (no Docker). Run: pip install fakeredis && python scripts/verify_cooccurrence.py"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import fakeredis.aioredis as fakeredis

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.graph_builder import KnowledgeGraphBuilder  # noqa: E402
from app.redis_storage import RedisGraphStorage  # noqa: E402


async def main() -> None:
    storage = RedisGraphStorage()
    storage._client = fakeredis.FakeRedis(decode_responses=True)

    builder = KnowledgeGraphBuilder()
    entities = [
        {"id": 1, "text": "Газпром", "type": "ORG"},
        {"id": 2, "text": "Миллер", "type": "PERSON"},
        {"id": 3, "text": "Путин", "type": "PERSON"},
    ]
    await builder.process_article_entities(storage, 100, entities)
    await builder.process_article_entities(
        storage,
        101,
        [
            {"id": 1, "text": "Газпром", "type": "ORG"},
            {"id": 2, "text": "Миллер", "type": "PERSON"},
        ],
    )
    await builder.process_article_entities(storage, 100, entities)

    rels = await storage.get_entity_relations(1)
    miller = next(r for r in rels if r["entity_id"] == 2)
    putin = next(r for r in rels if r["entity_id"] == 3)
    assert miller["weight"] == 2, miller
    assert putin["weight"] == 1, putin
    assert rels[0]["weight"] >= rels[1]["weight"]
    print("verify_cooccurrence: OK", rels)


if __name__ == "__main__":
    asyncio.run(main())
