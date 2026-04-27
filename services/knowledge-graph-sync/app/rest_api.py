from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.redis_storage import RedisGraphStorage

router = APIRouter()


def get_storage(request: Request) -> RedisGraphStorage:
    return request.app.state.storage


@router.get("/health")
async def health_check(storage: RedisGraphStorage = Depends(get_storage)) -> dict[str, str]:
    try:
        await storage.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="redis unavailable") from exc
    return {"status": "ok"}


@router.get("/entities/{entity_id}/relations")
async def get_entity_relations(
    entity_id: int,
    limit: int = 10,
    storage: RedisGraphStorage = Depends(get_storage),
) -> dict[str, Any]:
    try:
        relations = await storage.get_related_entities(entity_id, limit)
        if not relations:
            raise HTTPException(
                status_code=404,
                detail=f"Entity {entity_id} has no relations in the graph",
            )
        return {
            "entity_id": entity_id,
            "relations": relations,
            "total": len(relations),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/graph/entities/{entity_id}/subgraph")
async def get_entity_subgraph(
    entity_id: int,
    depth: int = 1,
    storage: RedisGraphStorage = Depends(get_storage),
) -> dict[str, Any]:
    if depth < 1:
        depth = 1
    if depth > 2:
        depth = 2

    direct_relations = await storage.get_entity_relations(entity_id)
    center_name, center_type = await storage.get_entity_name_type(entity_id)
    nodes: list[dict[str, Any]] = [
        {
            "id": entity_id,
            "label": center_name or "?",
            "type": center_type or "?",
        }
    ]
    edges: list[dict[str, Any]] = []
    seen = {entity_id}

    for r in direct_relations:
        oid = int(r["entity_id"])
        if oid not in seen:
            seen.add(oid)
            _, otype = await storage.get_entity_name_type(oid)
            nodes.append(
                {
                    "id": oid,
                    "label": r["entity_name"],
                    "type": otype or "?",
                }
            )
        edges.append(
            {
                "source": entity_id,
                "target": oid,
                "weight": r["weight"],
            }
        )

    if depth >= 2:
        for r in direct_relations[:20]:
            oid = int(r["entity_id"])
            second = await storage.get_entity_relations(oid)
            for s in second:
                tid = int(s["entity_id"])
                if tid == entity_id:
                    continue
                if tid not in seen:
                    seen.add(tid)
                    _, ttype = await storage.get_entity_name_type(tid)
                    nodes.append(
                        {
                            "id": tid,
                            "label": s["entity_name"],
                            "type": ttype or "?",
                        }
                    )
                edges.append(
                    {
                        "source": oid,
                        "target": tid,
                        "weight": s["weight"],
                    }
                )

    deduped: dict[tuple[int, int], int] = {}
    for e in edges:
        s, t, w = int(e["source"]), int(e["target"]), int(e["weight"])
        k = (s, t)
        prev = deduped.get(k)
        if prev is None or w > prev:
            deduped[k] = w
    edges_out = [
        {"source": s, "target": t, "weight": w}
        for (s, t), w in sorted(deduped.items(), key=lambda item: item[0])
    ]

    return {
        "center_entity": entity_id,
        "depth": depth,
        "nodes": nodes,
        "edges": edges_out,
    }


@router.get("/search/entities")
async def search_entities(q: str) -> list[dict[str, Any]]:  # noqa: ARG001
    return []
