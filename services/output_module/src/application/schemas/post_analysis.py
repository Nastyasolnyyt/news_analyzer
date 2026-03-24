from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.application.schemas.topic import TopicDTO

class PostAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    topic_id: Optional[int] = None
    emotion: float
    tonality: float
    relevance: float
    sentiment_label: Optional[str] = None # Добавил из твоей БД

class PostAnalysisWithExternalModelsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    post_id: int
    topic: Optional[TopicDTO] = None
    emotion: float
    tonality: float
    relevance: float
    sentiment_label: Optional[str] = None # Заменяем category на то, что есть в БД
    # Если фронтенд ОЧЕНЬ хочет эти поля, задаем им дефолты, чтобы не было ошибки
    category: Optional[str] = "General" 
    risk_level: str = "low"