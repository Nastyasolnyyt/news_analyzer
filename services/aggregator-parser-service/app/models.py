# aggregator-parser/app/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    id: Optional[int] = None 
    title: str
    text: Optional[str] = None # Это будет приходить из RSS
    link: str
    pub_date: Optional[datetime] = None
    source: str

    class Config:
        from_attributes = True # Для работы с ORM