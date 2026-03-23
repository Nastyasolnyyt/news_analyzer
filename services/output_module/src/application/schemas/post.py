from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict

# 1. Основная информация о новости
class PostBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: Optional[str]
    content: str  # В БД это колонка 'text'
    source: str
    link: Optional[str]
    pub_date: Optional[datetime]
    created_at: datetime

# 2. Объединенная аналитика (Sentiment + Risk + Anomaly)
class PostAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tonality: float        # Из таблицы sentiments (confidence)
    risk_level: str        # Из таблицы risks (risk_type)
    is_anomaly: Union[bool, str] # Из таблицы anomalies (anomaly_type)

# 3. Сущность (NER)
class EntityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    text: str
    type: Optional[str] = None

# 4. Итоговый объект, который летит на фронтенд
class PostResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    post: PostBaseDTO
    analysis: PostAnalysisDTO
    entities: List[EntityDTO] = []

# 5. Схема для фильтрации (используется в репозитории)
class PostFilterDTO(BaseModel):
    page: int = 1
    page_size: int = 10
    search: Optional[str] = None
    order: str = "desc" # asc или desc

# 6. DTO с внешними моделями (для service слоя)
class PostWithExternalModelsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    post: PostBaseDTO
    analysis: Optional['PostAnalysisWithExternalModelsDTO'] = None
    entities: List[EntityDTO] = []

# 7. Список постов для ответа
class PostListResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    posts: List[PostResponseDTO]
    total: int
    page: int
    page_size: int
