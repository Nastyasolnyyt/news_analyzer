from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NamedEntityDTO(BaseModel):
    id: int
    name: str
    entity_type: str
    created_at: datetime


class EntityInfo(BaseModel):
    entity: NamedEntityDTO
    post_id: int
    mentioned_at: datetime


class EntityMentionsFilterDTO(BaseModel):
    start: Optional[datetime] = Field(
        None, description="Начальная дата фильтрации (created_at поста)"
    )
    end: Optional[datetime] = Field(None, description="Конечная дата фильтрации (created_at поста)")


class EntityRelatedItem(BaseModel):
    """Элемент связанной сущности"""
    id: int
    name: str
    role: str
    entity_type: str


class EntityMentionStats(BaseModel):
    """Статистика упоминаний за период"""
    week: str
    count: int
    note: Optional[str] = None


class EntityDetailsResponse(BaseModel):
    """Полный ответ с информацией о сущности"""
    id: int
    name: str
    entity_type: str
    jurisdiction: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    founded: Optional[str] = None
    registry: Optional[str] = None
    identifiers: dict = Field(default_factory=dict)
    related_entities: List[EntityRelatedItem] = Field(default_factory=list)
    mentions_stats: List[EntityMentionStats] = Field(default_factory=list)
    recent_news: List[dict] = Field(default_factory=list)
    total_mentions: int = 0
