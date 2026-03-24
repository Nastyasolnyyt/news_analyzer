from typing import Optional

from pydantic import BaseModel
from src.application.schemas.topic import TopicDTO


class PostAnalysisDTO(BaseModel):
    id: int
    post_id: int
    topic_id: Optional[int] = None
    emotion: float
    tonality: float
    relevance: float


class PostAnalysisWithExternalModelsDTO(BaseModel):
    id: Optional[int] = None
    post_id: int
    topic: Optional[TopicDTO] = None
    emotion: float
    tonality: float
    relevance: float
    category: Optional[str] = None
    risk_level: str = "low"
