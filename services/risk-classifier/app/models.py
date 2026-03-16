# risk-classifier/app/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    id: Optional[int] = None
    title: str
    text: Optional[str] = None
    description: Optional[str] = None  
    link: str
    pub_date: Optional[datetime] = None 
    source: str

class RiskResult(BaseModel):
    # Используем Field для описания и валидатор, чтобы ограничить значения
    risk_type: str = Field(..., description="Уровень риска: high, medium или low")
    confidence: float = Field(..., ge=0, le=1.0)

    @validator('risk_type')
    def validate_risk_level(cls, v):
        # Приводим к нижнему регистру на случай, если нейронка ответит "High"
        v = v.lower().strip()
        allowed = ['high', 'medium', 'low']
        if v not in allowed:
            # Если нейронка выдала что-то странное, по умолчанию ставим low
            return 'low'
        return v