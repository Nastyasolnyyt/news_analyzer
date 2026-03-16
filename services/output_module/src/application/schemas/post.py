from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
# 1. Схема самой новости
class PostBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Добавлено
    
    id: int
    title: Optional[str]
    content: str
    source: str
    created_at: datetime
    author: Optional[str] = None

# 2. Схема аналитики
class PostAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tonality: float
    risk_level: Optional[str] = None
    # Теперь поле примет и "outlier" (str), и False (bool)
    is_anomaly: Optional[Union[str, bool]] = False

# 3. Схема сущности
class EntityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Добавлено
    
    id: int
    text: str
    type: Optional[str] = None
    details: Optional[dict] = None

# 4. Итоговый объект
class PostResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Современный стиль Pydantic V2
    
    post: PostBaseDTO
    analysis: PostAnalysisDTO
    entities: List[EntityDTO] = []

# 5. Схема для списка
class PostListResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    items: List[PostResponseDTO]
    total: int
    page: int
    page_size: int

# 6. Фильтры
class PostFilterDTO(BaseModel):
    search: Optional[str] = None
    entity_id: Optional[int] = None
    page: int = 1
    page_size: int = 20
    order: Optional[str] = "desc"
    sort: Optional[str] = "created_at"