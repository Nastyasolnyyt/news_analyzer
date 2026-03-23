from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    """Модель входящего сообщения из агрегатора/препроцессинга"""
    id: int
    title: str
    text: Optional[str] = None
    link: str
    source: str
    pub_date: Optional[str] = None

class RiskResult(BaseModel):
    """Результат анализа нейросетью"""
    risk_type: str = Field(..., description="Тип риска: политический, экономический или социальный")
    confidence: float = Field(..., ge=0, le=1.0)

    @validator('risk_type')
    def validate_risk_type(cls, v):
        v = v.lower().strip()
        allowed = ['политический', 'экономический', 'социальный', 'ошибка_нейросети', 'неопределенный']
        return v if v in allowed else 'неопределенный'
