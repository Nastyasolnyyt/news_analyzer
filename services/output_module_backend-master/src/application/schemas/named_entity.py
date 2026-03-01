from datetime import datetime
from typing import Optional

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
