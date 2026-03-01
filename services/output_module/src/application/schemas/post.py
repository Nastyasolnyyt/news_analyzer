from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from src.application.schemas.named_entity import NamedEntityDTO
from src.application.schemas.post_analysis import PostAnalysisWithExternalModelsDTO


class PostDTO(BaseModel):
    id: int
    author: str
    title: str
    content: str
    source: str
    created_at: datetime


class PostWithExternalModelsDTO(BaseModel):
    post: PostDTO
    analysis: PostAnalysisWithExternalModelsDTO
    entities: List[NamedEntityDTO]


class PostFilterDTO(BaseModel):
    topic_id: Optional[int] = None
    emotion: Optional[float] = None
    tonality: Optional[float] = None
    relevance: Optional[float] = None
    entity_id: Optional[int] = None
    sort: Optional[str] = Field(
        None, description="Поле для сортировки (id, created_at, emotion, tonality, relevance)"
    )
    order: Optional[str] = Field("asc", description="Порядок сортировки: asc или desc")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PostListResponseDTO(BaseModel):
    items: List[PostWithExternalModelsDTO]
    total: int
    page: int
    page_size: int
