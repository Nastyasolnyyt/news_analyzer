# src/application/schemas/post_analysis.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.application.schemas.topic import TopicDTO

class PostAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    topic_id: Optional[int] = None
    emotion: Optional[float] = None
    tonality: Optional[float] = None
    relevance: Optional[float] = None
    sentiment_label: Optional[str] = None
    confidence: Optional[float] = None


class PostAnalysisWithExternalModelsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    post_id: int
    topic: Optional[TopicDTO] = None
    
   
    emotion: Optional[float] = None
    tonality: Optional[float] = None
    relevance: Optional[float] = None
    sentiment_label: Optional[str] = None
    confidence: Optional[float] = None
    
    
    # Дополнительные поля
    category: Optional[str] = Field(default="General")
    risk_level: Optional[str] = Field(default="low")
    risk_type: Optional[str] = Field(default=None)