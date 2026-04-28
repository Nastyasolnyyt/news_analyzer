from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from src.application.schemas.post_analysis import PostAnalysisWithExternalModelsDTO
from src.application.schemas.topic import TopicDTO

# 1. Основная информация о новости
class PostBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: Optional[str]
    text: str  # В БД это колонка 'text'
    source: str
    link: Optional[str]
    pub_date: Optional[datetime]
    created_at: datetime

# 2. Сущность (NER)
class EntityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str  # Было text, стало name (как в БД)
    entity_type: Optional[str] = None  # Было type, стало entity_type (как в БД)

# 3. Итоговый объект, который летит на фронтенд
class PostResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    post: PostBaseDTO
    analysis: Optional[PostAnalysisWithExternalModelsDTO] = None
    entities: List[EntityDTO] = []

# 4. Схема для фильтрации (используется в репозитории)
class PostFilterDTO(BaseModel):
    page: int = 1
    page_size: int = 10
    search: Optional[str] = None
    order: str = "desc" # asc или desc
    risk_level: Optional[str] = None

# 5. DTO с внешними моделями (для service слоя)
class PostWithExternalModelsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    post: PostBaseDTO
    analysis: Optional[PostAnalysisWithExternalModelsDTO] = None
    entities: List[EntityDTO] = []

# 6. Список постов для ответа
class PostListResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    items: List[PostResponseDTO]
    total: int
    page: int
    page_size: int
