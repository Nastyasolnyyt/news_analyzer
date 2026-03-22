from pydantic import BaseModel, Field, validator
from typing import Optional

class RiskResult(BaseModel):
    # Теперь здесь будут категории: политический, экономический, социальный
    risk_type: str = Field(..., description="Тип риска: политический, экономический или социальный")
    confidence: float = Field(..., ge=0, le=1.0)

    @validator('risk_type')
    def validate_risk_type(cls, v):
        v = v.lower().strip()
        allowed = ['политический', 'экономический', 'социальный', 'ошибка_нейросети', 'неопределенный']
        if v not in allowed:
            return 'неопределенный'
        return v