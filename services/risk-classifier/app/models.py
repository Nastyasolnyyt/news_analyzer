# risk-classifier/app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None  
    link: str
    pub_date: Optional[datetime] = None 
    source: str

class RiskResult(BaseModel):
    risk_type: str
    confidence: float