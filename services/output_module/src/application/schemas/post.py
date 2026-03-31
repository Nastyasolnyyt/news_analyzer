# src/application/schemas/post.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# ✅ ПЛОСКАЯ структура для фронтенда (все поля на одном уровне)
class FlattenedPostDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    # Основная информация
    id: int
    title: Optional[str]
    text: str
    source: str
    link: Optional[str] = None
    pub_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Анализ тональности
    sentiment_label: Optional[str] = None
    tonality: Optional[float] = None
    confidence: Optional[float] = None
    emotion: Optional[float] = None
    relevance: Optional[float] = None
    
    # Риск (из risklevel-classifier и risk-classifier)
    risk_level: Optional[str] = None  # 'high' | 'medium' | 'low'
    risk_type: Optional[str] = None    # 'политический' | 'экономический' | 'социальный'
    risk_confidence: Optional[float] = None
    
    # Тема/кластер
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    
    # Сущности (NER)
    entities: List[dict] = []  # [{'id': 1, 'name': 'Газпром', 'entity_type': 'ORG'}]


# Фильтр для поиска (используется в репозитории)
class PostFilterDTO(BaseModel):
    page: int = 1
    page_size: int = 10
    search: Optional[str] = None
    order: str = "desc"  # asc или desc


# Ответ для списка постов
class PostListResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    items: List[FlattenedPostDTO]  # ✅ Теперь плоская структура
    total: int
    page: int
    page_size: int