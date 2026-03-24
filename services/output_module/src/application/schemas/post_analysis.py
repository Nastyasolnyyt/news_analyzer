from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.application.schemas.topic import TopicDTO

class PostAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    topic_id: Optional[int] = None
    emotion: Optional[float] = 0.0
    tonality: Optional[float] = 0.0
    relevance: Optional[float] = 0.0
    sentiment_label: Optional[str] = None

class PostAnalysisWithExternalModelsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    post_id: int
    topic: Optional[TopicDTO] = None
    emotion: float = 0.0
    tonality: float = 0.0
    relevance: float = 0.0
    sentiment_label: Optional[str] = None
    
    # ИСПОЛЬЗУЕМ Field с default, чтобы Pydantic не искал это в объекте БД
    category: Optional[str] = Field(default="General")
    risk_level: Optional[str] = Field(default="low")