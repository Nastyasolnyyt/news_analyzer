# services/risk-classifier/app/models.py
from pydantic import BaseModel
from typing import Optional

class RiskResult(BaseModel):
    risk_type: str  # Будет принимать значения 'high', 'medium', 'low'
    confidence: float